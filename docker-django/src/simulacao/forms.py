from django import forms
from jogos.models import Jogo
from .models import SimulacaoPeriodo


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

    jogos = forms.ModelMultipleChoiceField(
    label="Selecione os jogos",
    queryset=Jogo.objects.none(),
    widget=forms.CheckboxSelectMultiple
)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["jogos"].queryset = (
            Jogo.objects.filter(status=getattr(Jogo, "ATIVO", "A")).order_by("nome")
        )
