from django.db import migrations

USERNAME = 'admin443'
EMAIL = 'admin@gmail.com'
PASSWORD = 'admin'
GROUP_NAME = 'Mediador'
CPF_DUMMY = '000.000.000-00'

def criar_usuario_admin(apps, schema_editor):
    User = apps.get_model('authentication', 'Usuario')
    Group = apps.get_model('auth', 'Group')

    if User.objects.filter(email=EMAIL).exists():
        print(f"\nUsuário com e-mail '{EMAIL}' já existe. Nenhuma ação foi tomada.")
        return

    try:
        grupo_mediador = Group.objects.get(name=GROUP_NAME)
    except Group.DoesNotExist:
        raise Exception(f"O grupo '{GROUP_NAME}' não foi encontrado. "
                        "Certifique-se de que a migração que cria este grupo foi executada antes.")

    admin_user = User.objects.create_superuser(
        username=USERNAME,
        email=EMAIL,
        password=PASSWORD,
        cpf=CPF_DUMMY
    )

    admin_user.groups.add(grupo_mediador)
    print(f"\nSuperusuário '{USERNAME}' criado e adicionado ao grupo '{GROUP_NAME}' com sucesso.")


def remover_usuario_admin(apps, schema_editor):
    User = apps.get_model('authentication', 'Usuario')
    try:
        admin_user = User.objects.get(email=EMAIL)
        admin_user.delete()
        print(f"\nUsuário com e-mail '{EMAIL}' removido com sucesso.")
    except User.DoesNotExist:
        print(f"\nUsuário com e-mail '{EMAIL}' não encontrado. Nenhuma ação foi tomada.")


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0003_auto_20250924_1953'),
    ]

    operations = [
        migrations.RunPython(criar_usuario_admin, remover_usuario_admin),
    ]