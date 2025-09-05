from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse

def cenarios_view(request):
    #lista todos cenarios,produtos e insumo
    #insumos = Insumo.objects.all()
    #cenarios = Cenario.objects.all()
    #fazer um contexto que pega o usuario logado "request.user" para colocar no render
    return render(request,'cenarios/cenarios.html')

#lógica dos CRUDs
def cenarios_adicionar(request):
    return render(request,'cenarios/cenarios.html')

def cenarios_deletar(request):
    return render(request,'cenarios/cenarios.html')

def cenarios_editar(request):
    return render(request,'cenarios/cenarios.html')

def insumos_adicionar(request):
    return render(request,'cenarios/cenarios.html')

def insumos_deletar(request):
    return render(request,'cenarios/cenarios.html')

def insumoms_editar(request):
    return render(request,'cenarios/cenarios.html')

def produto_adicionar(request):
    return render(request,'cenarios/cenarios.html')

def produto_deletar(request):
    return render(request,'cenarios/cenarios.html')

def produto_editar(request):
    return render(request,'cenarios/cenarios.html')