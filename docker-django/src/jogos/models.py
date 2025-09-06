from django.db import models
from django.core.exceptions import ValidationError
from django.db import models
import random

class Jogo(models.Model):
    ATIVO, INATIVO = 'A', 'I'
    STATUS_CHOICES = ((ATIVO, 'Ativo'), (INATIVO, 'Inativo'))

    name = models.CharField(max_length=120)
    cod = models.CharField(max_length=40, unique=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=ATIVO)
    cenario = models.ForeignKey('cenarios.Cenario', on_delete=models.PROTECT, related_name='jogos')
    periodo_anterior = models.PositiveIntegerField(default=0)
    periodo_atual = models.PositiveIntegerField(default=0)
    status_decisoes_disponiveis = models.BooleanField(default=False)

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

    def save(self, args, **kwargs):
        if not self.cod:  # Gera o código apenas na criação de um novo jogo
            self.cod = self.gerar_codigo()
        super().save(args, **kwargs)

    def str(self):
        return f"{self.nome} ({self.cod}) - Status: {self.status}"

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(periodo_atual__gte=0), name='jogo_periodo_atual_gte_0'),
            models.CheckConstraint(check=models.Q(periodo_anterior__gte=0), name='jogo_periodo_anterior_gte_0'),
            models.CheckConstraint(check=models.Q(periodo_anterior__lte=models.F('periodo_atual')), name='jogo_periodo_anterior_lte_atual'),
        ]

    def __str__(self):
        return f'{self.name} ({self.cod})'
