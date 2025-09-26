
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from django.core.exceptions import ValidationError
from django.http import HttpResponseForbidden


from jogos.models import Jogo
from jogo_empresa.models import Empresa
from cenarios.models import Cenario

from authentication.decorators import group_required

def pagina_home(request):
    contexto = {"nome": "Alessandro"}
    return render(request, 'home.html', contexto)

#filtragem e ordenação jogo
def build_jogos_queryset(request):
    q = (request.GET.get("q") or "").strip() #lê o termo digitado e tira espaços (filtrar da lupa)
    sort = (request.GET.get("sort") or "asc").lower()   # 'asc' ou 'desc' -> diração da ordenação

    qs = Jogo.objects #select_related('cenario') -> opcional
    if q:
        qs = qs.filter(nome__icontains=q) # traz só os jogos cujo nome contém o termo 'q'

    order = "nome" if sort == "asc" else "-nome" #obs.: esse '-nome' significa descendente no Django
    return qs.order_by(order), q, sort

#filtragem e ordenação empresa
def build_empresas_queryset(request, jogo):
    q = (request.GET.get("q") or "").strip()          # termo da busca
    sort = (request.GET.get("sort") or "asc").lower() # 'asc' ou 'desc'

    qs = Empresa.objects.filter(jogo=jogo)
    if q:
        qs = qs.filter(nome__icontains=q)

    order = "nome" if sort == "asc" else "-nome"
    return qs.order_by(order), q, sort

@group_required(['Mediador'])
def jogos_crud(request):
    if request.method == 'POST':
        action = (request.POST.get('action') or '').strip()

        if action == 'create':
            nome = (request.POST.get('nome') or '').strip()
            cenario_id = request.POST.get('cenario_id')

            jogo = jogo = Jogo(nome=nome, criador=request.user)
            if cenario_id:
                jogo.cenario = get_object_or_404(Cenario, pk=cenario_id)

            try:
                jogo.save()
                # após criar, volte respeitando q/sort atuais (se quiser preservar)
                return redirect(reverse('jogo_empresa:jogos_crud'))
            except ValidationError as e:
                filtro_campo = {campo: [msg for msg in msgs if msg != 'This field cannot be blank.']
                                for campo, msgs in e.message_dict.items()}

                cenario_nome = ''
                if cenario_id:
                    try:
                        cenario_obj = Cenario.objects.get(pk=cenario_id)
                        cenario_nome = cenario_obj.nome
                    except Cenario.DoesNotExist:
                        pass

                jogos, q, sort = build_jogos_queryset(request)
                cenarios = Cenario.objects.select_related('produto').order_by('nome')
                return render(request, 'jogos/jogos.html', {
                    'jogos': jogos,
                    'cenarios': cenarios,
                    'errors': filtro_campo,
                    'form_data': {'nome': nome, 'cenario_id': cenario_id, 'cenario_nome': cenario_nome},
                    'q': q, 'sort': sort,
                })

        elif action == 'update':
            pk = request.POST.get('id')
            jogo = get_object_or_404(Jogo, pk=pk)
            if request.user != jogo.criador and not request.user.is_superuser:
                return HttpResponseForbidden("Você não tem permissão para alterar esse jogo.")
            
            nome = (request.POST.get('nome') or jogo.nome).strip()
            jogo.nome = nome

            try:
                jogo.full_clean(exclude=['cenario'])
                jogo.save()
                return redirect(f"{reverse('jogo_empresa:jogos_crud')}?edit={jogo.pk}")
            except ValidationError as e:
                erros = {}
                if 'nome' in e.message_dict:
                    erros['nome'] = [msg for msg in e.message_dict['nome'] if msg != 'This field cannot be blank.']

                jogos, q, sort = build_jogos_queryset(request)
                return render(request, 'jogos/jogos.html', {
                    'jogos': jogos,
                    'jogo_edit': jogo,
                    'errors': erros,
                    'q': q, 'sort': sort,
                })

        elif action == 'delete':
            pk = request.POST.get('id')
            jogo = get_object_or_404(Jogo, pk=pk)
            if request.user != jogo.criador and not request.user.is_superuser:
                return HttpResponseForbidden("Você não tem permissão para deletar esse jogo.")

            jogo.delete()
            return redirect(reverse('jogo_empresa:jogos_crud'))

        elif action == 'alterar_status':
            selecionados = request.POST.getlist('jogos_selecionados')
            valid_ids = [int(x) for x in selecionados if str(x).isdigit()]
            if valid_ids:
                for jogo in Jogo.objects.filter(id__in=valid_ids):
                    if request.user != jogo.criador and not request.user.is_superuser:
                        return HttpResponseForbidden(f"Você não tem permissão para alterar o jogo '{jogo.nome}'.")
                    
                    jogo.status = Jogo.INATIVO if jogo.status == Jogo.ATIVO else Jogo.ATIVO
                    jogo.save()
            return redirect(reverse('jogo_empresa:jogos_crud'))

    # GET
    edit_id = request.GET.get('edit')
    jogo_edit = Jogo.objects.filter(pk=edit_id).select_related('cenario').first() if edit_id else None

    jogos, q, sort = build_jogos_queryset(request)
    cenarios = Cenario.objects.select_related('produto').order_by('nome')

    if request.user.groups.filter(name='Mediador').exists() and not request.user.is_superuser:
        jogos = jogos.filter(criador=request.user) 
    
        if jogo_edit and jogo_edit.criador != request.user:
            jogo_edit = None  

    return render(request, 'jogos/jogos.html', {
        'jogos': jogos,
        'jogo_edit': jogo_edit,
        'cenarios': cenarios,
        'q': q, 'sort': sort,   # <- manda pra template
    })

