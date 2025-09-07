# simulacao/forms.py
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
    request_id = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )
    # Esses dois campos só servem para “persistir” os filtros atuais no POST
    status = forms.CharField(widget=forms.HiddenInput(), required=False)
    q = forms.CharField(widget=forms.HiddenInput(), required=False)

    # O campo de seleção múltipla de jogos (como checkboxes)
    jogos = forms.ModelMultipleChoiceField(
        label="Selecione os jogos",
        queryset=Jogo.objects.none(),
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        # Permite chegar um queryset filtrado de jogos pelo view
        jogos_qs = kwargs.pop("jogos_qs", None)
        super().__init__(*args, **kwargs)
        if jogos_qs is not None:
            self.fields["jogos"].queryset = jogos_qs
        else:
            self.fields["jogos"].queryset = (
                Jogo.objects.filter(status=getattr(Jogo, "ATIVO", "A")).order_by("nome")
            )

    def clean(self):
        cleaned = super().clean()
        jogos = cleaned.get("jogos")
        if not jogos or jogos.count() == 0:
            self.add_error("jogos", "Selecione ao menos um jogo.")
        return cleaned
