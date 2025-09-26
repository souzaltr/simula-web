from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from jogo_empresa.models import Empresa
from jogos.models import Jogo
from cenarios.models import Cenario, Produto, Insumo 
from django.contrib.auth.models import Group

Usuario = get_user_model()

class EmpresasCrudTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Produto e Cenário mínimos para criar um Jogo válido
        cls.produto = Produto.objects.create(nome="Produto 1")
        cls.cenario = Cenario.objects.create(nome="Cenário 1", produto=cls.produto)

        cls.usuario = Usuario.objects.create_user(username="user1", email="user@test.com",cpf="155.078.190-17",password="447766ifg!")
        mediador_group, created = Group.objects.get_or_create(name="Mediador")
        cls.usuario.groups.add(mediador_group)
        cls.usuario.save()

        cls.jogo = Jogo.objects.create(nome="Jogo 1", cenario=cls.cenario, criador=cls.usuario)

        # NOME CORRETO DA ROTA:
        cls.url = reverse("jogo_empresa:empresas_crud", args=[cls.jogo.id])

    def setUp(self):
        self.client = Client()
        self.client.login(username="user@test.com", password="447766ifg!")

    def test_listar_empresas(self):
        Empresa.objects.create(nome="Empresa1", jogo=self.jogo, criador=self.usuario)
        Empresa.objects.create(nome="Empresa2", jogo=self.jogo, criador=self.usuario)

        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("empresas", resp.context)
        self.assertEqual(resp.context["empresas"].count(), 2)

    def test_abrir_form_edicao_via_get(self):
        e = Empresa.objects.create(nome="Editar Aqui", jogo=self.jogo, criador=self.usuario)
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
        e = Empresa.objects.create(nome="Old", jogo=self.jogo, criador=self.usuario )  # campo correto: jogo=
        resp = self.client.post(self.url, {
            "action": "update",
            "id": e.id,
            "nome": "New",
        })
        self.assertEqual(resp.status_code, 302)
        e.refresh_from_db()
        self.assertEqual(e.nome, "New")

    def test_excluir_empresa(self):
        e = Empresa.objects.create(nome="Apagar", jogo=self.jogo, criador=self.usuario)
        resp = self.client.post(self.url, {
            "action": "delete",
            "id": e.id,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Empresa.objects.filter(id=e.id).exists())

class EmpresaPermissaoTestCase(TestCase):
    def setUp(self):
        self.m1 = Usuario.objects.create_user(username="m1", email="m1@test.com",cpf="483.738.610-50", password="447766ifg!")
        self.m2 = Usuario.objects.create_user(username="m2", email="m2@test.com",cpf="167.842.470-60", password="123784ifg!")
        self.super = Usuario.objects.create_superuser(username="admin", email="admin@test.com",cpf="155.078.190-17", password="447788ifg!")

        mediador_group, _ = Group.objects.get_or_create(name="Mediador")
        self.m1.groups.add(mediador_group)
        self.m2.groups.add(mediador_group) 
        self.m1.save()
        self.m2.save()

        insumo=Insumo.objects.create(nome="Madeira", fornecedor="Bertazini",forma_pagamento="À Vista",quantidade=50)
        self.produto = Produto.objects.create(nome="ProdutoX")
        self.produto.insumos.set([insumo])
        self.cenario = Cenario.objects.create(nome="Cenário X", produto=self.produto)

        # Jogos de cada usuário
        self.jogo_m1 = Jogo.objects.create(nome="Jogo M1", cenario=self.cenario, criador=self.m1)
        self.jogo_m2 = Jogo.objects.create(nome="Jogo M2", cenario=self.cenario, criador=self.m2)

        # Empresa criada no jogo de M2
        self.empresa_m2 = Empresa.objects.create(nome="Empresa M2", jogo=self.jogo_m2, criador=self.m2)

        self.client = Client()

    def test_mediador_nao_pode_ver_empresas_de_outro_jogo(self):
        self.client.login(username="m1@test.com", password="447766ifg!")
        resp = self.client.get(reverse("jogo_empresa:empresas_crud", args=[self.jogo_m2.id]))
        self.assertEqual(resp.status_code, 403)

    def test_mediador_nao_pode_criar_empresa_em_jogo_de_outro(self):
        self.client.login(username="m1@test.com", password="447766ifg!")
        resp = self.client.post(reverse("jogo_empresa:empresas_crud", args=[self.jogo_m2.id]), {
            "action": "create",
            "nome": "Invasão"
        })
        self.assertEqual(resp.status_code, 403)
        self.assertFalse(Empresa.objects.filter(nome="Invasão").exists())

    def test_mediador_nao_pode_editar_empresa_de_outro(self):
        self.client.login(username="m1@test.com", password="447766ifg!")
        resp = self.client.post(reverse("jogo_empresa:empresas_crud", args=[self.jogo_m2.id]), {
            "action": "update",
            "id": self.empresa_m2.id,
            "nome": "Hackeada"
        })
        self.assertEqual(resp.status_code, 403)

    def test_superuser_pode_ver_todas_empresas(self):
        self.client.login(username="admin@test.com", password="447788ifg!")
        resp = self.client.get(reverse("jogo_empresa:empresas_crud", args=[self.jogo_m2.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Empresa M2")

   