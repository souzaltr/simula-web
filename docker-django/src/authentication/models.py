import re
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from jogos.models import Jogo
from jogo_empresa.models import Empresa

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
        Empresa, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    codigo_de_jogo = models.ForeignKey(
        Jogo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email or self.username