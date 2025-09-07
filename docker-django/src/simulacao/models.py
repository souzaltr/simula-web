from django.db import models
from django.conf import settings  # pode continuar, mesmo sem usar, se já estiver aí
from jogos.models import Jogo


class SimulacaoPeriodo(models.Model):
    R0D = 'R0D'
    RND = 'RND'
    SPA = 'SPA'
    SPN = 'SPN'
    RDA = 'RDA'
    LPD = 'LPD'
    CAD = 'CAD'

    ACAO_CHOICES = (
        (R0D, 'Reprocessar 0→atual'),
        (RND, 'Reprocessar 0→atual e liberar próximo'),
        (SPA, 'Simular período atual'),
        (SPN, 'Simular período atual e liberar próximo'),
        (RDA, 'Reprocessar período passado'),
        (LPD, 'Liberar próximo período de decisões'),
        (CAD, 'Cancelar simulação do último período'),
    )

    execucao = models.ForeignKey('SimulacaoExecucao', on_delete=models.CASCADE, related_name='periodos')
    jogo = models.ForeignKey(Jogo, on_delete=models.CASCADE, related_name='periodos')
    acao = models.CharField(max_length=3, choices=ACAO_CHOICES)

    periodo_de = models.PositiveIntegerField()
    periodo_para = models.PositiveIntegerField()

    step_index = models.PositiveIntegerField(default=0)
    requested_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('execucao', 'step_index'),)
        indexes = [
            models.Index(fields=['jogo', 'requested_at']),
            models.Index(fields=['acao', 'requested_at']),
        ]
        ordering = ('requested_at',)

    def __str__(self):
        return f'{self.jogo.cod} {self.acao} {self.periodo_de}->{self.periodo_para} (step {self.step_index})'

class SimulacaoExecucao(models.Model):
    jogo = models.ForeignKey(Jogo, on_delete=models.CASCADE, related_name='execucoes')
    acao = models.CharField(max_length=3, choices=SimulacaoPeriodo.ACAO_CHOICES)
    lote_id = models.CharField(max_length=64)
    requested_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('jogo', 'lote_id'),)
        indexes = [
            models.Index(fields=['jogo', 'requested_at']),
            models.Index(fields=['acao', 'requested_at']),
        ]
        ordering = ('-requested_at',)

    def __str__(self):
        return f'Execução {self.acao} [{self.lote_id}] - {self.jogo.cod}'
