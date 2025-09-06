from django import forms
from jogos.models import Jogo
from .models import SimulacaoPeriodo

class SimularForm(forms.Form):
    jogos = forms.ModelMultipleChoiceField(
        queryset=Jogo.objects.none(),
        widget=forms.CheckboxSelectMultiple
    )
    acao = forms.ChoiceField(
        choices=SimulacaoPeriodo.ACAO_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"})
    )
    request_id = forms.CharField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["jogos"].queryset = Jogo.objects.filter(status=Jogo.ATIVO).order_by("name")

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get("jogos"):
            raise forms.ValidationError("Selecione ao menos um jogo.")
        if not cleaned.get("acao"):
            raise forms.ValidationError("Selecione uma ação.")
        return cleaned
