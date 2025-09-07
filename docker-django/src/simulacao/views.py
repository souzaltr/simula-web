# simulacao/views.py
from django.shortcuts import render
from django.views import View
from django.core.paginator import Paginator

from jogos.models import Jogo
from .forms import SimularForm, FiltroJogosForm
from .services import processar_lista, gerar_lote_id
from .models import SimulacaoPeriodo


class SimulacaoView(View):
    template_name = "simulacao/simular.html"

    def _jogos_filtrados(self, request):
        """
        Retorna (filtro_form, jogos_filtrados, jogos_ativos_para_simular).
        - No GET: lê filtros do querystring.
        - No POST: usa os hidden fields 'status' e 'q' do SimularForm.
        - jogos_filtrados: para exibir no resumo (pode ter ativos/inativos).
        - jogos_ativos_para_simular: SEMPRE apenas ativos, para o campo 'jogos' do form.
        """
        if request.method == "GET":
            filtro_form = FiltroJogosForm(request.GET or None)
        else:
            data_fake_get = {
                "status": request.POST.get("status") or FiltroJogosForm.STATUS_ATIVOS,
                "q": request.POST.get("q") or "",
            }
            filtro_form = FiltroJogosForm(data_fake_get)

        base = Jogo.objects.all()
        if filtro_form.is_valid():
            jogos_filtrados = filtro_form.filtrar_queryset(base)
        else:
            jogos_filtrados = Jogo.objects.filter(status=getattr(Jogo, "ATIVO", "A")).order_by("nome")

        # Apenas jogos ATIVOS podem ser simulados
        ativo_val = getattr(Jogo, "ATIVO", "A")
        jogos_ativos_para_simular = jogos_filtrados.filter(status=ativo_val).order_by("nome")

        return filtro_form, jogos_filtrados, jogos_ativos_para_simular

    def get(self, request):
        filtro_form, jogos_filtrados, jogos_ativos = self._jogos_filtrados(request)
        form = SimularForm(
            jogos_qs=jogos_ativos,
            initial={
                "status": (filtro_form.cleaned_data.get("status")
                           if filtro_form.is_valid() else FiltroJogosForm.STATUS_ATIVOS),
                "q": (filtro_form.cleaned_data.get("q")
                      if filtro_form.is_valid() else ""),
            },
        )
        return render(request, self.template_name, {
            "form": form,
            "filtro_form": filtro_form,
            "jogos": jogos_filtrados,
        })

    def post(self, request):
        filtro_form, jogos_filtrados, jogos_ativos = self._jogos_filtrados(request)
        form = SimularForm(request.POST, jogos_qs=jogos_ativos)

        # Se o form for inválido (ex.: nenhum jogo), volta com erros
        if not form.is_valid():
            return render(request, self.template_name, {
                "form": form,
                "filtro_form": filtro_form,
                "jogos": jogos_filtrados,
            })

        # --- Guard extra: impedir processamento sem seleção
        jogos_sel_qs = form.cleaned_data.get("jogos")
        if not jogos_sel_qs or jogos_sel_qs.count() == 0:
            form.add_error("jogos", "Selecione ao menos um jogo.")
            return render(request, self.template_name, {
                "form": form,
                "filtro_form": filtro_form,
                "jogos": jogos_filtrados,
            })
        # ---------------------------------------------------

        # Por segurança, garanta que todos os IDs estão dentro do queryset de ATIVOS
        ids_post = set(jogos_sel_qs.values_list("id", flat=True))
        ids_ativos = set(jogos_ativos.values_list("id", flat=True))
        if not ids_post.issubset(ids_ativos):
            form.add_error("jogos", "A seleção contém itens inválidos (apenas jogos ATIVOS podem ser simulados).")
            return render(request, self.template_name, {
                "form": form,
                "filtro_form": filtro_form,
                "jogos": jogos_filtrados,
            })

        jogos_ids = list(ids_post)
        acao = form.cleaned_data["acao"]
        lote_id = form.cleaned_data.get("request_id") or gerar_lote_id()

        res = processar_lista(
            jogos_ids=jogos_ids,
            acao=acao,
            user=(request.user if getattr(request, "user", None) and request.user.is_authenticated else None),
            lote_id=lote_id,
        )

        resultados = res["resultados"]
        jogos_map = {j.id: j for j in Jogo.objects.filter(id__in=jogos_ids)}
        linhas = []
        for r in resultados:
            j = jogos_map.get(r["jogo_id"])
            linhas.append({
                "jogo": j,
                "acao": r["acao"],
                "ok": True,
                "mensagem": "",
                "periodo_final": r["periodo_depois"],
                "logs_count": r["logs_criados"],
            })

        # Recria o form “limpo” preservando os filtros atuais
        form = SimularForm(
            jogos_qs=jogos_ativos,
            initial={
                "status": (filtro_form.cleaned_data.get("status")
                           if filtro_form.is_valid() else FiltroJogosForm.STATUS_ATIVOS),
                "q": (filtro_form.cleaned_data.get("q")
                      if filtro_form.is_valid() else ""),
            },
        )

        contexto = {
            "form": form,
            "filtro_form": filtro_form,
            "jogos": jogos_filtrados,
            "lote_id": lote_id,
            "linhas": linhas,
        }
        return render(request, self.template_name, contexto)


class HistoricoView(View):
    template_name = "simulacao/historico.html"

    def get(self, request):
        qs = (
            SimulacaoPeriodo.objects
            .select_related("jogo", "execucao")
            .order_by("-requested_at")
        )

        acao = request.GET.get("acao") or ""
        jogo_id = request.GET.get("jogo") or ""
        lote = request.GET.get("lote") or ""

        if acao:
            qs = qs.filter(acao=acao)
        if jogo_id:
            qs = qs.filter(jogo_id=jogo_id)
        if lote:
            qs = qs.filter(execucao__lote_id=lote)

        paginator = Paginator(qs, 20)
        page_obj = paginator.get_page(request.GET.get("page"))

        jogos = Jogo.objects.order_by("nome")

        return render(request, self.template_name, {
            "page_obj": page_obj,
            "jogos": jogos,
            "acao": acao,
            "jogo_sel": jogo_id,
            "lote": lote,
            "SimulacaoPeriodo": SimulacaoPeriodo,
        })
