from django.test import TestCase, Client 
from .models import Insumo,Produto,Cenario
from jogos.models import Jogo
from django.urls import reverse
from django.contrib.messages import get_messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User,Group

# Create your tests here.

#testes dos fluxos principais de views 

class CenariosTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.insumo_url = reverse("cenarios:home") 
        self.produto_url = reverse("cenarios:home") 
        self.cenario_url = reverse("cenarios:home")

        # Criar grupo Mediador (ou pegar se já existir)
        self.mediador_group, _ = Group.objects.get_or_create(name='Mediador')

        # Criar usuário mediador ativo
        self.mediador_user = User.objects.create_user(
            username='mediador1',
            email='mediadorteste1@gmail.com',
            password='mediadorparateste777',
            is_active=True
        )

        # Adicionar usuário ao grupo Mediador
        self.mediador_user.groups.add(self.mediador_group)

    def test_criar_insumo_valido(self):
        # Login do mediador
        login_sucesso = self.client.login(email='mediadorteste1@gmail.com', password='mediadorparateste777')
        self.assertTrue(login_sucesso, "Falha ao logar com mediador1")

        # Dados do Insumo
        data = {
            "model_type": "insumo",
            "action": "create",
            "nome": "Borracha",
            "fornecedor": "Borrachas LTDA",
            "quantidade": 0,
            "forma_pagamento": "avista"
        }

        # POST para criar insumo
        response = self.client.post(self.insumo_url, data, follow=True)

        # Verificar se o status da resposta é 200
        self.assertEqual(response.status_code, 200)

        # Verificar se o insumo foi criado
        self.assertTrue(Insumo.objects.filter(nome="Borracha").exists())

        # Verificar se a mensagem de sucesso aparece
        self.assertContains(response, "Insumo criado com sucesso!")

    def test_criar_produto_valido(self):
       
       login_sucesso = self.client.login(email='mediadorteste1@gmail.com', password='mediadorparateste777')
       self.assertTrue(login_sucesso, "Falha ao logar com mediador1")
       insumo = Insumo.objects.create(nome="Borracha", fornecedor="Borracharia LTDA", quantidade=0, criador=self.mediador_user)
       data = {
          "model_type": "produto",
          "action":"create",
          "nome": "Pneu",
          "insumos":[insumo.id],
       }

       response = self.client.post(self.produto_url,data,follow=True)
       self.assertEqual(response.status_code,200)
       self.assertTrue(Produto.objects.filter(nome="Pneu").exists())
       self.assertContains(response,"Produto criado com sucesso!")

    def test_criar_produto_invalido(self):
       
       login_sucesso = self.client.login(email='mediadorteste1@gmail.com', password='mediadorparateste777')
       self.assertTrue(login_sucesso, "Falha ao logar com mediador1")
       self.client.login(username='mediador1', password='1234')
       insumo = Insumo.objects.create(nome="Madeira",fornecedor="Madereira LTDA",quantidade=0, criador = self.mediador_user)
       self.produto_url = reverse("cenarios:home")

       data={
          "model_type": "produto",
          "action":"create",
          "nome" : "4321",
          "insumos":[insumo.id],
       }

       response = self.client.post(self.produto_url,data,follow=True)
       self.assertEqual(response.status_code,200)
       self.assertFalse(Produto.objects.exists())
       self.assertContains(response,"Erro ao salvar Produto, nome do Produto Inválido")
    
    def test_criar_cenario_valido(self):
        
        login_sucesso = self.client.login(email='mediadorteste1@gmail.com', password='mediadorparateste777')
        self.assertTrue(login_sucesso, "Falha ao logar com mediador1")
        self.client.login(username='mediador1', password='1234')
        insumo = Insumo.objects.create(nome="Borracha", fornecedor="Borracharia LTDA", quantidade=0,criador=self.mediador_user)
        produto = Produto.objects.create(nome="Pneu",criador=self.mediador_user)
        produto.insumos.add(insumo)

        data = {
           "model_type" : "cenario",
           "action":"create",
           "nome":"Bicicletas",
           "produto": produto.id,
        }
        
        response = self.client.post(self.cenario_url,data,follow=True)
        self.assertEqual(response.status_code,200)
        self.assertTrue(Cenario.objects.filter(nome="Bicicletas").exists())
    
    def test_criar_cenario_invalido(self):
        
        login_sucesso = self.client.login(email='mediadorteste1@gmail.com', password='mediadorparateste777')
        self.assertTrue(login_sucesso, "Falha ao logar com mediador1")
        self.client.login(username='mediador1', password='1234')
        self.cenario_url = reverse("cenarios:home")
        insumo = Insumo.objects.create(nome="Borracha", fornecedor="Borracharia LTDA", quantidade=0,criador=self.mediador_user)
        produto = Produto.objects.create(nome="Pneu",criador=self.mediador_user)
        produto.insumos.add(insumo)

        data = {
           "model_type":"cenario",
           "action" : "create",
           "nome" : "242424",
           "produto": produto.id,
        }

        response = self.client.post(self.cenario_url,data,follow=True)
        self.assertEqual(response.status_code,200)
        self.assertFalse(Cenario.objects.exists())
        self.assertContains(response,"Erro ao salvar Cenário, nome do Cenário Inválido")

    def test_deletar_insumo_sem_estar_produto(self):
        
        login_sucesso = self.client.login(email='mediadorteste1@gmail.com', password='mediadorparateste777')
        self.assertTrue(login_sucesso, "Falha ao logar com mediador1")
        insumo = Insumo.objects.create(nome="Borracha", fornecedor="Borracharia LTDA", quantidade=0,criador=self.mediador_user)
        self.assertEqual(Insumo.objects.count(),1)
        url = reverse("cenarios:removerInsumo", args=[insumo.id])
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, reverse("cenarios:home"))
        self.assertEqual(Insumo.objects.count(), 0)
        self.assertContains(response,"Insumo Deletado com sucesso")

    def test_deletar_insumo_estar_produto(self):
        
        login_sucesso = self.client.login(email='mediadorteste1@gmail.com', password='mediadorparateste777')
        self.assertTrue(login_sucesso, "Falha ao logar com mediador1")
        insumo = Insumo.objects.create(nome="Borracha", fornecedor="Borracharia LTDA", quantidade=0,criador=self.mediador_user)
        produto = Produto.objects.create(nome="Pneu",criador=self.mediador_user)
        produto.insumos.add(insumo)
        url = reverse("cenarios:removerInsumo",args=[insumo.id])
        response = self.client.post(url,follow=True)
        self.assertEqual(response.status_code,200)
        self.assertTrue(Insumo.objects.filter(id=insumo.id).exists())
        self.assertTrue(Produto.objects.filter(id=produto.id).exists())
        self.assertContains(response,"Não é possível excluir o insumo pois está associado a um produto!")

       
    def test_deletar_produto_sem_estar_cenario(self):
       
       login_sucesso = self.client.login(email='mediadorteste1@gmail.com', password='mediadorparateste777')
       self.assertTrue(login_sucesso, "Falha ao logar com mediador1")
       insumo = Insumo.objects.create(nome="Borracha", fornecedor="Borracharia LTDA", quantidade=0,criador=self.mediador_user)
       produto = Produto.objects.create(nome="Pneu",criador=self.mediador_user)
       produto.insumos.add(insumo)
       self.assertEqual(Produto.objects.count(),1)
       url = reverse("cenarios:removerProduto", args=[produto.id])
       response = self.client.get(url, follow=True)
       self.assertRedirects(response, reverse("cenarios:home"))
       self.assertEqual(Produto.objects.count(), 0)
       self.assertContains(response,"Produto Deletado com sucesso")


    def test_deletar_produto_estar_cenario(self):
       
       login_sucesso = self.client.login(email='mediadorteste1@gmail.com', password='mediadorparateste777')
       self.assertTrue(login_sucesso, "Falha ao logar com mediador1")
       insumo = Insumo.objects.create(nome="Borracha", fornecedor="Borracharia LTDA", quantidade=0,criador=self.mediador_user)
       produto = Produto.objects.create(nome="Pneu",criador=self.mediador_user)
       produto.insumos.add(insumo)
       Cenario.objects.create(nome="Bicicletas",produto=produto,criador=self.mediador_user)
       self.assertEqual(Produto.objects.count(),1)
       url = reverse("cenarios:removerProduto", args=[produto.id])
       response = self.client.get(url,follow=True)
       self.assertRedirects(response, reverse("cenarios:home"))
       self.assertTrue(Produto.objects.filter(id=produto.id).exists())
       self.assertEqual(Produto.objects.count(), 1)
       self.assertContains(response,"Não é possível excluir o produto pois está associado a um cenário!")


    def test_remover_cenario_sem_jogo_ativo(self):
       
       login_sucesso = self.client.login(email='mediadorteste1@gmail.com', password='mediadorparateste777')
       self.assertTrue(login_sucesso, "Falha ao logar com mediador1")
       insumo = Insumo.objects.create(nome="Borracha", fornecedor="Borracharia LTDA", quantidade=0,criador=self.mediador_user)
       produto = Produto.objects.create(nome="Pneu",criador=self.mediador_user)
       produto.insumos.add(insumo)
       cenario = Cenario.objects.create(nome="Bicicletas",produto=produto,criador=self.mediador_user)
       url = reverse("cenarios:removerCenario", args=[cenario.id])
       response = self.client.get(url, follow=True)
       self.assertEqual(response.status_code, 200)
       self.assertFalse(Cenario.objects.filter(id=cenario.id).exists())
       self.assertContains(response, "Cenário Deletado com sucesso")

    def test_remover_cenario_com_jogo_ativo(self):
       
       login_sucesso = self.client.login(email='mediadorteste1@gmail.com', password='mediadorparateste777')
       self.assertTrue(login_sucesso, "Falha ao logar com mediador1")
       insumo = Insumo.objects.create(nome="Borracha", fornecedor="Borracharia LTDA", quantidade=0,criador=self.mediador_user)
       produto = Produto.objects.create(nome="Pneu",criador=self.mediador_user)
       produto.insumos.add(insumo)
       cenario = Cenario.objects.create(nome="Bicicletas",produto=produto,criador=self.mediador_user)

       Jogo.objects.create(nome="Jogo das Bike",cod= "1",status=Jogo.ATIVO,cenario=cenario,periodo_anterior=0,periodo_atual=0,status_decisoes_disponiveis=False,criador=self.mediador_user)

       url = reverse("cenarios:removerCenario", args=[cenario.id])
       response = self.client.get(url, follow=True)
       self.assertEqual(response.status_code, 200)
       self.assertTrue(Cenario.objects.filter(id=cenario.id).exists())
       self.assertContains(response,"Este Cenário está em um Jogo Ativo, Não é possível deletá-lo")
       
    def test_editar_insumo(self):
        
        login_sucesso = self.client.login(email='mediadorteste1@gmail.com', password='mediadorparateste777')
        self.assertTrue(login_sucesso, "Falha ao logar com mediador1")
        insumo = Insumo.objects.create(nome="Borracha", fornecedor="Borracharia LTDA", quantidade=0,criador=self.mediador_user)
        url = reverse("cenarios:editarInsumo", args=[insumo.id])
        
        novos_dados = {
            "nome": "Pedal",
            "fornecedor": "Pedaleiros",
        }

        response = self.client.post(url, novos_dados, follow=True)
        insumo.refresh_from_db()
        self.assertEqual(insumo.nome, "Pedal")
        self.assertEqual(insumo.fornecedor, "Pedaleiros")
        self.assertRedirects(response, reverse("cenarios:home"))

    def test_editar_produto(self):
       
       login_sucesso = self.client.login(email='mediadorteste1@gmail.com', password='mediadorparateste777')
       self.assertTrue(login_sucesso, "Falha ao logar com mediador1")
       insumo1 = Insumo.objects.create(nome="Borracha", fornecedor="Borracharia LTDA", quantidade=0,criador=self.mediador_user)
       insumo2 = Insumo.objects.create(nome="Mármore", fornecedor="Pedreira", quantidade=0,criador=self.mediador_user)

       produto = Produto.objects.create(nome="Pneu",criador=self.mediador_user)
       produto.insumos.add(insumo1)
       
       url = reverse("cenarios:editarProduto", args=[produto.id])

       novos_dados = {
            "nome": "Piso",
            "insumos": [insumo2.id],
        }
       
       response = self.client.post(url, novos_dados, follow=True)
       produto.refresh_from_db()
       self.assertEqual(produto.nome, "Piso")
       insumos_ids = list(produto.insumos.values_list('id', flat=True))
       self.assertEqual(insumos_ids, [insumo2.id])
       self.assertRedirects(response, reverse("cenarios:home"))

    def test_editar_cenario(self):
       
       login_sucesso = self.client.login(email='mediadorteste1@gmail.com', password='mediadorparateste777')
       self.assertTrue(login_sucesso, "Falha ao logar com mediador1")
       insumo1 = Insumo.objects.create(nome="Borracha", fornecedor="Borracharia LTDA", quantidade=0,criador=self.mediador_user)
       insumo2 = Insumo.objects.create(nome="Mármore", fornecedor="Pedreira", quantidade=0,criador=self.mediador_user)

       produto1 = Produto.objects.create(nome="Pneu",criador=self.mediador_user)
       produto2 = Produto.objects.create(nome="Piso",criador=self.mediador_user)

       produto1.insumos.add(insumo1)
       produto2.insumos.add(insumo2)

       cenario = Cenario.objects.create(nome="Bicicletas",produto=produto1,criador=self.mediador_user)

       url = reverse("cenarios:editarCenario", args=[cenario.id])

       novos_dados = {
            "nome": "Loja de Pisos",
            "produto": produto2.id,
        }
       
       response = self.client.post(url, novos_dados, follow=True)
       cenario.refresh_from_db()
       self.assertEqual(cenario.nome, "Loja de Pisos")
       self.assertEqual(cenario.produto.id,produto2.id)
       self.assertRedirects(response, reverse("cenarios:home"))

    def test_listar_insumos(self):

       login_sucesso = self.client.login(email='mediadorteste1@gmail.com', password='mediadorparateste777')
       self.assertTrue(login_sucesso, "Falha ao logar com mediador1")
       Insumo.objects.create(nome="Borracha", fornecedor="Borracharia LTDA", quantidade=0,criador=self.mediador_user)
       Insumo.objects.create(nome="Mármore", fornecedor="Pedreira", quantidade=0,criador=self.mediador_user)
       Insumo.objects.create(nome="Madeira", fornecedor="Madereiros LTDA", quantidade=0,criador=self.mediador_user)
       Insumo.objects.create(nome="Mola", fornecedor="Moleiros", quantidade=0,criador=self.mediador_user)

       url = reverse("cenarios:home")
       response = self.client.get(url,follow=True)

       self.assertEqual(response.status_code, 200)
       self.assertContains(response, "Borracha")
       self.assertContains(response, "Mármore")
       self.assertContains(response, "Madeira")
       self.assertContains(response, "Mola")
       self.assertEqual(Insumo.objects.count(), 4)

    def test_listar_produtos(self):
       
       login_sucesso = self.client.login(email='mediadorteste1@gmail.com', password='mediadorparateste777')
       self.assertTrue(login_sucesso, "Falha ao logar com mediador1")
       insumo1 = Insumo.objects.create(nome="Borracha", fornecedor="Borracharia LTDA", quantidade=0,criador=self.mediador_user)
       insumo2 = Insumo.objects.create(nome="Mármore", fornecedor="Pedreira", quantidade=0,criador=self.mediador_user)
       insumo3 = Insumo.objects.create(nome="Madeira", fornecedor="Madereiros LTDA", quantidade=0,criador=self.mediador_user)
       insumo4 = Insumo.objects.create(nome="Mola", fornecedor="Moleiros", quantidade=0,criador=self.mediador_user)

       produto1 = Produto.objects.create(nome="Pneu",criador=self.mediador_user)
       produto2 = Produto.objects.create(nome="Piso",criador=self.mediador_user)
       produto3 = Produto.objects.create(nome="Suspensão",criador=self.mediador_user)
       produto4 = Produto.objects.create(nome = "Quadros",criador=self.mediador_user)

       produto1.insumos.add(insumo1)
       produto2.insumos.add(insumo2)
       produto3.insumos.add(insumo4)
       produto4.insumos.add(insumo3)

       url = reverse("cenarios:home")
       response = self.client.get(url,follow=True)
       self.assertEqual(response.status_code, 200)
       self.assertContains(response, "Pneu")
       self.assertContains(response, "Piso")
       self.assertContains(response, "Suspensão")
       self.assertContains(response, "Quadros")
       self.assertEqual(Insumo.objects.count(), 4)

    def test_listar_cenarios(self):
       
       login_sucesso = self.client.login(email='mediadorteste1@gmail.com', password='mediadorparateste777')
       self.assertTrue(login_sucesso, "Falha ao logar com mediador1")
       insumo1 = Insumo.objects.create(nome="Borracha", fornecedor="Borracharia LTDA", quantidade=0,criador=self.mediador_user)
       insumo2 = Insumo.objects.create(nome="Mármore", fornecedor="Pedreira", quantidade=0,criador=self.mediador_user)
       insumo3 = Insumo.objects.create(nome="Madeira", fornecedor="Madereiros LTDA", quantidade=0,criador=self.mediador_user)
       insumo4 = Insumo.objects.create(nome="Mola", fornecedor="Moleiros", quantidade=0,criador=self.mediador_user)
       produto1 = Produto.objects.create(nome="Pneu",criador=self.mediador_user)
       produto2 = Produto.objects.create(nome="Piso",criador=self.mediador_user)
       produto3 = Produto.objects.create(nome="Suspensão",criador=self.mediador_user)
       produto4 = Produto.objects.create(nome = "Quadros",criador=self.mediador_user)

       produto1.insumos.add(insumo1)
       produto2.insumos.add(insumo2)
       produto3.insumos.add(insumo4)
       produto4.insumos.add(insumo3)

       Cenario.objects.create(nome="Loja de Bicicletas",produto=produto1,criador=self.mediador_user)
       Cenario.objects.create(nome="Loja de Construção de Casas",produto=produto2,criador=self.mediador_user)
       Cenario.objects.create(nome="Oficina Mecânica",produto=produto3,criador=self.mediador_user)
       Cenario.objects.create(nome="Loja de Decorações",produto=produto4,criador=self.mediador_user)

       url = reverse("cenarios:home")
       response = self.client.get(url,follow=True)
       self.assertEqual(response.status_code, 200)
       self.assertContains(response, "Loja de Bicicletas")
       self.assertContains(response, "Loja de Construção de Casas")
       self.assertContains(response, "Oficina Mecânica")
       self.assertContains(response, "Loja de Decorações")
       self.assertEqual(Insumo.objects.count(), 4)
   
   
