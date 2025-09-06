from django.views.generic import TemplateView
from .tasks import show_hello_world
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse

from django.core.exceptions import ValidationError

from jogos.models import Jogo
from myapp.models import Empresa
from cenarios.models import Cenario

def pagina_home(request):
    contexto = {"nome": "Alessandro"}
    return render(request, 'home.html', contexto)

def jogos_teste(request):
    return render(request, 'empresas/empresas.html')

def jogos_crud(request):

    if request.method == 'POST':
        action = (request.POST.get('action') or '').strip()

        if action == 'create':
            nome = (request.POST.get('nome') or '').strip()
            cenario_id = request.POST.get('cenario_id')
            
            jogo = Jogo(nome=nome)

            if cenario_id:
                jogo.cenario= get_object_or_404(Cenario, pk=cenario_id)
            
            try:
                jogo.save()
                return redirect(reverse('myapp:jogos_crud'))
            except ValidationError as e:
                filtro_campo = {}
                for campo, msgs in e.message_dict.items():
                    filtro_campo[campo] = [msg for msg in msgs if msg != 'This field cannot be blank.']
                
                cenario_nome = ''
                if cenario_id:
                    try:
                        cenario_obj = Cenario.objects.get(pk=cenario_id)
                        cenario_nome = cenario_obj.nome
                    except Cenario.DoesNotExist:
                        cenario_nome = ''

                jogos = Jogo.objects.select_related('cenario').order_by('nome')
                cenarios = Cenario.objects.select_related('produto').order_by('nome')
                return render(request, 'jogos/jogos.html', {
                'jogos': jogos,
                'cenarios': cenarios,
                'errors': filtro_campo, 
                'form_data': {'nome': nome, 'cenario_id': cenario_id, 'cenario_nome': cenario_nome}})
        
        elif action == 'update':
            pk = request.POST.get('id')
            jogo = get_object_or_404(Jogo, pk=pk)
            nome = (request.POST.get('nome') or jogo.nome).strip()
            jogo.nome = nome

            try:
                jogo.full_clean(exclude=['cenario'])
                jogo.save()
                return redirect(f"{reverse('myapp:jogos_crud')}?edit={jogo.pk}")
            except ValidationError as e:
                erros={}
                if 'nome' in e.message_dict:
                     msgs = [msg for msg in e.message_dict['nome'] if msg != 'This field cannot be blank.']
                     erros['nome'] = msgs

                jogos= Jogo.objects.select_related('cenario').order_by('nome')
                return render(request, 'jogos/jogos.html', {
                    'jogos': jogos,
                    'jogo_edit': jogo,
                    'errors': erros,})
                
        elif action == 'delete':
            pk = request.POST.get('id')
            jogo = get_object_or_404(Jogo, pk=pk)
            jogo.delete()
            return redirect(reverse('myapp:jogos_crud'))
        
        elif action == 'alterar_status':
            selecionados = request.POST.getlist('jogos_selecionados')
            valid_ids = []
            for id_str in selecionados:
                if id_str.isdigit():
                    valid_ids.append(int(id_str))
            
            if valid_ids:
                jogos = Jogo.objects.filter(id__in=valid_ids)
                for jogo in jogos:
                    jogo.status = Jogo.INATIVO if jogo.status == Jogo.ATIVO else Jogo.ATIVO
                    jogo.save()
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
            empresa= Empresa(nome=nome, jogo=jogo)
            try:
                empresa.full_clean()
                empresa.save()
                return redirect(reverse('myapp:empresas_crud', args=[jogo.id]))
            except ValidationError as e:
                erros={}
                if 'nome' in e.message_dict:
                     msgs = [msg for msg in e.message_dict['nome'] if msg != 'This field cannot be blank.']
                     erros['nome'] = msgs

                
                empresas = Empresa.objects.filter(jogo=jogo).order_by('nome')
                return render(request, 'empresas/empresas.html', {
                    'jogo': jogo,
                    'empresas': empresas,
                    'empresa_edit': None,
                    'errors': erros,
                    'form_data': {'nome': nome},})
                 
        elif action == 'update':
            emp_id = request.POST.get('id')
            empresa = get_object_or_404(Empresa, pk=emp_id, jogo=jogo)
            nome = (request.POST.get('nome') or '').strip()
            empresa.nome = nome

            try:
                empresa.full_clean()
                empresa.save()
                return redirect(f"{reverse('myapp:empresas_crud', args=[jogo.id])}?edit={empresa.id}")
            except ValidationError as e:
                erros={}
                if 'nome' in e.message_dict:
                    msgs = [msg for msg in e.message_dict['nome'] if msg != 'This field cannot be blank.']
                    erros['nome'] = msgs

                empresas = Empresa.objects.filter(jogo=jogo).order_by('nome')
                return render(request, 'empresas/empresas.html', {
                    'jogo': jogo,
                    'empresas': empresas,
                    'empresa_edit': empresa,
                    'errors': erros,
                    'form_data': {'nome': nome},
                })
        
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

