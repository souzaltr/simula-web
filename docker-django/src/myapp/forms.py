from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .models import Usuario


class UsuarioForm(forms.ModelForm):
    senha = forms.CharField(widget=forms.PasswordInput, min_length=6)

    class Meta:
        model = Usuario
        fields = ['nome', 'email', 'jogo', 'empresa', 'senha']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError("Email inválido.")
        return email

    def clean_senha(self):
        senha = self.cleaned_data.get('senha')
        if len(senha) < 6:
            raise ValidationError("A senha deve ter no mínimo 6 caracteres.")
        return senha

    def save(self, commit=True):
        usuario = super().save(commit=False)
        senha = self.cleaned_data.get('senha')
        if senha:
            usuario.set_password(senha)  # cria o hash da senha
        if commit:
            usuario.save()
        return usuario
