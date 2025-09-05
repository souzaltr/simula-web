from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import random

class Jogo(models.Model):
    nome = models.CharField(max_length=80)
    status = models.BooleanField(default=True) # Ativo == True Inativo == False
    codigo = models.CharField(max_length=9, unique=True, editable=False)
    cenario = models.CharField(max_length=80,blank=True) # Por enquanto isso, ver como será feita essa ligação/integração com Model e contexto do caso de uso de Cenário
    periodo_atual = models.PositiveIntegerField(default=1)

    def gerar_codigo(self):
        while True:
            codigo = str(random.randint(100000000,999999999))
            if not Jogo.objects.filter(codigo=codigo).exists():
                return codigo
    def clean(self):
        if not self.nome.strip():
           raise ValidationError({"nome":"Nome não pode ser vazio ou somente espaços."}) 

    @property
    def num_jogador(self):
        return self.usuarios.count()

    def save(self, *args, **kwargs):
        if not self.codigo:  # Gera o código apenas na criação de um novo jogo
            self.codigo = self.gerar_codigo()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nome} ({self.codigo}) - Status: {self.status}"


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
   

class Usuario(AbstractUser):
    # Remoção do username padrão para podermos usar email como login
    username = None
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    jogo = models.ForeignKey(Jogo, on_delete=models.SET_NULL,null=True,blank=True,related_name='usuarios') # Relação do jogador participar de UM jogo
    empresa = models.OneToOneField(Empresa, on_delete=models.SET_NULL, null=True, blank=True, related_name='usuario') # Relação de um jogador com uma empresa

    # Define o campo de login para usar email (identificador unico)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome']  # campo obrigatório ao criar superusuario

    def clean(self):
        if not self.nome.strip():
            raise ValidationError({'nome': "Nome não pode ser vazio ou somente espaços."})
        
        # Se houver associação a uma empresa, ela deve pertencer ao mesmo jogo
        if self.empresa and self.jogo and self.empresa.jogo != self.jogo:
            raise ValidationError({'empresa': "A empresa deve pertencer ao mesmo jogo do usuário."})

    def __str__(self):
        if self.empresa:
            return f"{self.nome} ({self.empresa.nome})"
        return self.nome

class DemoModel(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField()
    image = models.ImageField(upload_to="demo_images")

    def __str__(self):
        return self.title
