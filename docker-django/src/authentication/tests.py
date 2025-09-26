from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from .models import Usuario, validate_cpf
from .forms import RegisterForm, AdminUserCreationForm
from jogos.models import Jogo
from jogo_empresa.models import Empresa
from cenarios.models import Cenario, Produto, Insumo

class UsuarioModelTest(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'cpf': '123.456.789-09'
        }
        
    def test_create_user(self):
        user = Usuario.objects.create_user(**self.user_data)
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.cpf, self.user_data['cpf'])
        
    def test_str_representation(self):
        user = Usuario.objects.create_user(**self.user_data)
        self.assertEqual(str(user), self.user_data['email'])

class CpfValidatorTest(TestCase):
    def test_valid_cpf_formats(self):
        valid_cpfs = ['123.456.789-09', '12345678909']
        for cpf in valid_cpfs:
            try:
                validate_cpf(cpf)
            except ValidationError:
                self.fail(f"validate_cpf raised ValidationError unexpectedly for {cpf}")
                
    def test_invalid_cpf_formats(self):
        invalid_cpfs = [
            '123.456.789', # CPF incompleto
            'abc.def.ghi-jk', # Caracteres não numéricos
            '111.111.111-11', # Dígitos repetidos
            '123.456.789-00' # CPF inválido
        ]
        for cpf in invalid_cpfs:
            with self.assertRaises(ValidationError):
                validate_cpf(cpf)

class RegisterFormTest(TestCase):
    def setUp(self):
        # Criar cenário necessário primeiro
        self.insumo = Insumo.objects.create(
            nome='Insumo Teste',
            fornecedor='Fornecedor Teste'
        )
        self.produto = Produto.objects.create(nome='Produto Teste')
        self.produto.insumos.add(self.insumo)
        self.cenario = Cenario.objects.create(
            nome='Cenario Teste',
            produto=self.produto
        )
        
        # Criar jogo com cenário
        self.jogo = Jogo.objects.create(
            nome='Jogo Teste',
            cod='TEST123',
            cenario=self.cenario
        )
        
        self.empresa = Empresa.objects.create(
            nome='Empresa Teste',
            jogo=self.jogo
        )
        
    def test_valid_registration(self):
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'cpf': '123.456.789-09',
            'empresa': self.empresa.id,
            'codigo_de_jogo': self.jogo.cod
        }
        form = RegisterForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)
        
    def test_invalid_registration(self):
        form_data = {
            'username': 'testuser',
            'email': 'invalid-email',
            'password1': 'test',
            'password2': 'different',
            'cpf': '111.111.111-11'
        }
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())

class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('authentication:login')
        self.logout_url = reverse('authentication:logout')
        self.register_url = reverse('authentication:register')
        
        # Criar usuário para testes
        self.user = Usuario.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            cpf='123.456.789-09'
        )
        
        # Criar ou obter grupo Diretor
        self.grupo_diretor, _ = Group.objects.get_or_create(name='Diretor')
        
    def test_login_view(self):
        response = self.client.post(self.login_url, {
            'username': 'test@example.com',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect após login
        
    def test_logout_view(self):
        self.client.login(username='test@example.com', password='testpass123')
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 302)  # Redirect após logout
        
    def test_register_view(self):
        # Garantir que o grupo Diretor existe
        Group.objects.get_or_create(name='Diretor')
        
        # Criar cenário necessário
        insumo = Insumo.objects.create(
            nome='Insumo Teste',
            fornecedor='Fornecedor Teste'
        )
        produto = Produto.objects.create(nome='Produto Teste')
        produto.insumos.add(insumo)
        cenario = Cenario.objects.create(
            nome='Cenario Teste',
            produto=produto
        )
        
        # Criar jogo
        jogo = Jogo.objects.create(
            nome='Jogo Teste',
            cod='TEST123',
            cenario=cenario
        )
        
        # Criar empresa
        empresa = Empresa.objects.create(
            nome='Empresa Teste',
            jogo=jogo
        )
        
        # Testar registro com credenciais válidas
        response = self.client.post(self.register_url, {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'cpf': '529.982.247-25',
            'empresa': empresa.id,
            'codigo_de_jogo': jogo.cod
        })
        
        if response.status_code != 302:
            form = response.context['form']
            self.fail(f"Form errors: {form.errors.as_text()}")
            
        self.assertTrue(
            Usuario.objects.filter(email='new@example.com').exists()
        )

class AdminUserCreationFormTest(TestCase):
    def setUp(self):
        # Criar cenário necessário primeiro
        self.insumo = Insumo.objects.create(
            nome='Insumo Teste',
            fornecedor='Fornecedor Teste'
        )
        self.produto = Produto.objects.create(nome='Produto Teste')
        self.produto.insumos.add(self.insumo)
        self.cenario = Cenario.objects.create(
            nome='Cenario Teste',
            produto=self.produto
        )
        
        # Criar jogo com cenário
        self.jogo = Jogo.objects.create(
            nome='Jogo Teste',
            cod='TEST123',
            cenario=self.cenario
        )
        
        self.empresa = Empresa.objects.create(
            nome='Empresa Teste',
            jogo=self.jogo
        )
        
    def test_admin_user_creation(self):
        form_data = {
            'username': 'adminuser',
            'email': 'admin@example.com',
            'password1': 'adminpass123',
            'password2': 'adminpass123',
            'cpf': '123.456.789-09',
            'vinculo': 'mediador',
            'codigo_de_jogo': self.jogo.cod
        }
        form = AdminUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)
        
    def test_admin_user_creation_invalid(self):
        form_data = {
            'username': 'adminuser',
            'email': 'admin@example.com',
            'password1': 'adminpass123',
            'password2': 'adminpass123',
            'cpf': '123.456.789-09',
            'vinculo': 'diretor_com_jogo',
            'codigo_de_jogo': ''  # Código de jogo é requerido neste caso
        }
        form = AdminUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
