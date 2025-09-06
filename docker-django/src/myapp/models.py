from django.db import models
from django.core.exceptions import ValidationError
import random

from jogos.models import Jogo

class Empresa(models.Model):
   nome = models.CharField(max_length=80)
   jogo = models.ForeignKey(Jogo, on_delete=models.CASCADE, related_name="empresas") # Relação de empresa com um jogo
   
   def clean(self):
       if not self.nome.strip():
           raise ValidationError({"nome":"Nome não pode ser vazio ou somente espaços."})
        
       if Empresa.objects.filter(jogo=self.jogo, nome__iexact=self.nome).exclude(pk=self.pk).exists():
           raise ValidationError({"nome":"Este nome já está em uso neste jogo."}) 

   def __str__(self):
        return f"{self.nome} ({self.jogo.nome})" 
