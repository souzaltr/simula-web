from django import forms
from .models import Insumo,Produto,Cenario



class InsumoForm(forms.ModelForm):
    class Meta:
        model = Insumo
        fields=[
            'nome',
            'fornecedor'
        ]

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields=[
            'nome', 
            'insumos',
        ]
        widgets = {
            'insumos': forms.CheckboxSelectMultiple(),
        }
        
class CenarioForm(forms.ModelForm):
    class Meta:
        model = Cenario
        fields=[
            'nome',
            'produto',
        ]
        widgets = {
            'produto': forms.Select(),
        }
    def __init__(self, *args, **kwargs): ## estudar essa linha
        super().__init__(*args, **kwargs)
        self.fields['produto'].empty_label = None