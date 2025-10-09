from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings

# Create your models here.

#fazer as validações
class Insumo(models.Model):

    FormasPagamento = [
        ("avista","À Vista"),
        ("x1","1 parcela sem entrada"),
        ("x2","2 parcelas sem entrada"),
        ("entrada+1","Entrada +1 parcela"),
        ("entrada+2","Entrada +2 parcelas"),      
    ]

    nome = models.CharField(max_length=100)
    fornecedor = models.CharField(max_length=100,)
    forma_pagamento = models.CharField(max_length=25, choices=FormasPagamento, null=True,blank=True,default="avista")
    quantidade = models.PositiveIntegerField(null=True,blank=True,default=0)
    #fk de um mediador criador
    criador = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False, on_delete=models.CASCADE, related_name='insumos_criados')

    def __str__(self):
        return f"{self.nome} - Fornecedor -> {self.fornecedor}"
    
    def clean(self):
        if not self.nome.strip():
            raise ValidationError({"nome": "Nome do insumo não pode ser vazio ou somente espaços!"})
        
        if self.nome.strip().isdigit():
            raise ValidationError({"nome": "Nome do Insumo não pode ser apenas números!"})
        
        if not self.fornecedor.strip():
            raise ValidationError({"fornecedor":"Nome do Fornecedor não pode ser vazio ou somente espaços!"})
        
        if self.fornecedor.strip().isdigit():
            raise ValidationError({"fornecedor":"Nome do Fornecedor não pode ser apenas números!"})
        
        if self.quantidade < 0:
            raise ValidationError("A quantidade de insumos não pode ser negativa!")
       
        if self.pk:
            try:
                original = Insumo.objects.get(pk=self.pk)
            except Insumo.DoesNotExist:
                original = None
            if original and original.criador != self.criador:
                raise ValidationError({'criador': 'O criador do insumo não pode ser alterado.'})
 
        
class Produto(models.Model):
    nome = models.CharField(max_length=100)
    insumos = models.ManyToManyField(Insumo, related_name="produtos") #relação entre produtos e insumos
    criador = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False, on_delete=models.CASCADE, related_name='produtos_criados')

    def __str__(self):
        insumos_nomes = [i.nome for i in self.insumos.all()]
        return f"{self.nome} {insumos_nomes}"
    
    def clean(self):
        if not self.nome.strip():
            raise ValidationError({"nome" : "O nome do Produto não pode ser vazio ou apenas espaços!"})
        
        if self.nome.strip().isdigit():
            raise ValidationError({"nome": "O nome do produto não pode conter apenas números!"})
        
        if self.pk:
            try:
                original = Produto.objects.get(pk=self.pk)
            except Produto.DoesNotExist:
                original = None
            if original and original.criador != self.criador:
                raise ValidationError({'criador': 'O criador do produto não pode ser alterado.'})
        


class Cenario(models.Model):
    nome = models.CharField(max_length=100)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name="cenarios",blank=False,null=False)
    criador = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False, on_delete=models.CASCADE, related_name='cenarios_criados')

    def __str__(self):
        return f"{self.nome} Com o Produto: {self.produto}"
    
    def clean(self):
        if not self.nome.strip():
            raise ValidationError({"nome":"O nome do Cenário não pode ser vazio ou apenas espaços!"})
        
        if self.nome.strip().isdigit():
            raise ValidationError({"nome": "O nome do Cenário não pode conter apenas números!"})
        
        if self.pk:
            try:
                original = Cenario.objects.get(pk=self.pk)
            except Cenario.DoesNotExist:
                original = None
            if original and original.criador != self.criador:
                raise ValidationError({'criador': 'O criador do cenário não pode ser alterado.'})

    