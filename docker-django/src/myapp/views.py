from django import get_version
from django.views.generic import TemplateView
from .tasks import show_hello_world
from .models import DemoModel

from django.shortcuts import render 
from django.http import HttpResponse


# Create your views here.

def pagina_home(request):
    contexto = { 
        "nome" : "Alessandro"
    }
    return render(request, 'home.html', contexto)


    

