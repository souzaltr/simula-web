from django.shortcuts import render,redirect,get_object_or_404
from .models import Insumo,Cenario,Produto 
from .forms import InsumoForm,ProdutoForm,CenarioForm
from django.http import HttpRequest
from django.contrib import messages
from jogos.models import Jogo
from django.db.models import Q

from authentication.decorators import group_required


# filtragem/busca na tela principal 
@group_required(['Mediador'])
def build_insumos_queryset(request):
    #adptar aqui pra somente itens que o proprio mediador criou 
    q = (request.GET.get("q_insumo")or"").strip()
    sort = (request.GET.get("sort_insumo") or "asc").lower()

    qs = Insumo.objects.filter(criador=request.user)

    if q:
        qs=qs.filter(Q(nome__icontains=q) | Q(fornecedor__icontains=q)) # busca pelo nome do insuno e do fornecedor

    order = "nome" if sort == "asc" else "-nome"
    return qs.order_by(order), q, sort

@group_required(['Mediador'])
def build_produtos_queryset(request):
    q = (request.GET.get("q_produto") or "").strip()
    sort = (request.GET.get("sort_produto") or "asc").lower()

    qs = Produto.objects.filter(criador=request.user)

    if q: # busca pelo nome do produto, nome do insumo, e nome do fornecdor do insumo
        qs=qs.filter(Q(nome__icontains=q) | Q(insumos__nome__icontains=q) | Q(insumos__fornecedor__icontains=q))

    order = "nome" if sort == "asc" else "-nome"
    return qs.order_by(order), q ,sort

@group_required(['Mediador'])
def build_cenarios_queryset(request):
    q = (request.GET.get("q_cenario") or "").strip()
    sort = (request.GET.get("sort_cenario") or "asc").lower()
    
    qs = Cenario.objects.filter(criador=request.user)

    if q: # busca pelo nome do cenário, nome do produto, nome do insumo, e nome do fornecdor do insumo
        qs=qs.filter(Q(nome__icontains=q) | Q(produto__nome__icontains=q) | Q(produto__insumos__nome__icontains=q) | Q(produto__insumos__fornecedor__icontains=q))

    order = "nome" if sort == "asc" else "-nome"
    return qs.order_by(order), q, sort
    