@group_required(['Mediador'])
def empresas_crud(request, jogo_id):
    jogo = get_object_or_404(Jogo, pk=jogo_id)

    if request.user != jogo.criador and not request.user.is_superuser:
        return HttpResponseForbidden("Você não tem permissão para gerenciar empresas deste jogo.")

    if request.method == 'POST':
        action = (request.POST.get('action') or '').strip()

        if action == 'create':
            nome = (request.POST.get('nome') or '').strip()
            empresa = Empresa(nome=nome, jogo=jogo, criador=request.user)
            try:
                empresa.full_clean()
                empresa.save()
                return redirect(reverse('jogo_empresa:empresas_crud', args=[jogo.id]))
            except ValidationError as e:
                erros = {}
                if 'nome' in e.message_dict:
                    msgs = [msg for msg in e.message_dict['nome'] if msg != 'This field cannot be blank.']
                    erros['nome'] = msgs

                # <<< usa o helper para manter q/sort no reload
                empresas, q, sort = build_empresas_queryset(request, jogo)
                return render(request, 'empresas/empresas.html', {
                    'jogo': jogo,
                    'empresas': empresas,
                    'empresa_edit': None,
                    'errors': erros,
                    'form_data': {'nome': nome},
                    'q': q, 'sort': sort,
                })

        elif action == 'update':
            emp_id = request.POST.get('id')
            empresa = get_object_or_404(Empresa, pk=emp_id, jogo=jogo)
            nome = (request.POST.get('nome') or '').strip()
            empresa.nome = nome

            try:
                empresa.full_clean()
                empresa.save()
                return redirect(f"{reverse('jogo_empresa:empresas_crud', args=[jogo.id])}?edit={empresa.id}")
            except ValidationError as e:
                erros = {}
                if 'nome' in e.message_dict:
                    msgs = [msg for msg in e.message_dict['nome'] if msg != 'This field cannot be blank.']
                    erros['nome'] = msgs

                # <<< usa o helper para manter q/sort no reload
                empresas, q, sort = build_empresas_queryset(request, jogo)
                return render(request, 'empresas/empresas.html', {
                    'jogo': jogo,
                    'empresas': empresas,
                    'empresa_edit': empresa,
                    'errors': erros,
                    'form_data': {'nome': nome},
                    'q': q, 'sort': sort,
                })

        elif action == 'delete':
            emp_id = request.POST.get('id')
            empresa = get_object_or_404(Empresa, pk=emp_id, jogo=jogo)
            empresa.delete()
            return redirect(reverse('jogo_empresa:empresas_crud', args=[jogo.id]))

        return redirect(reverse('jogo_empresa:empresas_crud', args=[jogo.id]))

    # GET normal
    edit_id = request.GET.get('edit')
    empresa_edit = Empresa.objects.filter(pk=edit_id, jogo=jogo).first() if edit_id else None

    # <<< usa o helper também no GET
    empresas, q, sort = build_empresas_queryset(request, jogo)
    return render(request, 'empresas/empresas.html', {
        'jogo': jogo,
        'empresas': empresas,
        'empresa_edit': empresa_edit,
        'q': q, 'sort': sort,
    })