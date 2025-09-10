from django import forms
from django.db.models import Q
from jogos.models import Jogo
from .models import SimulacaoPeriodo


class FiltroJogosForm(forms.Form):
    STATUS_TODOS = "todos"
    STATUS_ATIVOS = "ativos"
    STATUS_INATIVOS = "inativos"

    status = forms.ChoiceField(
        label="Status",
        required=False,
        choices=[
            (STATUS_ATIVOS, "Ativos"),
            (STATUS_INATIVOS, "Inativos"),
            (STATUS_TODOS, "Todos"),
        ],
        initial=STATUS_ATIVOS,
        widget=forms.Select(attrs={"class": "form-select"})
    )
    q = forms.CharField(
        label="Buscar",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Nome ou código"})
    )

    def filtrar_queryset(self, qs):
        """Aplica os filtros (status + busca) sobre o queryset de Jogo."""
        status = self.cleaned_data.get("status") or self.STATUS_ATIVOS
        q = (self.cleaned_data.get("q") or "").strip()

        ativo_val = getattr(Jogo, "ATIVO", "A")
        if status == self.STATUS_ATIVOS:
            qs = qs.filter(status=ativo_val)
        elif status == self.STATUS_INATIVOS:
            qs = qs.exclude(status=ativo_val)

        if q:
            qs = qs.filter(Q(nome__icontains=q) | Q(cod__icontains=q))

        return qs.order_by("nome")


class SimularForm(forms.Form):
    acao = forms.ChoiceField(
        label="Ação",
        choices=SimulacaoPeriodo.ACAO_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"})
    )
    forcar_decisoes_automaticas = forms.BooleanField(
        label="Forçar decisões automáticas",
        required=False
    )

    # Se vier vazio, a view gera um novo; se vier preenchido, validamos.
    request_id = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )

    # Persistem os filtros atuais no POST
    status = forms.CharField(widget=forms.HiddenInput(), required=False)
    q = forms.CharField(widget=forms.HiddenInput(), required=False)

    # Seleção múltipla
    jogos = forms.ModelMultipleChoiceField(
        label="Selecione os jogos",
        queryset=Jogo.objects.none(),
        required=True,
        widget=forms.CheckboxSelectMultiple()  # precisa ser instanciado
    )

    def __init__(self, *args, **kwargs):
    
        jogos_qs = kwargs.pop("jogos_qs", None)
        super().__init__(*args, **kwargs)

        if jogos_qs is None:
            jogos_qs = Jogo.objects.filter(
                status=getattr(Jogo, "ATIVO", "A")
            ).order_by("nome")

        self.fields["jogos"].queryset = jogos_qs

    def clean_request_id(self):
        """
        Se informado, o request_id deve ter 16 caracteres hexadecimais.
        (Ele vira o lote_id na SimulacaoExecucao.)
        """
        val = (self.cleaned_data.get("request_id") or "").strip()
        if not val:
            return ""

        if len(val) != 16:
            raise forms.ValidationError("ID do lote inválido: use exatamente 16 caracteres hexadecimais.")

        try:
            int(val, 16)
        except ValueError:
            raise forms.ValidationError("ID do lote inválido: use apenas caracteres hexadecimais (0-9, a-f).")

        return val.lower()

    def clean_jogos(self):
        """Garante seleção e que todos os jogos sejam ATIVOS."""
        selecionados = self.cleaned_data.get("jogos")

        if not selecionados or selecionados.count() == 0:
            raise forms.ValidationError("Selecione ao menos um jogo.")

        ativo_code = getattr(Jogo, "ATIVO", "A")
        inativos = [j for j in selecionados if getattr(j, "status", None) != ativo_code]
        if inativos:
            nomes = ", ".join(j.nome for j in inativos[:3])
            if len(inativos) > 3:
                nomes += "…"
            raise forms.ValidationError(
                f"Apenas jogos ATIVOS podem ser simulados. Remova os inativos: {nomes}."
            )

        return selecionados