#lógica de criação em uma unica função da view
@group_required(['Mediador'])
def cenarios_view(request:HttpRequest):

   
    insumo_form = InsumoForm()
    produto_form = ProdutoForm(usuario=request.user)
    cenario_form = CenarioForm(usuario=request.user)

    if request.method == "POST":
        model_type = request.POST.get("model_type")
        action = request.POST.get("action")

        if model_type == "insumo":
            if action == "create":
                formInsumo = InsumoForm(request.POST)
                if formInsumo.is_valid():
                    insumoNovo = formInsumo.save(commit=False)
                    insumoNovo.criador = request.user
                    insumoNovo.save()
                    messages.success(request, "Insumo criado com sucesso!")
                    return redirect("cenarios:home")
                else:
                    if formInsumo.errors.get('nome'):
                        messages.error(request, "Erro ao salvar insumo, nome do insumo inválido!")
                    if formInsumo.errors.get('fornecedor'):
                        messages.error(request,"Erro ao salvar insumo, nome do fornecedor inválido")
                    insumo_form = formInsumo
                
        if model_type == "produto":
            if action == "create":
                formProduto = ProdutoForm(request.POST)
                if formProduto.is_valid():
                    produtoNovo = formProduto.save(commit=False)
                    produtoNovo.criador = request.user
                    produtoNovo.save()
                    formProduto.save_m2m()
                    messages.success(request, "Produto criado com sucesso!")
                    return redirect("cenarios:home")
                else:
                    if formProduto.errors.get('nome'):
                        messages.error(request,"Erro ao salvar Produto, nome do Produto Inválido")
                    if formProduto.errors.get('insumos'):
                        messages.error(request,"Erro ao salvar, Produto sem insumos!")
                    produto_form = formProduto
                
        if model_type == "cenario":
            if action == "create":
                formCenario = CenarioForm(request.POST)
                if formCenario.is_valid():
                    cenarioNovo = formCenario.save(commit=False)
                    cenarioNovo.criador = request.user
                    cenarioNovo.save()
                    messages.success(request,"Cenário criado com sucesso!")
                    return redirect("cenarios:home")
                else:
                    if formCenario.errors.get('nome'):
                        messages.error(request,"Erro ao salvar Cenário, nome do Cenário Inválido")
                    if formCenario.errors.get('produto'):
                        messages.error(request,"Erro ao salvar, é necessário um produto vinculado para criar um Cenário!")
                
    #lista todos cenarios,produtos e insumo e seus respectivos forms
    insumos, q_insumo, sort_insumo = build_insumos_queryset(request)
    cenarios, q_cenario, sort_cenario = build_cenarios_queryset(request)
    produtos,q_produto,sort_produto = build_produtos_queryset(request)

    #filtragem dos itens criados pelo mediador específico
    if request.user.groups.filter(name="Mediador").exists() and not request.user.is_superuser:
        insumos = insumos.filter(criador=request.user)
        produtos = produtos.filter(criador=request.user)
        cenarios = cenarios.filter(criador=request.user)

    #filtragem dos itens em jogos ativos 
    cenariosAtivos = cenarios.filter(criador=request.user,jogos__status='A').distinct()
    produtosAtivos = produtos.filter(criador=request.user,cenarios__jogos__status='A').distinct()
    insumosAtivos = insumos.filter(criador=request.user,produtos__cenarios__jogos__status='A').distinct()

    contexto = { 
        "insumos": insumos,
        "cenarios": cenarios,
        "produtos": produtos,
        "insumo_form": insumo_form,
        "produto_form": produto_form,
        "cenario_form": cenario_form,
        "q_insumo": q_insumo,
        "q_produto": q_produto,
        "q_cenario": q_cenario,
        "sort_insumo": sort_insumo,
        "sort_produto": sort_produto,
        "sort_cenario": sort_cenario,
        "cenarios_ativos" : cenariosAtivos,
        "produtos_ativos" : produtosAtivos,
        "insumos_ativos" : insumosAtivos
    }
                      
    return render(request,'cenarios/cenarios.html',contexto)

#lógica remover
@group_required(['Mediador'])
def removerInsumo(request:HttpRequest,id):
    ## remover insumo só se nao tiver produto e um cenario relacionado a ele
    insumo = get_object_or_404(Insumo,id=id,criador=request.user)
    if insumo.criador != request.user and not request.user.is_superuser:
        messages.error(request,"Não é possível excluir o insumo pois você não é o criador!")
        return redirect("cenarios:home")
    produtoVinculado = Produto.objects.filter(insumos=insumo).exists()

    if produtoVinculado:
        messages.error(request,"Não é possível excluir o insumo pois está associado a um produto!")
    else:
        insumo.delete()
        messages.success(request,"Insumo Deletado com sucesso")
    return redirect("cenarios:home")

@group_required(['Mediador'])
def removerProduto(request:HttpRequest,id):
    produto = get_object_or_404(Produto,id=id,criador=request.user)

    if produto.criador != request.user and not request.user.is_superuser:
        messages.error(request,"Não é possível excluir o produto pois você não é o criador!")
        return redirect("cenarios:home")
    cenarioVinculado = (Cenario.objects.filter(produto=produto)).exists()

    if cenarioVinculado:
        messages.error(request,"Não é possível excluir o produto pois está associado a um cenário!")
    else:
        produto.delete()
        messages.success(request,"Produto Deletado com sucesso")
    return redirect("cenarios:home")

@group_required(['Mediador'])
def removerCenario(request:HttpRequest,id):

    cenario = get_object_or_404(Cenario,id=id,criador=request.user)
    if cenario.criador != request.user and not request.user.is_superuser:
        messages.error(request,"Não é possível excluir o cenário pois você não é o criador!")
        return redirect("cenarios:home")
    #logica de ver se o cenario está em um jogo ativo
    jogoAtivo = Jogo.objects.filter(cenario=cenario, status = Jogo.ATIVO).exists()

    if jogoAtivo:
        messages.error(request,"Este Cenário está em um Jogo Ativo, Não é possível deletá-lo")
    else:
        cenario.delete()
        messages.success(request,"Cenário Deletado com sucesso")
    return redirect("cenarios:home")

