from django.db import migrations

def criar_grupos(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')

    Group.objects.get_or_create(name='Diretor')
    Group.objects.get_or_create(name='Mediador')

def reverter_grupos(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name__in=['Diretor', 'Mediador']).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_auto_20250924_1952'),
    ]

    operations = [
        migrations.RunPython(criar_grupos, reverter_grupos),
    ]