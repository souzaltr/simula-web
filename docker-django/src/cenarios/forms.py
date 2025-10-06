from django import forms
from .models import Insumo,Produto,Cenario

class InsumoForm(forms.ModelForm):
    class Meta:
        model = Insumo
        fields=[
            'nome',
            'fornecedor'
        ]

        error_messages = {
            'nome': {
                'required': "Informe o nome do Insumo!",
         },
         'fornecedor':{
             'required' : "Informe o nome do Fornecedor!"
         }
        }

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

        error_messages = {
            'nome': {
                'required': "Informe o nome do Produto!",
         },
         'insumos' :{
             'required' : "É necessário selecionar ao menos um insumo!"
         } 
        }

    def __init__(self, *args, **kwargs):
        
        usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)
        
        if usuario:
            
            self.fields['insumos'].queryset = Insumo.objects.filter(criador=usuario)
        
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
        
        error_messages = {
            'nome':{
                'required': "Informe o nome do Cenário!",
            },
            'produto':{
                'required': "É necessário ter um produto para criar um Cenário",
            }
        }

    def __init__(self, *args, **kwargs):
        
        usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)
        
        if usuario:
            
            self.fields['produto'].queryset = Produto.objects.filter(criador=usuario)
