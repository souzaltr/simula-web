from django.shortcuts import render
from django.views import View
from django.core.paginator import Paginator
from jogos.models import Jogo
from .models import SimulacaoPeriodo
from .forms import SimularForm
from .services import processar_lista, gerar_lote_id


class SimularView(View):
    template_name = "simulacao/simular.html"

    def get(self, request):
        form = SimularForm()
        jogos = Jogo.objects.filter(status=getattr(Jogo, 'ATIVO', 'A')).order_by("name")
        return render(request, self.template_name, {"form": form, "jogos": jogos})


class AplicarSimulacaoView(View):
    template_name = "simulacao/resultado.html"

    def post(self, request):
        form = SimularForm(request.POST)
        if not form.is_valid():
            jogos = Jogo.objects.filter(status=getattr(Jogo, 'ATIVO', 'A')).order_by("name")
            return render(request, "simulacao/simular.html", {"form": form, "jogos": jogos})

        jogos_ids = list(form.cleaned_data["jogos"].values_list("id", flat=True))
        acao = form.cleaned_data["acao"]
        lote = form.cleaned_data.get("request_id") or gerar_lote_id()

        res = processar_lista(
            jogos_ids=jogos_ids,
            acao=acao,
            user=request.user if getattr(request, "user", None) and request.user.is_authenticated else None,
            lote_id=lote,
        )

        resultados = res["resultados"]
        lote_id = res["lote_id"]

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

        return render(request, self.template_name, {"lote_id": lote_id, "linhas": linhas})


class HistoricoView(View):
    template_name = "simulacao/historico.html"

    def get(self, request):
        qs = SimulacaoPeriodo.objects.select_related("jogo", "execucao").order_by("-requested_at")
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
        jogos = Jogo.objects.order_by("name")

        return render(request, self.template_name, {
            "page_obj": page_obj,
            "jogos": jogos,
            "acao": acao,
            "jogo_sel": jogo_id,
            "lote": lote,
            "SimulacaoPeriodo": SimulacaoPeriodo,
        })