User = get_user_model()

class InsumoPermissionsTest(TestCase):
    def setUp(self):
       
        self.mediador_group, _ = Group.objects.get_or_create(name='Mediador')

       
        self.mediador1 = User.objects.create_user(
            username='mediador1',
            email='mediadorteste1@gmail.com',
            password='senhamediadorteste1',
            cpf='037.868.811-11',
            is_active=True
        )
        self.mediador2 = User.objects.create_user(
            username='mediador2',
            email='mediadorteste2@gmail.com',
            password='senhamediadorteste2',
            cpf='085.053.381-38',
            is_active=True
        )

      
        self.mediador1.groups.add(self.mediador_group)
        self.mediador2.groups.add(self.mediador_group)

     
        self.insumo = Insumo.objects.create(
            nome="Insumo Teste",
            fornecedor="Fornecedor Teste",
            quantidade=10,
            criador=self.mediador2
        )

        self.client = Client()

    def test_mediador_nao_pode_deletar_insumo_que_nao_e_seu(self):
       
       login_sucesso = self.client.login(email='mediadorteste1@gmail.com', password='senhamediadorteste1')
       self.assertTrue(login_sucesso, "Falha ao logar com mediador1")

       url = reverse('cenarios:removerInsumo', args=[self.insumo.id])

       response = self.client.post(url, follow=True)

       
       self.assertTrue(
            Insumo.objects.filter(id=self.insumo.id).exists(),
       )

       self.assertEqual(
            response.status_code, 404,
            f"Esperado status 404, mas foi {response.status_code}"
       )
