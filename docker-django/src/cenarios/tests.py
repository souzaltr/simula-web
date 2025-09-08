from django.test import TestCase, Client 
from .models import Insumo,Produto,Cenario
from jogos.models import Jogo
from django.urls import reverse

# Create your tests here.

#testes dos fluxos principais de views 

class CenariosTest(TestCase):
    
    def setUp(self):
      self.client = Client()
      self.insumo_url = reverse("cenarios:home")
      self.produto_url = reverse("cenarios:home")
      self.cenario_url = reverse("cenarios:home")

    def test_criar_insumo_valido(self):
       
       data = {
          "model_type": "insumo",
          "action": "create",
          "nome": "Borracha",
          "fornecedor": "Borrachas LTDA",
          "quantidade": 0,
          "forma_pagamento": "avista",
       }

       response = self.client.post(self.insumo_url,data,follow=True)
       self.assertEqual(response.status_code,200)
       self.assertTrue(Insumo.objects.filter(nome="Borracha").exists())
       self.assertContains(response,"Insumo criado com sucesso!")

    def test_criar_insumo_invalido(self):
       
       data = {
          "model_type":"insumo",
          "action": "create",
          "nome": "1234",
          "fornecedor" : "Fornecedor de Números",
          "quantidade": 5,
       }

       response = self.client.post(self.insumo_url,data,follow=True)
       self.assertEqual(response.status_code,200)
       self.assertFalse(Insumo.objects.exists())
       self.assertContains(response,"Erro ao salvar insumo, nome do insumo inválido!")

    def test_criar_produto_valido(self):
       
       insumo = Insumo.objects.create(nome="Borracha", fornecedor="Borracharia LTDA", quantidade=0)

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
       
       insumo = Insumo.objects.create(nome="Madeira",fornecedor="Madereira LTDA",quantidade=0)
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
        
        insumo = Insumo.objects.create(nome="Borracha", fornecedor="Borracharia LTDA", quantidade=0)
        produto = Produto.objects.create(nome="Pneu")
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
        
        self.cenario_url = reverse("cenarios:home")
        insumo = Insumo.objects.create(nome="Borracha", fornecedor="Borracharia LTDA", quantidade=0)
        produto = Produto.objects.create(nome="Pneu")
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
        
        insumo = Insumo.objects.create(nome="Borracha", fornecedor="Borracharia LTDA", quantidade=0)
        self.assertEqual(Insumo.objects.count(),1)
        url = reverse("cenarios:removerInsumo", args=[insumo.id])
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, reverse("cenarios:home"))
        self.assertEqual(Insumo.objects.count(), 0)
        self.assertContains(response,"Insumo Deletado com sucesso")

    def test_deletar_insumo_estar_produto(self):
        
        insumo = Insumo.objects.create(nome="Borracha", fornecedor="Borracharia LTDA", quantidade=0)
        produto = Produto.objects.create(nome="Pneu")
        produto.insumos.add(insumo)
        url = reverse("cenarios:removerInsumo",args=[insumo.id])
        response = self.client.post(url,follow=True)
        self.assertEqual(response.status_code,200)
        self.assertTrue(Insumo.objects.filter(id=insumo.id).exists())
        self.assertTrue(Produto.objects.filter(id=produto.id).exists())
        self.assertContains(response,"Não é possível excluir o insumo pois está associado a um produto!")

       
    def test_deletar_produto_sem_estar_cenario(self):
       
       insumo = Insumo.objects.create(nome="Borracha", fornecedor="Borracharia LTDA", quantidade=0)
       produto = Produto.objects.create(nome="Pneu")
       produto.insumos.add(insumo)
       self.assertEqual(Produto.objects.count(),1)
       url = reverse("cenarios:removerProduto", args=[produto.id])
       response = self.client.get(url, follow=True)
       self.assertRedirects(response, reverse("cenarios:home"))
       self.assertEqual(Produto.objects.count(), 0)
       self.assertContains(response,"Produto Deletado com sucesso")


    def test_deletar_produto_estar_cenario(self):
       insumo = Insumo.objects.create(nome="Borracha", fornecedor="Borracharia LTDA", quantidade=0)
       produto = Produto.objects.create(nome="Pneu")
       produto.insumos.add(insumo)
       Cenario.objects.create(nome="Bicicletas",produto=produto)
       self.assertEqual(Produto.objects.count(),1)
       url = reverse("cenarios:removerProduto", args=[produto.id])
       response = self.client.get(url,follow=True)
       self.assertRedirects(response, reverse("cenarios:home"))
       self.assertTrue(Produto.objects.filter(id=produto.id).exists())
       self.assertEqual(Produto.objects.count(), 1)
       self.assertContains(response,"Não é possível excluir o produto pois está associado a um cenário!")


    def test_remover_cenario_sem_jogo_ativo(self):
       
       insumo = Insumo.objects.create(nome="Borracha", fornecedor="Borracharia LTDA", quantidade=0)
       produto = Produto.objects.create(nome="Pneu")
       produto.insumos.add(insumo)
       cenario = Cenario.objects.create(nome="Bicicletas",produto=produto)
       url = reverse("cenarios:removerCenario", args=[cenario.id])
       response = self.client.get(url, follow=True)
       self.assertEqual(response.status_code, 200)
       self.assertFalse(Cenario.objects.filter(id=cenario.id).exists())
       self.assertContains(response, "Cenário Deletado com sucesso")

    def test_remover_cenario_com_jogo_ativo(self):
       
       insumo = Insumo.objects.create(nome="Borracha", fornecedor="Borracharia LTDA", quantidade=0)
       produto = Produto.objects.create(nome="Pneu")
       produto.insumos.add(insumo)
       cenario = Cenario.objects.create(nome="Bicicletas",produto=produto)
       Jogo.objects.create(nome="Jogo das Bike",cod="1",status=Jogo.ATIVO,cenario=cenario,periodo_anterior=0,periodo_atual=0,status_decisoes_disponiveis=False)
       url = reverse("cenarios:removerCenario", args=[cenario.id])
       response = self.client.get(url, follow=True)
       self.assertEqual(response.status_code, 200)
       self.assertTrue(Cenario.objects.filter(id=cenario.id).exists())
       self.assertContains(response,"Este Cenário está em um Jogo Ativo, Não é possível deletá-lo")
       
    def test_editar_insumo(self):
        
        insumo = Insumo.objects.create(nome="Borracha", fornecedor="Borracharia LTDA", quantidade=0)
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
       
       insumo1 = Insumo.objects.create(nome="Borracha", fornecedor="Borracharia LTDA", quantidade=0)
       insumo2 = Insumo.objects.create(nome="Mármore", fornecedor="Pedreira", quantidade=0)

       produto = Produto.objects.create(nome="Pneu")
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
       
       insumo1 = Insumo.objects.create(nome="Borracha", fornecedor="Borracharia LTDA", quantidade=0)
       insumo2 = Insumo.objects.create(nome="Mármore", fornecedor="Pedreira", quantidade=0)

       produto1 = Produto.objects.create(nome="Pneu")
       produto2 = Produto.objects.create(nome="Piso")

       produto1.insumos.add(insumo1)
       produto2.insumos.add(insumo2)

       cenario = Cenario.objects.create(nome="Bicicletas",produto=produto1)

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

       Insumo.objects.create(nome="Borracha", fornecedor="Borracharia LTDA", quantidade=0)
       Insumo.objects.create(nome="Mármore", fornecedor="Pedreira", quantidade=0)
       Insumo.objects.create(nome="Madeira", fornecedor="Madereiros LTDA", quantidade=0)
       Insumo.objects.create(nome="Mola", fornecedor="Moleiros", quantidade=0)

       url = reverse("cenarios:home")
       response = self.client.get(url,follow=True)

       self.assertEqual(response.status_code, 200)
       self.assertContains(response, "Borracha")
       self.assertContains(response, "Mármore")
       self.assertContains(response, "Madeira")
       self.assertContains(response, "Mola")
       self.assertEqual(Insumo.objects.count(), 4)

    def test_listar_produtos(self):
       
       insumo1 = Insumo.objects.create(nome="Borracha", fornecedor="Borracharia LTDA", quantidade=0)
       insumo2 = Insumo.objects.create(nome="Mármore", fornecedor="Pedreira", quantidade=0)
       insumo3 = Insumo.objects.create(nome="Madeira", fornecedor="Madereiros LTDA", quantidade=0)
       insumo4 = Insumo.objects.create(nome="Mola", fornecedor="Moleiros", quantidade=0)

       produto1 = Produto.objects.create(nome="Pneu")
       produto2 = Produto.objects.create(nome="Piso")
       produto3 = Produto.objects.create(nome="Suspensão")
       produto4 = Produto.objects.create(nome = "Quadros")

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
       
       insumo1 = Insumo.objects.create(nome="Borracha", fornecedor="Borracharia LTDA", quantidade=0)
       insumo2 = Insumo.objects.create(nome="Mármore", fornecedor="Pedreira", quantidade=0)
       insumo3 = Insumo.objects.create(nome="Madeira", fornecedor="Madereiros LTDA", quantidade=0)
       insumo4 = Insumo.objects.create(nome="Mola", fornecedor="Moleiros", quantidade=0)
       produto1 = Produto.objects.create(nome="Pneu")
       produto2 = Produto.objects.create(nome="Piso")
       produto3 = Produto.objects.create(nome="Suspensão")
       produto4 = Produto.objects.create(nome = "Quadros")

       produto1.insumos.add(insumo1)
       produto2.insumos.add(insumo2)
       produto3.insumos.add(insumo4)
       produto4.insumos.add(insumo3)

       Cenario.objects.create(nome="Loja de Bicicletas",produto=produto1)
       Cenario.objects.create(nome="Loja de Construção de Casas",produto=produto2)
       Cenario.objects.create(nome="Oficina Mecânica",produto=produto3)
       Cenario.objects.create(nome="Loja de Decorações",produto=produto4)

       url = reverse("cenarios:home")
       response = self.client.get(url,follow=True)
       self.assertEqual(response.status_code, 200)
       self.assertContains(response, "Loja de Bicicletas")
       self.assertContains(response, "Loja de Construção de Casas")
       self.assertContains(response, "Oficina Mecânica")
       self.assertContains(response, "Loja de Decorações")
       self.assertEqual(Insumo.objects.count(), 4)