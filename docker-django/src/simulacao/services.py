import uuid
from django.db import transaction
from jogos.models import Jogo
from .models import SimulacaoExecucao, SimulacaoPeriodo

ACOES = {c for c, _ in SimulacaoPeriodo.ACAO_CHOICES}


def gerar_lote_id():
    return uuid.uuid4().hex[:16]
  
  
def _criar_execucao(jogo: Jogo, acao: str, lote_id: str, user):
    obj, created = SimulacaoExecucao.objects.get_or_create(
        jogo=jogo,
        lote_id=lote_id,
        defaults={"acao": acao},
    )
    if not created and obj.acao != acao:
        obj.acao = acao
        obj.save(update_fields=["acao"])
    return obj


def _proximo_step(execucao: SimulacaoExecucao):
    ultimo = (
        SimulacaoPeriodo.objects.filter(execucao=execucao)
        .order_by("-step_index")
        .first()
    )
    return 0 if not ultimo else ultimo.step_index + 1


def _criar_periodo(execucao, jogo, acao, periodo_de, periodo_para):
    """
    Cria um registro de SimulacaoPeriodo.
    Campos 'decisoes_de'/'decisoes_para' foram removidos do model conforme solicitado.
    """
    step = _proximo_step(execucao)
    return SimulacaoPeriodo.objects.create(
        execucao=execucao,
        jogo=jogo,
        acao=acao,
        periodo_de=periodo_de,
        periodo_para=periodo_para,
        step_index=step,
    )

  
def _acao_R0D(jogo, execucao):
    p = jogo.periodo_atual
    for k in range(0, p):
        _criar_periodo(execucao, jogo, SimulacaoPeriodo.R0D, k, k + 1)
    return {
        "logs": p,
        "periodo_final": jogo.periodo_atual,
        "decisoes": jogo.status_decisoes_disponiveis,
    }

  
def _acao_RND(jogo, execucao):
    p = jogo.periodo_atual
    for k in range(0, p + 1):
        _criar_periodo(execucao, jogo, SimulacaoPeriodo.RND, k, k + 1)
    jogo.periodo_atual = p + 1
    jogo.save(update_fields=["periodo_atual"])
    return {
        "logs": p + 1,
        "periodo_final": jogo.periodo_atual,
        "decisoes": jogo.status_decisoes_disponiveis,
    }

  
def _acao_SPA(jogo, execucao):
    p = jogo.periodo_atual
    _criar_periodo(execucao, jogo, SimulacaoPeriodo.SPA, p, p)
    return {
        "logs": 1,
        "periodo_final": jogo.periodo_atual,
        "decisoes": jogo.status_decisoes_disponiveis,
    }

  
def _acao_SPN(jogo, execucao):
    p = jogo.periodo_atual
    _criar_periodo(execucao, jogo, SimulacaoPeriodo.SPN, p, p + 1)
    jogo.periodo_atual = p + 1
    jogo.save(update_fields=["periodo_atual"])
    return {
        "logs": 1,
        "periodo_final": jogo.periodo_atual,
        "decisoes": jogo.status_decisoes_disponiveis,
    }


def _acao_RDA(jogo, execucao):
    p = jogo.periodo_atual
    _criar_periodo(execucao, jogo, SimulacaoPeriodo.RDA, max(0, p - 1), p)
    return {
        "logs": 1,
        "periodo_final": jogo.periodo_atual,
        "decisoes": jogo.status_decisoes_disponiveis,
    }


def _acao_LPD(jogo, execucao):
    _criar_periodo(execucao, jogo, SimulacaoPeriodo.LPD, jogo.periodo_atual, jogo.periodo_atual)
    if not jogo.status_decisoes_disponiveis:
        jogo.status_decisoes_disponiveis = True
        jogo.save(update_fields=["status_decisoes_disponiveis"])
    return {
        "logs": 1,
        "periodo_final": jogo.periodo_atual,
        "decisoes": jogo.status_decisoes_disponiveis,
    }

  
def _acao_CAD(jogo, execucao):
    p = jogo.periodo_atual
    novo = max(0, p - 1)
    _criar_periodo(execucao, jogo, SimulacaoPeriodo.CAD, p, novo)
    if p != novo:
        jogo.periodo_atual = novo
        jogo.save(update_fields=["periodo_atual"])
    return {
        "logs": 1,
        "periodo_final": jogo.periodo_atual,
        "decisoes": jogo.status_decisoes_disponiveis,
    }

def _acao_RSD(jogo, execucao):
    p = jogo.periodo_atual

    for k in range(0, p):
        _criar_periodo(execucao, jogo, SimulacaoPeriodo.R0D, k, k + 1)

    _criar_periodo(execucao, jogo, SimulacaoPeriodo.SPN, p, p + 1)
    jogo.periodo_atual = p + 1
    jogo.save(update_fields=["periodo_atual"])

    _criar_periodo(execucao, jogo, SimulacaoPeriodo.LPD, jogo.periodo_atual, jogo.periodo_atual)
    if not jogo.status_decisoes_disponiveis:
        jogo.status_decisoes_disponiveis = True
        jogo.save(update_fields=["status_decisoes_disponiveis"])

    total_logs = p + 2
    return {
        "logs": total_logs,
        "periodo_final": jogo.periodo_atual,
        "decisoes": jogo.status_decisoes_disponiveis,
    }
  
_FUNCS = {
    SimulacaoPeriodo.R0D: _acao_R0D,
    SimulacaoPeriodo.RND: _acao_RND,
    SimulacaoPeriodo.SPA: _acao_SPA,
    SimulacaoPeriodo.SPN: _acao_SPN,
    SimulacaoPeriodo.RDA: _acao_RDA,
    SimulacaoPeriodo.LPD: _acao_LPD,
    SimulacaoPeriodo.CAD: _acao_CAD,
    SimulacaoPeriodo.RSD: _acao_RSD,
}

@transaction.atomic
def processar_lista(jogos_ids, acao, user=None, lote_id=None):
    if acao not in ACOES:
        raise ValueError("acao invalida")

    lote = lote_id or gerar_lote_id()
    resultados = []

    jogos = (
        Jogo.objects.filter(id__in=jogos_ids)
        .select_related("cenario")
        .order_by("id")
    )

    for jogo in jogos:
        execucao = _criar_execucao(jogo, acao, lote, user)

        antes_p = jogo.periodo_atual
        antes_dec = jogo.status_decisoes_disponiveis

        info = _FUNCS[acao](jogo, execucao)

        resultados.append(
            {
                "jogo_id": jogo.id,
                "cod": jogo.cod,
                "nome": jogo.nome,
                "acao": acao,
                "lote_id": lote,
                "periodo_antes": antes_p,
                "periodo_depois": info["periodo_final"],
                "decisoes_antes": antes_dec,
                "decisoes_depois": info["decisoes"],
                "logs_criados": info["logs"],
            }
        )

    return {"lote_id": lote, "resultados": resultados}


