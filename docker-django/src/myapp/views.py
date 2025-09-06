from django import get_version
from django.views.generic import TemplateView
from .tasks import show_hello_world

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from django.http import HttpResponse

from jogos.models import Jogo
from myapp.models import Empresa

from cenarios.models import Cenario

import random

def pagina_home(request):
    contexto = {"nome": "Alessandro"}
    return render(request, 'home.html', contexto)

def jogos_teste(request):
    return render(request, 'empresas/empresas.html')

def jogos_crud(request):
    def gerar_cod_unico():
        while True:
            codigo = str(random.randint(100000000, 999999999))
            if not Jogo.objects.filter(cod=codigo).exists():
                return codigo

    if request.method == 'POST':
        action = (request.POST.get('action') or '').strip()

        if action == 'create':
            nome = (request.POST.get('nome') or '').strip()
            cenario_id = request.POST.get('cenario_id')
            cenario = get_object_or_404(Cenario, pk=cenario_id)
            jogo = Jogo(nome=nome, cenario=cenario, cod=gerar_cod_unico())
            jogo.save()
            return redirect(reverse('myapp:jogos_crud'))

        elif action == 'update':
            pk = request.POST.get('id')
            jogo = get_object_or_404(Jogo, pk=pk)
            nome = (request.POST.get('nome') or jogo.nome).strip()
            cenario_id = request.POST.get('cenario_id')
            if cenario_id:
                cenario = get_object_or_404(Cenario, pk=cenario_id)
                jogo.cenario = cenario
            jogo.nome = nome
            jogo.save()
            return redirect(f"{reverse('myapp:jogos_crud')}?edit={jogo.pk}")

        elif action == 'delete':
            pk = request.POST.get('id')
            jogo = get_object_or_404(Jogo, pk=pk)
            jogo.delete()
            return redirect(reverse('myapp:jogos_crud'))

        return redirect(reverse('myapp:jogos_crud'))

    edit_id = request.GET.get('edit')
    jogo_edit = Jogo.objects.filter(pk=edit_id).select_related('cenario').first() if edit_id else None
    jogos = Jogo.objects.select_related('cenario').order_by('nome')
    cenarios = Cenario.objects.select_related('produto').order_by('nome')
    return render(request, 'jogos/jogos.html', {
        'jogos': jogos,
        'jogo_edit': jogo_edit,
        'cenarios': cenarios,
    })

def empresas_crud(request, jogo_id):
    jogo = get_object_or_404(Jogo, pk=jogo_id)

    if request.method == 'POST':
        action = (request.POST.get('action') or '').strip()
        if action == 'create':
            nome = (request.POST.get('nome') or '').strip()
            if nome:
                Empresa.objects.create(nome=nome, jogo=jogo)
            return redirect(reverse('myapp:empresas_crud', args=[jogo.id]))
        elif action == 'update':
            emp_id = request.POST.get('id')
            empresa = get_object_or_404(Empresa, pk=emp_id, jogo=jogo)
            empresa.nome = (request.POST.get('nome') or empresa.nome).strip()
            empresa.full_clean()
            empresa.save()
            return redirect(f"{reverse('myapp:empresas_crud', args=[jogo.id])}?edit={empresa.id}")
        elif action == 'delete':
            emp_id = request.POST.get('id')
            empresa = get_object_or_404(Empresa, pk=emp_id, jogo=jogo)
            empresa.delete()
            return redirect(reverse('myapp:empresas_crud', args=[jogo.id]))
        return redirect(reverse('myapp:empresas_crud', args=[jogo.id]))

    edit_id = request.GET.get('edit')
    empresa_edit = Empresa.objects.filter(pk=edit_id, jogo=jogo).first() if edit_id else None
    empresas = Empresa.objects.filter(jogo=jogo).order_by('nome')
    return render(request, 'empresas/empresas.html', {'jogo': jogo, 'empresas': empresas, 'empresa_edit': empresa_edit})

    

class ShowHelloWorld(TemplateView):
    template_name = 'hello_world.html'

    def get(self, *args, **kwargs):
        show_hello_world.apply()
        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['demo_content'] = DemoModel.objects.all()
        context['version'] = get_version()
        return context
