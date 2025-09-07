from django.shortcuts import render,redirect,get_object_or_404
from .models import Insumo,Cenario,Produto 
from .forms import InsumoForm,ProdutoForm,CenarioForm
from django.http import HttpRequest
from django.contrib import messages
from jogos.models import Jogo

# Create your views here.

#filtrar e ordenar
def build_insumos_queryset(request):
    q = (request.GET.get("q_insumo")or"").strip()
    sort = (request.GET.get("sort_insumo") or "asc").lower()

    qs = Insumo.objects.all()

    if q:
        qs=qs.filter(nome__icontains=q)

    order = "nome" if sort == "asc" else "-nome"
    return qs.order_by(order), q, sort

def build_produtos_queryset(request):
    q = (request.GET.get("q_produto") or "").strip()
    sort = (request.GET.get("sort_produto") or "asc").lower()

    qs = Produto.objects.all()

    if q:
        qs=qs.filter(nome__icontains=q)

    order = "nome" if sort == "asc" else "-nome"
    return qs.order_by(order), q ,sort

def build_cenarios_queryset(request):
    q = (request.GET.get("q_cenario") or "").strip()
    sort = (request.GET.get("sort_cenario") or "asc").lower()
    qs = Cenario.objects.all()

    if q: 
        qs=qs.filter(nome__icontains=q)

    order = "nome" if sort == "asc" else "-nome"
    return qs.order_by(order), q, sort
    

#lógica dos CRUDs em uma unica função da view
def cenarios_view(request:HttpRequest):
   
    insumo_form = InsumoForm()
    produto_form = ProdutoForm()
    cenario_form = CenarioForm()

    if request.method == "POST":
        model_type = request.POST.get("model_type")
        action = request.POST.get("action")

        if model_type == "insumo":
            if action == "create":
                formInsumo = InsumoForm(request.POST)
                if formInsumo.is_valid():
                    formInsumo.save()
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
                    formProduto.save()
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
                    formCenario.save()
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
        "sort_cenario": sort_cenario
    }
                      
    return render(request,'cenarios/cenarios.html',contexto)

def removerInsumo(request:HttpRequest,id):
    ## remover insumo só se nao tiver produto e um cenario relacionado a ele
    insumo = get_object_or_404(Insumo,id=id)
    insumo.delete()
    messages.success(request,"Insumo Deletado com sucesso")
    return redirect("cenarios:home")

def removerProduto(request:HttpRequest,id):
    produto = get_object_or_404(Produto,id=id)
    produto.delete()
    messages.success(request,"Produto Deletado com sucesso")
    return redirect("cenarios:home")

def removerCenario(request:HttpRequest,id):

    cenario = get_object_or_404(Cenario,id=id)
    #logica de ver se o cenario está em um jogo ativo
    jogoAtivo = Jogo.objects.filter(cenario=cenario, status = Jogo.ATIVO).exists()

    if jogoAtivo:
        messages.error(request,"Este Cenário está em um Jogo Ativo, Não é possível deletá-lo")
    else:
        cenario.delete()
        messages.success(request,"Cenário Deletado com sucesso")
    return redirect("cenarios:home")

def editarInsumo(request:HttpRequest, id):
    insumo = get_object_or_404(Insumo,id=id)
    if request.method == "POST":
        formInsumo = InsumoForm(request.POST,instance=insumo)
        if formInsumo.is_valid():
            formInsumo.save()
            messages.success(request,"Insumo Editado com sucesso")
            return redirect("cenarios:home")
        else:
            messages.success(request,"Erro ao atualizar insumo!")
    formInsumo = InsumoForm(instance=insumo)
    contexto = { 
        'insumo_form':formInsumo,
        "insumos": Insumo.objects.all(),
        "cenarios": Cenario.objects.all(),
        "produtos": Produto.objects.all(),
        }
    
    return render(request, 'cenarios/cenarios.html',contexto)

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
    contexto = {
        'produto_form' : formProduto,
        "insumos": Insumo.objects.all(),
        "cenarios": Cenario.objects.all(),
        "produtos": Produto.objects.all(),
    }

    return render(request, 'cenarios/cenarios.html',contexto)

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
    contexto = {
        'cenario_form' : formCenario,
        "insumos": Insumo.objects.all(),
        "cenarios": Cenario.objects.all(),
        "produtos": Produto.objects.all(),
    }
    return render(request, 'cenarios/cenarios.html',contexto)


