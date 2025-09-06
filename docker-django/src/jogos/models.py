from django.db import models

from django.db import models


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

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(periodo_atual__gte=0), name='jogo_periodo_atual_gte_0'),
            models.CheckConstraint(check=models.Q(periodo_anterior__gte=0), name='jogo_periodo_anterior_gte_0'),
            models.CheckConstraint(check=models.Q(periodo_anterior__lte=models.F('periodo_atual')), name='jogo_periodo_anterior_lte_atual'),
        ]

    def __str__(self):
        return f'{self.name} ({self.cod})'
