from django.test import TestCase
from django.urls import reverse
from jogo_empresa.models import Empresa
from jogos.models import Jogo
from cenarios.models import Cenario, Produto 

class EmpresasCrudTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Produto e Cenário mínimos para criar um Jogo válido
        cls.produto = Produto.objects.create(nome="Produto 1")

        cls.cenario = Cenario.objects.create(nome="Cenário 1", produto=cls.produto)
        cls.jogo = Jogo.objects.create(nome="Jogo 1", cenario=cls.cenario)

        # NOME CORRETO DA ROTA:
        cls.url = reverse("jogo_empresa:empresas_crud", args=[cls.jogo.id])

    def test_listar_empresas(self):
        Empresa.objects.create(nome="Empresa1", jogo=self.jogo)
        Empresa.objects.create(nome="Empresa2", jogo=self.jogo)

        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("empresas", resp.context)
        self.assertEqual(resp.context["empresas"].count(), 2)

    def test_abrir_form_edicao_via_get(self):
        e = Empresa.objects.create(nome="Editar Aqui", jogo=self.jogo)
        resp = self.client.get(self.url, {"edit": e.id})  # chave correta: "edit"
        self.assertEqual(resp.status_code, 200)
        self.assertIn("empresa_edit", resp.context)
        self.assertEqual(resp.context["empresa_edit"].id, e.id)

    def test_criar_empresa(self):
        resp = self.client.post(self.url, {
            "action": "create",
            "nome": "Nova Empresa",
        })
        self.assertEqual(resp.status_code, 302)  # redirect
        self.assertTrue(Empresa.objects.filter(nome="Nova Empresa", jogo=self.jogo).exists())

    def test_editar_empresa(self):
        e = Empresa.objects.create(nome="Old", jogo=self.jogo)  # campo correto: jogo=
        resp = self.client.post(self.url, {
            "action": "update",
            "id": e.id,
            "nome": "New",
        })
        self.assertEqual(resp.status_code, 302)
        e.refresh_from_db()
        self.assertEqual(e.nome, "New")

    def test_excluir_empresa(self):
        e = Empresa.objects.create(nome="Apagar", jogo=self.jogo)
        resp = self.client.post(self.url, {
            "action": "delete",
            "id": e.id,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Empresa.objects.filter(id=e.id).exists())



   