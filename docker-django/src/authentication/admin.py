from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from authentication.models import Usuario

class CustomUserAdmin(UserAdmin):
    model = Usuario
    # Adiciona os novos campos à tela de edição do usuário no admin
    fieldsets = UserAdmin.fieldsets + (
        ('Campos Personalizados', {'fields': ('empresa', 'cpf', 'codigo_de_jogo')}),
    )
    # Adiciona os novos campos à tela de criação de usuário no admin
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('empresa', 'cpf', 'codigo_de_jogo')}),
    )
    # Adiciona os campos à visualização em lista no admin
    list_display = ['username', 'email', 'empresa', 'cpf', 'is_staff']


admin.site.register(Usuario, CustomUserAdmin)