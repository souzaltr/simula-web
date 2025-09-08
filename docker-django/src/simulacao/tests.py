from django.test import TestCase
from django.urls import reverse

from jogos.models import Jogo
from cenarios.models import Insumo, Produto, Cenario
from simulacao.models import SimulacaoPeriodo, SimulacaoExecucao


def ativo_value():
    return getattr(Jogo, "ATIVO", "A")


def inativo_value():
    val = getattr(Jogo, "ATIVO", "A")
    return "I" if val != "I" else "X"


def bootstrap_cenario(nome_cenario="Cenário Teste"):
    """
    Cria a cadeia mínima válida para Cenário:
    - 1 Insumo
    - 1 Produto (com o insumo)
    - 1 Cenário (com o produto)
    """
    insumo = Insumo.objects.create(nome="Insumo Base", fornecedor="Fornecedor X")
    produto = Produto.objects.create(nome="Produto Teste")
    produto.insumos.set([insumo])
    return Cenario.objects.create(nome=nome_cenario, produto=produto)


class SimulacaoViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Garante um Cenário válido para os jogos
        cls.cen = bootstrap_cenario("Cenário Teste")

        cls.j_ativo = Jogo.objects.create(
            nome="Jogo Ativo",
            cod="JATV",
            status=ativo_value(),
            periodo_atual=0,
            status_decisoes_disponiveis=False,
            cenario=cls.cen,
        )
        cls.j_inativo = Jogo.objects.create(
            nome="Jogo Inativo",
            cod="JINV",
            status=inativo_value(),
            periodo_atual=0,
            status_decisoes_disponiveis=False,
            cenario=cls.cen,
        )

    def test_get_simular_default_mostra_apenas_ativos_no_form(self):
        url = reverse("simulacao:simular")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

        form = resp.context["form"]
        qs = form.fields["jogos"].queryset
        self.assertIn(self.j_ativo, list(qs))
        self.assertNotIn(self.j_inativo, list(qs))

    def test_post_simular_sem_nenhum_jogo_mostra_erro_e_nao_processa(self):
        url = reverse("simulacao:simular")
        get_resp = self.client.get(url)
        self.assertEqual(get_resp.status_code, 200)
        form = get_resp.context["form"]
        initial_status = form.initial.get("status", "")
        initial_q = form.initial.get("q", "")

        data = {
            "acao": SimulacaoPeriodo.SPA,
            "forcar_decisoes_automaticas": "",
            "request_id": "",
            "status": initial_status,
            "q": initial_q,
            # sem 'jogos'
        }
        post_resp = self.client.post(url, data)
        self.assertEqual(post_resp.status_code, 200)

        form_after = post_resp.context["form"]
        self.assertTrue(form_after.errors)
        self.assertIn("jogos", form_after.errors)

        self.assertEqual(SimulacaoExecucao.objects.count(), 0)
        self.assertEqual(SimulacaoPeriodo.objects.count(), 0)

    def test_post_simular_processa_apenas_os_selecionados_ativos(self):
        url = reverse("simulacao:simular")
        get_resp = self.client.get(url)
        self.assertEqual(get_resp.status_code, 200)

        form = get_resp.context["form"]
        initial_status = form.initial.get("status", "")
        initial_q = form.initial.get("q", "")

        data = {
            "acao": SimulacaoPeriodo.SPA,
            "forcar_decisoes_automaticas": "on",
            "request_id": "",
            "status": initial_status,
            "q": initial_q,
            "jogos": [str(self.j_ativo.id)],
        }
        post_resp = self.client.post(url, data, follow=True)
        self.assertEqual(post_resp.status_code, 200)

        self.assertIn("linhas", post_resp.context)
        linhas = post_resp.context["linhas"]
        self.assertEqual(len(linhas), 1)
        self.assertEqual(linhas[0]["jogo"].id, self.j_ativo.id)

        self.assertEqual(SimulacaoExecucao.objects.count(), 1)
        self.assertGreaterEqual(SimulacaoPeriodo.objects.count(), 1)

    def test_request_id_invalido_hex(self):
        url = reverse("simulacao:simular")
        get_resp = self.client.get(url)
        form = get_resp.context["form"]
        initial_status = form.initial.get("status", "")
        initial_q = form.initial.get("q", "")

        data = {
            "acao": SimulacaoPeriodo.SPA,
            "forcar_decisoes_automaticas": "",
            "request_id": "ZZZ_NOT_HEX_1234",
            "status": initial_status,
            "q": initial_q,
            "jogos": [str(self.j_ativo.id)],
        }
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.context["form"].errors)
        self.assertIn("ID do lote", str(resp.context["form"].errors))

    def test_request_id_hex_tamanho_errado(self):
        url = reverse("simulacao:simular")
        get_resp = self.client.get(url)
        form = get_resp.context["form"]
        initial_status = form.initial.get("status", "")
        initial_q = form.initial.get("q", "")

        data = {
            "acao": SimulacaoPeriodo.SPA,
            "forcar_decisoes_automaticas": "",
            "request_id": "abcd",
            "status": initial_status,
            "q": initial_q,
            "jogos": [str(self.j_ativo.id)],
        }
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.context["form"].errors)
        self.assertIn("ID do lote inválido", str(resp.context["form"].errors))


class HistoricoViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cen = bootstrap_cenario("Cenário H")

        cls.j1 = Jogo.objects.create(
            nome="Jogo H1", cod="H1", status=ativo_value(),
            periodo_atual=0, status_decisoes_disponiveis=False, cenario=cls.cen
        )
        cls.j2 = Jogo.objects.create(
            nome="Jogo H2", cod="H2", status=ativo_value(),
            periodo_atual=0, status_decisoes_disponiveis=False, cenario=cls.cen
        )

        e1 = SimulacaoExecucao.objects.create(
            jogo=cls.j1, acao=SimulacaoPeriodo.SPA, lote_id="aaaaaaaaaaaaaaaa"
        )
        e2 = SimulacaoExecucao.objects.create(
            jogo=cls.j2, acao=SimulacaoPeriodo.R0D, lote_id="bbbbbbbbbbbbbbbb"
        )

        SimulacaoPeriodo.objects.create(
            execucao=e1, jogo=cls.j1, acao=SimulacaoPeriodo.SPA,
            periodo_de=0, periodo_para=0, step_index=0
        )
        SimulacaoPeriodo.objects.create(
            execucao=e2, jogo=cls.j2, acao=SimulacaoPeriodo.R0D,
            periodo_de=0, periodo_para=1, step_index=0
        )

    def test_historico_sem_filtro_lista_tudo(self):
        url = reverse("simulacao:historico")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        page_obj = resp.context["page_obj"]
        self.assertEqual(page_obj.paginator.count, 2)

    def test_historico_filtra_por_acao(self):
        url = reverse("simulacao:historico")
        resp = self.client.get(url, {"acao": SimulacaoPeriodo.SPA})
        self.assertEqual(resp.status_code, 200)
        page_obj = resp.context["page_obj"]
        self.assertEqual(page_obj.paginator.count, 1)
        obj = page_obj.object_list[0]  # lista
        self.assertEqual(obj.acao, SimulacaoPeriodo.SPA)

    def test_historico_filtra_por_jogo(self):
        url = reverse("simulacao:historico")
        resp = self.client.get(url, {"jogo": str(self.j2.id)})
        self.assertEqual(resp.status_code, 200)
        page_obj = resp.context["page_obj"]
        self.assertEqual(page_obj.paginator.count, 1)
        self.assertEqual(page_obj.object_list[0].jogo_id, self.j2.id)

    def test_historico_filtra_por_lote(self):
        url = reverse("simulacao:historico")
        resp = self.client.get(url, {"lote": "aaaaaaaaaaaaaaaa"})
        self.assertEqual(resp.status_code, 200)
        page_obj = resp.context["page_obj"]
        self.assertEqual(page_obj.paginator.count, 1)
        self.assertEqual(page_obj.object_list[0].execucao.lote_id, "aaaaaaaaaaaaaaaa")