from django.db import models
from django.core.exceptions import ValidationError
import random

class Jogo(models.Model):
    ATIVO, INATIVO = 'A', 'I'
    STATUS_CHOICES = ((ATIVO, 'Ativo'), (INATIVO, 'Inativo'))

    nome = models.CharField(max_length=120, blank=False)
    cod = models.CharField(max_length=40, unique=True,editable=False)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=ATIVO)
    cenario = models.ForeignKey('cenarios.Cenario', editable=False, on_delete=models.CASCADE, related_name='jogos')
    periodo_anterior = models.PositiveIntegerField(default=0)
    periodo_atual = models.PositiveIntegerField(default=0)
    status_decisoes_disponiveis = models.BooleanField(default=False)

    def gerar_codigo(self):
        while True:
            codigo = str(random.randint(100000000, 999999999))  # 9 dígitos
            if not Jogo.objects.filter(cod=codigo).exists():
                return codigo

    def clean(self):
        if not (self.nome or '').strip():
            raise ValidationError({"nome": "Nome não pode ser vazio ou somente espaços."})
        
        if not self.cenario_id:
            raise ValidationError({"cenario": "Selecione um cenário para criar o jogo."})

    @property
    def num_jogador(self):
        return self.usuarios.count() if hasattr(self, 'usuarios') else 0

    def save(self, *args, **kwargs):  
        if not self.cod or not self.cod.strip():
            self.cod = self.gerar_codigo()
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(periodo_atual__gte=0), name='jogo_periodo_atual_gte_0'),
            models.CheckConstraint(check=models.Q(periodo_anterior__gte=0), name='jogo_periodo_anterior_gte_0'),
            models.CheckConstraint(check=models.Q(periodo_anterior__lte=models.F('periodo_atual')), name='jogo_periodo_anterior_lte_atual'),
        ]

    def __str__(self):
        return f'{self.nome} ({self.cod})'