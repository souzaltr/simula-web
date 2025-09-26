import re
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
def validate_cpf(value):
    cpf = re.sub(r'\D', '', value)

    if len(cpf) != 11 or not cpf.isdigit():
        raise ValidationError(
            _('%(value)s não é um número de CPF válido.'),
            params={'value': value},
        )
    
    if re.match(r'(\d)\1{10}', cpf):
        raise ValidationError(
            _('CPF com todos os dígitos iguais não é válido.'),
            params={'value': value},
        )
        
    # Primeira etapa de validação
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    digito1 = (soma * 10) % 11
    if digito1 == 10:
        digito1 = 0
        
    if str(digito1) != cpf[9]:
        raise ValidationError(
            _('%(value)s não é um CPF válido.'),
            params={'value': value},
        )
        
    # Segunda etapa de validação
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    digito2 = (soma * 10) % 11
    if digito2 == 10:
        digito2 = 0
        
    if str(digito2) != cpf[10]:
        raise ValidationError(
            _('%(value)s não é um CPF válido.'),
            params={'value': value},
        )

class Usuario(AbstractUser):
    
    # O AbstractUser já inclui: username, first_name, last_name, email, password, etc.

    email = models.EmailField(unique=True)
    
    cpf = models.CharField(
        _("CPF"),
        max_length=14,
        unique=True,
        validators=[validate_cpf],
        help_text=_("Formato exigido: 000.000.000-00 ou apenas números.")
    )
    
    empresa = models.ForeignKey(
        'jogo_empresa.Empresa', 
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    codigo_de_jogo = models.ForeignKey(
        'jogos.Jogo',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usuarios'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email or self.username