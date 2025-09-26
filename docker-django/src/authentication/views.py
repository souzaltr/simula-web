from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.core.paginator import Paginator
from django.db.models import Q

from authentication.forms import RegisterForm, AdminUserCreationForm, AdminUserEditForm
from authentication.decorators import group_required
from authentication.models import Usuario
from jogos.models import Jogo


def redirect_based_on_group(request):
    """
    Redireciona o usuário com base na sua appartença ao grupo 'Mediador'.
    - Se for do grupo 'Mediador', vai para a dashboard de jogos.
    - Caso contrário, vai para a home geral.
    """

    if request.user.is_authenticated and request.user.groups.filter(name='Mediador').exists():
        return redirect('jogo_empresa:jogos_crud')
    else:
        return redirect('general_home')

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"Você agora está logado como {username}.")
                return redirect_based_on_group(request)
            else:
                messages.error(request, "Usuário ou senha inválidos.")
        else:
            messages.error(request, "Usuário ou senha inválidos.")
    else:
        form = AuthenticationForm()
        
    return render(request, "auth/login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "Você saiu da sua conta com sucesso.")
    return redirect("authentication:login")

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            try:
                group = Group.objects.get(name='Diretor')
                user.groups.add(group)
            except Group.DoesNotExist:
                messages.error(request, "O grupo 'Diretor' não foi encontrado.")
                user.delete() 
                return redirect('authentication:register')

            login(request, user)
            messages.success(request, "Registro bem-sucedido!")
            return redirect_based_on_group(request)
        else:
            messages.error(request, "Falha no registro. Verifique as informações.")
    else:
        form = RegisterForm()
    
    return render(request, "auth/register.html", {"form": form})


@group_required(['Mediador'])
def user_management_view(request):
    # MUDANÇA COMEÇA AQUI ------------------------------------------------------------------------------------------------------------------------
    codigo_jogo_str = request.GET.get('jogo', None)
    search_query = request.GET.get('q', None)
    filter_option = request.GET.get('filter', None)

    other_game_code = request.GET.get('other_game_code', None)
    all_games = Jogo.objects.all().order_by('nome')
    # MUDANÇA TERMINA AQUI ------------------------------------------------------------------------------------------------------------------------
    jogo_selecionado = None

    # Verifica se o usuário logado é um mediador.
    usuario = request.user
    is_mediador = False
    if usuario.is_authenticated: is_mediador = usuario.groups.filter(name="Mediador").exists()

    # Baseado no Query-Param 'jogo' pega o jogo no banco de dados.
    if codigo_jogo_str:
        try:
            jogo_selecionado = Jogo.objects.get(cod=codigo_jogo_str)
        except Jogo.DoesNotExist:
            messages.warning(request, f"O jogo com código '{codigo_jogo_str}' não foi encontrado.")

    # --- FORMULÁRIO ---
    if request.method == "POST":
        post_data = request.POST.copy()

        # Se um jogo foi pré-selecionado pela URL, seu valor não veio no POST.
        # Usa o jogo do query-param ao invés do selecionado.
        if jogo_selecionado:
            post_data['codigo_de_jogo'] = jogo_selecionado.cod

        # Instancia o formulário com os dados completos (incluindo o jogo)
        form = AdminUserCreationForm(post_data)
        
        if form.is_valid():
            form.save()
            messages.success(request, "Novo usuário criado com sucesso!")

            query_params = request.GET.urlencode()
            base_url = reverse('authentication:user_management')
            url = f"{base_url}?{query_params}" if query_params else base_url
            return redirect(url)
        else:
            messages.error(request, "Erro ao criar o usuário. Por favor, corrija os campos.")

    else: # GET
        initial_data = {}

        # Basicamente seleciona no SELECT o jogo que está no Query-Param.
        if jogo_selecionado:
            initial_data['codigo_de_jogo'] = jogo_selecionado.cod

        form = AdminUserCreationForm(initial=initial_data)

    # MUDANÇA COMEÇA AQUI ------------------------------------------------------------------------------------------------------------------------
    lista_de_usuarios = Usuario.objects.all().order_by('username')

    if filter_option:
        if filter_option == 'users_in_game':
            if jogo_selecionado:
                lista_de_usuarios = lista_de_usuarios.filter(codigo_de_jogo=jogo_selecionado)
            else:
                messages.warning(request, f"Nenhum Jogo Selecionado.")
                lista_de_usuarios = []

        elif filter_option == 'users_to_add_to_game':
            lista_de_usuarios = lista_de_usuarios.filter(codigo_de_jogo__isnull=True)

        elif filter_option == 'users_in_other_games':
            if other_game_code:
                try:
                    other_game_obj = Jogo.objects.get(cod=other_game_code)
                    lista_de_usuarios = lista_de_usuarios.filter(codigo_de_jogo=other_game_obj)
                except Jogo.DoesNotExist:
                    messages.warning(request, f"O jogo com código '{other_game_code}' para o filtro não foi encontrado.")
            elif jogo_selecionado:
                lista_de_usuarios = lista_de_usuarios.filter(codigo_de_jogo__isnull=False).exclude(codigo_de_jogo=jogo_selecionado)
            else:
                lista_de_usuarios = lista_de_usuarios.filter(codigo_de_jogo__isnull=False)

    if search_query:
        lista_de_usuarios = lista_de_usuarios.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(cpf__icontains=search_query)
        )

    query_dict = request.GET.copy()
    if 'page' in query_dict:
        del query_dict['page']
    pagination_query_params = query_dict.urlencode()
    # MUDANÇA TERMINA AQUI ------------------------------------------------------------------------------------------------------------------------

    # --- PAGINAÇÃO ---
    paginator = Paginator(lista_de_usuarios, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # --- CONTEXTO ---
    context = {
        'form': form,
        'page_obj': page_obj,
        'jogo_selecionado': jogo_selecionado,
        # MUDANÇA COMEÇA AQUI ------------------------------------------------------------------------------------------------------------------------
        'search_query': search_query,
        'is_general': True,
        'is_mediador': is_mediador,
        'pagination_query_params': pagination_query_params,
        'all_games': all_games,
        'other_game_code': other_game_code,
        # MUDANÇA TERMINA AQUI ------------------------------------------------------------------------------------------------------------------------
    }
    return render(request, "users/user_management.html", context)


@group_required(['Mediador'])
def user_edit_view(request, user_id):
    usuario = request.user
    is_mediador = False

    if usuario.is_authenticated:
        is_mediador = usuario.groups.filter(name="Mediador").exists()

    user_to_edit = get_object_or_404(Usuario, pk=user_id)
    if request.method == 'POST':
        form = AdminUserEditForm(request.POST, instance=user_to_edit)
        if form.is_valid():
            form.save()
            messages.success(request, f"Usuário '{user_to_edit.username}' atualizado com sucesso!")
            return redirect('authentication:user_management')
    else:
        form = AdminUserEditForm(instance=user_to_edit)

    selected_vinculo = form.data.get('vinculo', form.initial.get('vinculo'))
    
    need_game = False
    if selected_vinculo and selected_vinculo not in ['mediador', 'diretor']:
        need_game = True

    return render(request, 'users/user_edit.html', {'form': form, 'user_to_edit': user_to_edit, 'is_mediador': is_mediador, 'need_game': need_game})


@group_required(['Mediador'])
def user_delete_view(request, user_id):
    usuario = request.user
    is_mediador = False

    if usuario.is_authenticated:
        is_mediador = usuario.groups.filter(name="Mediador").exists()

    user_to_delete = get_object_or_404(Usuario, pk=user_id)
    if request.method == 'POST':
        username = user_to_delete.username
        user_to_delete.delete()
        messages.success(request, f"Usuário '{username}' deletado com sucesso!")
        return redirect('authentication:user_management')

    return render(request, 'users/user_delete_confirm.html', {'user_to_delete': user_to_delete, 'is_mediador': is_mediador})

from authentication.forms import UserProfileUpdateForm, CustomPasswordChangeForm
@login_required 
def profile_edit_view(request):
    # Instanciamos os formulários
    profile_form = UserProfileUpdateForm(instance=request.user)
    password_form = CustomPasswordChangeForm(user=request.user)
    usuario = request.user
    is_mediador = False

    if usuario.is_authenticated:
        is_mediador = usuario.groups.filter(name="Mediador").exists()

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            profile_form = UserProfileUpdateForm(request.POST, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                return redirect('authentication:profile_edit')
        
        elif 'change_password' in request.POST:
            password_form = CustomPasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                return redirect('authentication:profile_edit')
            else:
                messages.error(request, 'Erro ao alterar a senha. Por favor, corrija os erros abaixo.')

    context = {
        'profile_form': profile_form,
        'password_form': password_form,
        'is_mediador': is_mediador
    }
    
    return render(request, 'auth/profile_edit.html', context)
