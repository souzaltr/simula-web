from django.test import TestCase 
from django.urls import reverse
from cenarios.models import Cenario, Produto, Insumo
from myapp.models import Jogo

# Create your tests here.
class JogoTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        insumo=Insumo.objects.create(nome="Madeira", fornecedor="Bertazini",forma_pagamento="À Vista",quantidade=50)
        produto=Produto.objects.create(nome="Guarda-roupa")
        produto.insumos.set([insumo])
        cls.cenario=Cenario.objects.create(nome="Loja de móveis", produto=produto)

    def test_lista_vazia_jogos(self):
        response= self.client.get(reverse("myapp:jogos_crud")) 
        self.assertEqual(response.status_code,200)
        self.assertContains(response,"Nenhum jogo cadastrado")

    def test_criar_jogo_valido(self):
        response= self.client.post(reverse("myapp:jogos_crud"), {
            "action": "create",
            "nome": "Jogo de teste",
            "cenario_id": self.cenario.id
        })
        self.assertEqual(response.status_code, 302) 
        self.assertTrue(Jogo.objects.filter(nome="Jogo de teste", cenario=self.cenario).exists())      

    def test_jogo_nome_vazio(self):
        response= self.client.post(reverse("myapp:jogos_crud"),{
            "action":"create",
            "nome":" ",
            "cenario_id": self.cenario.id
        })
        self.assertEqual(response.status_code,200)
        self.assertContains(response,"Nome não pode ser vazio ou somente espaços.")
        self.assertEqual(Jogo.objects.count(),0)

    def test_nao_criar_jogo_sem_cenario(self):
        response = self.client.post(reverse("myapp:jogos_crud"), {
            "action": "create",
            "nome": "Jogo sem cenário",
             })

        self.assertNotEqual(response.status_code, 302, msg="Selecione um cenário para criar o jogo.")
    
    def test_editar_nome_do_jogo(self):
        jogo= Jogo.objects.create(nome="Jogo não editado",cenario=self.cenario)
        response= self.client.post(reverse("myapp:jogos_crud"), {
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
        jogo=Jogo.objects.create(nome="Jogo", cenario=self.cenario)

        response = self.client.post(reverse("myapp:jogos_crud"), {
            "action": "update",
            "id": jogo.id,
            "nome": "Jogo",
            "cenario_id": novo_cenario.id
        })

        self.assertEqual(response.status_code, 302)
        jogo.refresh_from_db()
        self.assertEqual(jogo.cenario, self.cenario) # cenario não deve mudar    

    def test_excluir_jogo(self):
        jogo=Jogo.objects.create(nome="ExcluirJogo", cenario=self.cenario)
        response=self.client.post(reverse("myapp:jogos_crud"), {
            "action": "delete",
            "id": jogo.id
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Jogo.objects.filter(id=jogo.id).exists())

    def test_alterar_status(self):
        jogo1 = Jogo.objects.create(nome="Ativo", cenario=self.cenario)
        jogo2 = Jogo.objects.create(nome="Inativo", cenario=self.cenario, status=Jogo.INATIVO)

        response = self.client.post(reverse("myapp:jogos_crud"), {
            "action": "alterar_status",
            "jogos_selecionados": [jogo1.id, jogo2.id]
        })

        self.assertEqual(response.status_code, 302)
        jogo1.refresh_from_db()
        jogo2.refresh_from_db()
        self.assertEqual(jogo1.status, Jogo.INATIVO)
        self.assertEqual(jogo2.status, Jogo.ATIVO)