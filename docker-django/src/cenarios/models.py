from django.db import models

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
    fornecedor = models.CharField(max_length=100)
    forma_pagamento = models.CharField(max_length=25, choices=FormasPagamento)
    quantidade = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.nome} - Fornecedor {self.fornecedor}"
    

class Produto(models.Model):
    nome = models.CharField(max_length=100)
    insumos = models.ManyToManyField(Insumo, related_name="produtos") #relação entre produtos e insumos

    def __str__(self):
        return f"{self.nome} Insumos: {self.insumos}"


class Cenario(models.Model):
    nome = models.CharField(max_length=100)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name="cenarios")

    def __str__(self):
        return f"{self.nome} Com o Produto: {self.produto}"