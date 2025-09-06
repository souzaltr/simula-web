from django.contrib import admin
from .models import SimulacaoExecucao, SimulacaoPeriodo

@admin.register(SimulacaoExecucao)
class ExecucaoAdmin(admin.ModelAdmin):
    list_display = ('requested_at', 'jogo', 'acao', 'lote_id', 'requested_by')
    list_filter = ('acao', 'requested_at')
    search_fields = ('jogo__name', 'jogo__cod', 'lote_id')

@admin.register(SimulacaoPeriodo)
class PeriodoAdmin(admin.ModelAdmin):
    list_display = ('requested_at', 'jogo', 'acao', 'periodo_de', 'periodo_para', 'lote', 'step_index')
    list_filter = ('acao', 'requested_at')
    search_fields = ('jogo__name', 'jogo__cod', 'execucao__lote_id')

    def lote(self, obj):
        return obj.execucao.lote_id
