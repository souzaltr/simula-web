from django.db import models
from django.core.exceptions import ValidationError

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
 
        
class Produto(models.Model):
    nome = models.CharField(max_length=100)
    insumos = models.ManyToManyField(Insumo, related_name="produtos") #relação entre produtos e insumos

    def __str__(self):
        insumos_nomes = [i.nome for i in self.insumos.all()]
        return f"{self.nome} {insumos_nomes}"
    
    def clean(self):
        if not self.nome.strip():
            raise ValidationError({"nome" : "O nome do Produto não pode ser vazio ou apenas espaços!"})
        if self.nome.strip().isdigit():
            raise ValidationError({"nome": "O nome do produto não pode conter apenas números!"})


class Cenario(models.Model):
    nome = models.CharField(max_length=100)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name="cenarios",blank=False,null=False)

    def __str__(self):
        return f"{self.nome} Com o Produto: {self.produto}"
    
    def clean(self):
        if not self.nome.strip():
            raise ValidationError({"nome":"O nome do Cenário não pode ser vazio ou apenas espaços!"})
        if self.nome.strip().isdigit():
            raise ValidationError({"nome": "O nome do Cenário não pode conter apenas números!"})

    