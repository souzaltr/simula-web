from django.db import models
from django.contrib.auth.models import AbstractUser
import random

class Jogo(models.Model):
    nome = models.CharField(max_length=80)
    status = models.BooleanField(default=True) # Ativo == True Inativo == False
    codigo = models.CharField(max_length=9, unique=True, editable=False)
    cenario = models.CharField(max_length=80,blank=True) # Por enquanto isso, ver como será feita essa ligação/integração com Model e contexto do caso de uso de Cenário
    num_jogador = models.PositiveIntegerField(default=0)
    periodo_atual = models.PositiveIntegerField(default=1)

    def gerar_codigo(self):
        while True:
            codigo = str(random.randint(100000000,999999999))
            if not Jogo.objects.filter(codigo=codigo).exists():
                return codigo

    def __str__(self):
        return f"{self.nome} ({self.codigo}) - Status: {self.status}"


class Empresa(models.Model):
   nome = models.CharField(max_length=80)
   jogo = models.ForeignKey(Jogo, on_delete=models.CASCADE, related_name="empresas") # Relação de empresa com um jogo
   def __str__(self):
        return f"{self.nome} ({self.jogo.nome})" 
   

class Usuario(AbstractUser):
    # Remoção do username padrão para podermos usar email como login
    username = None
    first_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    empresa = models.OneToOneField(Empresa, on_delete=models.CASCADE, related_name='usuarios') # Relação de um jogador com uma empresa

    # Define o campo de login para usar email (identificador unico)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name']  # campo obrigatório ao criar superusuario

    def __str__(self):
        return f"{self.first_name} ({self.empresa.nome})"



class DemoModel(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField()
    image = models.ImageField(upload_to="demo_images")

    def __str__(self):
        return self.title
