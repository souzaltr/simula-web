from django.shortcuts import render,redirect,get_object_or_404
from .models import Insumo,Cenario,Produto 
from .forms import InsumoForm,ProdutoForm,CenarioForm
from django.http import HttpRequest
# Create your views here.

from django.http import HttpResponse

#lógica dos CRUDs em uma unica função da view
def cenarios_view(request:HttpRequest):
   
    insumo_form = InsumoForm()
    produto_form = ProdutoForm()
    cenario_form = CenarioForm()


    #lista todos cenarios,produtos e insumo
    contexto = { 
        "insumos": Insumo.objects.all(),
        "cenarios": Cenario.objects.all(),
        "produtos": Produto.objects.all(),
        "insumo_form": insumo_form,
        "produto_form": produto_form,
        "cenario_form": cenario_form,
    }

    if request.method == "POST":
        model_type = request.POST.get("model_type")
        action = request.POST.get("action")

        if model_type == "insumo":
            if action == "create":
                formInsumo = InsumoForm(request.POST)
                if formInsumo.is_valid():
                    formInsumo.save()
                    return redirect("cenarios:home")
                
        if model_type == "produto":
            if action == "create":
                formProduto = ProdutoForm(request.POST)
                if formProduto.is_valid():
                    formProduto.save()
                    return redirect("cenarios:home")
                
        if model_type == "cenario":
            if action == "create":
                formCenario = CenarioForm(request.POST)
                if formCenario.is_valid():
                    formCenario.save()
                    return redirect("cenarios:home")
                
    return render(request,'cenarios/cenarios.html',contexto)




def removerInsumo(request:HttpRequest,id):
    insumo = get_object_or_404(Insumo,id=id)
    insumo.delete()
    return redirect("cenarios:home")

def removerProduto(request:HttpRequest,id):
    produto = get_object_or_404(Produto,id=id)
    produto.delete()
    return redirect("cenarios:home")

def removerCenario(request:HttpRequest,id):
    #logica de ver se o cenario está em um jogo ativo
    cenario = get_object_or_404(Cenario,id=id)
    cenario.delete()
    return redirect("cenarios:home")

def editarInsumo(request:HttpRequest, id):
    insumo = get_object_or_404(Insumo,id=id)
    if request.method == "POST":
        formInsumo = InsumoForm(request.POST,instance=insumo)
        if formInsumo.is_valid():
            formInsumo.save()
            return redirect("cenarios:home")
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
            return redirect("cenarios:home")
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
            return redirect ("cenarios:home")
    formCenario = CenarioForm(instance=cenario)
    contexto = {
        'cenario_form' : formCenario,
        "insumos": Insumo.objects.all(),
        "cenarios": Cenario.objects.all(),
        "produtos": Produto.objects.all(),
    }
    return render(request, 'cenarios/cenarios.html',contexto)