#lógica editar
@group_required(['Mediador'])
def editarInsumo(request:HttpRequest, id):
    insumo = get_object_or_404(Insumo,id=id,criador=request.user)
    if request.method == "POST":
        formInsumo = InsumoForm(request.POST,instance=insumo)
        if formInsumo.is_valid():
            formInsumo.save()
            messages.success(request,"Insumo Editado com sucesso")
            return redirect("cenarios:home")
        else:
            messages.success(request,"Erro ao atualizar insumo!")

    formInsumo = InsumoForm(instance=insumo)
    cenarios = Cenario.objects.filter(criador=request.user)
    insumos = Insumo.objects.filter(criador=request.user)
    produtos = Produto.objects.filter(criador=request.user)
    cenariosAtivos = cenarios.filter(jogos__status='A').distinct()
    produtosAtivos = produtos.filter(cenarios__jogos__status='A').distinct()
    insumosAtivos = insumos.filter(produtos__cenarios__jogos__status='A').distinct()
    contexto = { 
        'insumo_form':formInsumo,
        "insumos": insumos,
        "cenarios": cenarios,
        "produtos": produtos,
        "cenarios_ativos" : cenariosAtivos,
        "produtos_ativos" : produtosAtivos,
        "insumos_ativos" : insumosAtivos
        }
    
    return render(request, 'cenarios/cenarios.html',contexto)

@group_required(['Mediador'])
def editarProduto(request:HttpRequest, id):
    produto = get_object_or_404(Produto, id=id)
    if request.method == "POST":
        formProduto = ProdutoForm(request.POST,instance=produto)
        if formProduto.is_valid():
            formProduto.save()
            messages.success(request,"Produto Editado com sucesso")
            return redirect("cenarios:home")
        else:
            messages.error(request,"Erro ao atualizar Produto!")
    formProduto = ProdutoForm(instance=produto)
    cenarios = Cenario.objects.filter(criador=request.user)
    insumos = Insumo.objects.filter(criador=request.user)
    produtos = Produto.objects.filter(criador=request.user)
    cenariosAtivos = cenarios.filter(jogos__status='A').distinct()
    produtosAtivos = produtos.filter(cenarios__jogos__status='A').distinct()
    insumosAtivos = insumos.filter(produtos__cenarios__jogos__status='A').distinct()
    contexto = {
        'produto_form' : formProduto,
        "insumos": insumos,
        "cenarios": cenarios,
        "produtos": produtos,
        "cenarios_ativos" : cenariosAtivos,
        "produtos_ativos" : produtosAtivos,
        "insumos_ativos" : insumosAtivos
    }

    return render(request, 'cenarios/cenarios.html',contexto)

@group_required(['Mediador'])
def editarCenario(request:HttpRequest, id):
    cenario = get_object_or_404(Cenario,id=id)
    if request.method == "POST":
        formCenario = CenarioForm(request.POST, instance = cenario)
        if formCenario.is_valid():
            formCenario.save()
            messages.success(request,"Cenário Editado com sucesso")
            return redirect ("cenarios:home")
        else:
            messages.error(request,"Erro ao editar Cenário!")
    formCenario = CenarioForm(instance=cenario)
    cenarios = Cenario.objects.filter(criador=request.user)
    insumos = Insumo.objects.filter(criador=request.user)
    produtos = Produto.objects.filter(criador=request.user)
    cenariosAtivos = cenarios.filter(jogos__status='A').distinct()
    produtosAtivos = produtos.filter(cenarios__jogos__status='A').distinct()
    insumosAtivos = insumos.filter(produtos__cenarios__jogos__status='A').distinct()
    contexto = {
        'cenario_form' : formCenario,
        "insumos": insumos,
        "cenarios": cenarios,
        "produtos": produtos,
        "cenarios_ativos" : cenariosAtivos,
        "produtos_ativos" : produtosAtivos,
        "insumos_ativos" : insumosAtivos
    }
    return render(request, 'cenarios/cenarios.html',contexto)


