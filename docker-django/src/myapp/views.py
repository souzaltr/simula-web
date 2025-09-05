from django import get_version
from django.views.generic import TemplateView
from .tasks import show_hello_world

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from django.http import HttpResponse

from .models import DemoModel, Jogo

def pagina_home(request):
    contexto = {"nome": "Alessandro"}
    return render(request, 'home.html', contexto)

def jogos_teste(request):
    return render(request, 'jogos/jogos.html')

def jogos_crud(request):
    if request.method == 'POST':
        action = (request.POST.get('action') or '').strip()

        if action == 'create':
            nome = (request.POST.get('nome') or '').strip()
            cenario = (request.POST.get('cenario') or '').strip()
            periodo_raw = request.POST.get('periodo_atual') or '1'
            try:
                periodo_atual = int(periodo_raw)
            except ValueError:
                periodo_atual = 1
            status = request.POST.get('status') == 'on'

            jogo = Jogo(nome=nome, cenario=cenario, periodo_atual=periodo_atual, status=status)
            if not jogo.codigo and hasattr(jogo, 'gerar_codigo'):
                jogo.codigo = jogo.gerar_codigo()
            jogo.save()
            return redirect(reverse('myapp:jogos_crud'))

        elif action == 'update':
            pk = request.POST.get('id')
            jogo = get_object_or_404(Jogo, pk=pk)

            jogo.nome = (request.POST.get('nome') or jogo.nome).strip()
            jogo.cenario = (request.POST.get('cenario') or '').strip()

            periodo_raw = request.POST.get('periodo_atual')
            if periodo_raw:
                try:
                    jogo.periodo_atual = int(periodo_raw)
                except ValueError:
                    pass

            jogo.status = request.POST.get('status') == 'on'
            jogo.save()
            return redirect(f"{reverse('myapp:jogos_crud')}?edit={jogo.pk}")

        elif action == 'delete':
            pk = request.POST.get('id')
            jogo = get_object_or_404(Jogo, pk=pk)
            jogo.delete()
            return redirect(reverse('myapp:jogos_crud'))

        return redirect(reverse('myapp:jogos_crud'))

    edit_id = request.GET.get('edit')
    jogo_edit = Jogo.objects.filter(pk=edit_id).first() if edit_id else None
    jogos = Jogo.objects.order_by('nome')
    return render(request, 'jogos/jogos.html', {'jogos': jogos, 'jogo_edit': jogo_edit})


    

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
