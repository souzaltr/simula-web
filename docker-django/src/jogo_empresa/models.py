from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from jogos.models import Jogo


class Empresa(models.Model):
   nome = models.CharField(max_length=80)
   jogo = models.ForeignKey(Jogo, on_delete=models.CASCADE,editable=False, related_name="empresas") # Relação de empresa com um jogo
   criador = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False, on_delete=models.CASCADE, related_name='empresas_criadas')
                        
   def clean(self):
       if not self.nome.strip():
           raise ValidationError({"nome":"Nome não pode ser vazio ou somente espaços."})
        
       if Empresa.objects.filter(jogo=self.jogo, nome__iexact=self.nome).exclude(pk=self.pk).exists():
           raise ValidationError({"nome":"Este nome já está em uso neste jogo."}) 
       
       if self.pk:
            try:
                original = Jogo.objects.get(pk=self.pk)
            except Jogo.DoesNotExist:
                original = None
            if original and original.criador != self.criador:
                raise ValidationError({'criador': "O criador do jogo não pode ser alterado."})

   def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)        

   def __str__(self):
        return f"{self.nome} ({self.jogo.nome})" 
