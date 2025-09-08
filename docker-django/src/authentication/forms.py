from django import forms
from django.contrib.auth.forms import UserCreationForm
from authentication.models import Usuario
from jogo_empresa.models import Empresa
from jogos.models import Jogo
from django.contrib.auth.models import Group
from django.db import transaction

class RegisterForm(UserCreationForm):
    username = forms.CharField(label="Nome de usuário", max_length=150)
    email = forms.EmailField(label="E-mail")
    password1 = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput,
        help_text="Sua senha deve conter pelo menos 8 caracteres."
    )
    password2 = forms.CharField(
        label="Confirmação de senha",
        widget=forms.PasswordInput,
        help_text="Digite a mesma senha novamente para confirmação."
    )
    
    cpf = forms.CharField(label="CPF", max_length=14)
    empresa = forms.ModelChoiceField(
        queryset=Empresa.objects.all(),
        label="Instituição ou empresa", 
        required=False,
        help_text="Se é estudante, informe sua instituição de ensino."
    )
    codigo_de_jogo = forms.CharField(
        label="Código de Jogo",
        required=False,
        help_text="Se ainda não possuir o código para a inscrição, você poderá digitá-lo posteriormente."
    )

    def clean_codigo_de_jogo(self):
        codigo = self.cleaned_data.get("codigo_de_jogo")
        if codigo:
            try:
                return Jogo.objects.get(cod=codigo)
            except Jogo.DoesNotExist:
                raise forms.ValidationError("Jogo não encontrado para este código.")
        return None
   
    class Meta:
        model = Usuario
        fields = ("username", "email", "password1", "password2", "cpf", "empresa", "codigo_de_jogo")

# Em seu forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.db import transaction
from .models import Usuario, Empresa

class AdminUserCreationForm(UserCreationForm):
    vinculo = forms.ChoiceField(
        label="Vínculo do Usuário",
        help_text="Selecione o papel e a empresa do novo usuário.",
        required=True,
    )

    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ("username", "email", "cpf", "codigo_de_jogo")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        choices = [
            ('', '---------'),
            ('mediador', 'Vincular como Mediador'),
            ('diretor', 'Vincular como Diretor (Sem vincular ao jogo)'),
            ('diretor_com_jogo', 'Vincular Apenas ao Jogo por Enquanto'),
        ]

        empresas = Empresa.objects.all().order_by('nome')
        for empresa in empresas:
            choices.append((f'empresa_{empresa.pk}', f'{empresa.pk}# {empresa.nome}'))

        self.fields['vinculo'].choices = choices

    def clean(self):
        cleaned_data = super().clean()
        
        vinculo = cleaned_data.get("vinculo")
        codigo_de_jogo = cleaned_data.get("codigo_de_jogo")

        if vinculo == 'diretor_com_jogo' and not codigo_de_jogo:
            self.add_error(
                'codigo_de_jogo', 
                "Você deve selecionar um jogo para criar um usuário com este vínculo."
            )

        if vinculo == 'diretor':
            cleaned_data['codigo_de_jogo'] = None
            
        return cleaned_data

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        
        vinculo_selecionado = self.cleaned_data.get("vinculo")

        try:
            diretor_group = Group.objects.get(name='Diretor')
            mediador_group = Group.objects.get(name='Mediador')
        except Group.DoesNotExist as e:
            raise ValueError(f"O grupo '{e.args[0].split()[1]}' não foi encontrado. Crie os grupos 'Diretor' e 'Mediador' no Admin do Django.") from e
        
        if vinculo_selecionado == 'mediador':
            user.empresa = None
            if commit:
                user.save()
                user.groups.add(mediador_group)

        elif vinculo_selecionado == 'diretor':
            user.empresa = None
            if commit:
                user.save()
                user.groups.add(diretor_group)

        elif vinculo_selecionado == 'diretor_com_jogo':
            user.empresa = None
            if commit:
                user.save()
                user.groups.add(diretor_group)

        elif vinculo_selecionado.startswith('empresa_'):
            empresa_id = int(vinculo_selecionado.split('_')[1])
            try:
                empresa_obj = Empresa.objects.get(pk=empresa_id)
                user.empresa = empresa_obj
                if commit:
                    user.save()
                    user.groups.add(diretor_group)
            except Empresa.DoesNotExist:
                self.add_error('vinculo', 'A empresa selecionada não é mais válida.')
                return user
        
        if commit:
            user.save()
            self.save_m2m() 

        return user
    
