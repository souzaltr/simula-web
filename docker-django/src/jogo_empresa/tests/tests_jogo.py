from django.test import TestCase, Client 
from django.urls import reverse
from django.contrib.auth import get_user_model
from cenarios.models import Cenario, Produto, Insumo
from jogo_empresa.models import Jogo
from django.contrib.auth.models import Group

Usuario = get_user_model()

# Create your tests here.
class JogoTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        insumo=Insumo.objects.create(nome="Madeira", fornecedor="Bertazini",forma_pagamento="À Vista",quantidade=50)
        produto=Produto.objects.create(nome="Guarda-roupa")
        produto.insumos.set([insumo])
        cls.cenario=Cenario.objects.create(nome="Loja de móveis", produto=produto)

        cls.usuario = Usuario.objects.create_user(username="user1", email="u1@test.com",cpf="167.842.470-60",password="447766ifg!")
        mediador_group, created = Group.objects.get_or_create(name="Mediador")
        cls.usuario.groups.add(mediador_group)
        cls.usuario.save()

    def setUp(self):
        self.client.login(username="u1@test.com", password="447766ifg!")    

    def test_lista_vazia_jogos(self):
        response= self.client.get(reverse("jogo_empresa:jogos_crud")) 
        self.assertEqual(response.status_code,200)
        self.assertContains(response,"Nenhum jogo cadastrado")

    def test_criar_jogo_valido(self):
        response= self.client.post(reverse("jogo_empresa:jogos_crud"), {
            "action": "create",
            "nome": "Jogo de teste",
            "cenario_id": self.cenario.id
        })
        self.assertEqual(response.status_code, 302) 
        self.assertTrue(Jogo.objects.filter(nome="Jogo de teste", cenario=self.cenario).exists())      

    def test_jogo_nome_vazio(self):
        response= self.client.post(reverse("jogo_empresa:jogos_crud"),{
            "action":"create",
            "nome":" ",
            "cenario_id": self.cenario.id
        })
        self.assertEqual(response.status_code,200)
        self.assertContains(response,"Nome não pode ser vazio ou somente espaços.")
        self.assertEqual(Jogo.objects.count(),0)

    def test_nao_criar_jogo_sem_cenario(self):
        response = self.client.post(reverse("jogo_empresa:jogos_crud"), {
            "action": "create",
            "nome": "Jogo sem cenário",
             })

        self.assertNotEqual(response.status_code, 302, msg="Selecione um cenário para criar o jogo.")
    
    def test_editar_nome_do_jogo(self):
        jogo= Jogo.objects.create(nome="Jogo não editado",cenario=self.cenario, criador=self.usuario)
        response= self.client.post(reverse("jogo_empresa:jogos_crud"), {
            "action":"update",
            "id":jogo.id,
            "nome":"Jogo editado",
            "cenario_id":self.cenario.id
        })
        self.assertEqual(response.status_code,302)
        jogo.refresh_from_db()
        self.assertEqual(jogo.nome, "Jogo editado")

    def test_nao_edicao_cenario(self):
        novo_insumo=Insumo.objects.create(nome="Borracha", fornecedor="Pirelli",forma_pagamento="À Vista",quantidade=200)
        novo_produto=Produto.objects.create(nome="Pneu")
        novo_produto.insumos.set([novo_insumo])
        novo_cenario=Cenario.objects.create(nome="Borracharia", produto=novo_produto)
        jogo=Jogo.objects.create(nome="Jogo", cenario=self.cenario, criador=self.usuario)

        response = self.client.post(reverse("jogo_empresa:jogos_crud"), {
            "action": "update",
            "id": jogo.id,
            "nome": "Jogo",
            "cenario_id": novo_cenario.id
        })

        self.assertEqual(response.status_code, 302)
        jogo.refresh_from_db()
        self.assertEqual(jogo.cenario, self.cenario) # cenario não deve mudar    

    def test_excluir_jogo(self):
        jogo=Jogo.objects.create(nome="ExcluirJogo", cenario=self.cenario,criador=self.usuario)
        response=self.client.post(reverse("jogo_empresa:jogos_crud"), {
            "action": "delete",
            "id": jogo.id
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Jogo.objects.filter(id=jogo.id).exists())

    def test_alterar_status(self):
        jogo1 = Jogo.objects.create(nome="Ativo", cenario=self.cenario,criador=self.usuario)
        jogo2 = Jogo.objects.create(nome="Inativo", cenario=self.cenario, status=Jogo.INATIVO, criador=self.usuario)

        response = self.client.post(reverse("jogo_empresa:jogos_crud"), {
            "action": "alterar_status",
            "jogos_selecionados": [jogo1.id, jogo2.id]
        })

        self.assertEqual(response.status_code, 302)
        jogo1.refresh_from_db()
        jogo2.refresh_from_db()
        self.assertEqual(jogo1.status, Jogo.INATIVO)
        self.assertEqual(jogo2.status, Jogo.ATIVO)

class JogoPermissaoTestCase(TestCase):
    def setUp(self):
        self.m1 = Usuario.objects.create_user(username="m1", email="m1@test.com",cpf="155.078.190-17", password="447766ifg!")
        self.m2 = Usuario.objects.create_user(username="m2", email="m2@test.com",cpf="483.738.610-50", password="123784ifg!")
        self.super = Usuario.objects.create_superuser(username="admin", email="admin@test.com",cpf="932.164.470-90", password="447788ifg!")
        
        mediador_group, _ = Group.objects.get_or_create(name="Mediador")
        self.m1.groups.add(mediador_group)
        self.m2.groups.add(mediador_group) 
        self.m1.save()
        self.m2.save()

        insumo=Insumo.objects.create(nome="Madeira", fornecedor="Bertazini",forma_pagamento="À Vista",quantidade=50)
        self.produto = Produto.objects.create(nome="ProdutoX")
        self.produto.insumos.set([insumo])
        self.cenario = Cenario.objects.create(nome="Cenário X", produto=self.produto)

        self.jogo_m1 = Jogo.objects.create(nome="Jogo M1", cenario=self.cenario, criador=self.m1)
        self.jogo_m2 = Jogo.objects.create(nome="Jogo M2", cenario=self.cenario, criador=self.m2)

        self.client = Client()

    def test_mediador_ve_apenas_seus_jogos(self):
        self.client.login(username="m1@test.com", password="447766ifg!")
        resp = self.client.get(reverse("jogo_empresa:jogos_crud"))
        self.assertContains(resp, "Jogo M1")
        self.assertNotContains(resp, "Jogo M2")

    def test_mediador_nao_pode_editar_jogo_de_outro(self):
        self.client.login(username="m1@test.com", password="447766ifg!")
        resp = self.client.post(reverse("jogo_empresa:jogos_crud"), {
            "action": "update",
            "id": self.jogo_m2.id,
            "nome": "Hackeado"
        })
        self.assertEqual(resp.status_code, 403)

    def test_mediador_nao_pode_deletar_jogo_de_outro(self):
        self.client.login(username="m1@test.com", password="447766ifg!")
        resp = self.client.post(reverse("jogo_empresa:jogos_crud"), {
            "action": "delete",
            "id": self.jogo_m2.id
        })
        self.assertEqual(resp.status_code, 403)
        self.assertTrue(Jogo.objects.filter(id=self.jogo_m2.id).exists())

    def test_superuser_ve_todos_os_jogos(self):
        self.client.login(username="admin@test.com", password="447788ifg!")
        resp = self.client.get(reverse("jogo_empresa:jogos_crud"))
        self.assertContains(resp, "Jogo M1")
        self.assertContains(resp, "Jogo M2")        