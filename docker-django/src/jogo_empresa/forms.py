from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .models import Jogo, Empresa

class JogoForm(forms.ModelForm):
    class Meta:
        model = Jogo
        fields = ['nome', 'cenario', 'status', 'periodo_atual']

class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ['nome'] 