class AdminUserEditForm(forms.ModelForm):
    vinculo = forms.ChoiceField(
        label="Vínculo do Usuário",
        required=True,
    )
    
    codigo_de_jogo = forms.ModelChoiceField(
        queryset=Jogo.objects.all(),
        label="Jogo",
        required=False,
        help_text="Selecione um jogo se o vínculo for 'Apenas ao Jogo' ou à uma empresa."
    )

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'cpf', 'vinculo', 'codigo_de_jogo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        choices = [
            ('', '---------'),
            ('mediador', 'Vincular como Mediador'),
            ('diretor', 'Vincular como Diretor'),
            ('diretor_com_jogo', 'Vincular Apenas ao Jogo'),
        ]
        empresas = Empresa.objects.all().order_by('nome')
        for empresa in empresas:
            choices.append((f'empresa_{empresa.pk}', f'Vincular à Empresa: {empresa.nome}'))
            
        self.fields['vinculo'].choices = choices

        if self.instance and self.instance.pk:
            user = self.instance
            initial_vinculo = ''
            
            if user.groups.filter(name='Mediador').exists():
                initial_vinculo = 'mediador'
            elif user.empresa:
                initial_vinculo = f'empresa_{user.empresa.pk}'
            elif user.codigo_de_jogo:
                initial_vinculo = 'diretor_com_jogo'
                self.fields['codigo_de_jogo'].initial = user.codigo_de_jogo
            else:
                initial_vinculo = 'diretor'
            
            self.fields['vinculo'].initial = initial_vinculo

    def clean(self):
        cleaned_data = super().clean()
        vinculo = cleaned_data.get("vinculo")
        codigo_de_jogo = cleaned_data.get("codigo_de_jogo")

        if vinculo == 'diretor_com_jogo' and not codigo_de_jogo:
            self.add_error(
                'codigo_de_jogo', 
                "Você deve selecionar um jogo para este tipo de vínculo."
            )
        
        if vinculo in ['mediador', 'diretor']:
            cleaned_data['codigo_de_jogo'] = None
            
        return cleaned_data

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        
        vinculo_selecionado = self.cleaned_data.get("vinculo")
        codigo_de_jogo_selecionado = self.cleaned_data.get("codigo_de_jogo")

        try:
            diretor_group = Group.objects.get(name='Diretor')
            mediador_group = Group.objects.get(name='Mediador')
        except Group.DoesNotExist as e:
            raise ValueError(f"O grupo '{e.args[0].split()[1]}' não foi encontrado.") from e

        user.empresa = None
        user.codigo_de_jogo = codigo_de_jogo_selecionado
        user.groups.clear()

        if vinculo_selecionado == 'mediador':
            user.groups.add(mediador_group)
            
        elif vinculo_selecionado == 'diretor':
            user.groups.add(diretor_group)

        elif vinculo_selecionado == 'diretor_com_jogo':
            user.groups.add(diretor_group)

        elif vinculo_selecionado.startswith('empresa_'):
            empresa_id = int(vinculo_selecionado.split('_')[1])
            user.empresa = Empresa.objects.get(pk=empresa_id)
            user.groups.add(diretor_group)
        
        if commit:
            user.save()

        return user

from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from authentication.models import Usuario
from jogo_empresa.models import Empresa

class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Usuario
        # Campos que o usuário pode editar no perfil
        fields = ['username', 'email', 'cpf']
        labels = {
            'username': 'Nome de Usuário',
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'email': 'E-mail',
            'cpf': 'CPF',
        }

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Exemplo de como adicionar classes CSS aos campos
        self.fields['old_password'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'})