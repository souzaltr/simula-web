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
    

