from django.urls import path
from django.http import HttpResponse

from .import views

app_name = "cenarios"

urlpatterns = [
    path("", views.cenarios_view), 
    path("adicionar/",views.cenarios_adicionar,name="adicionarCenario"),
    path("insumos/adicionar",views.insumos_adicionar),
    path("produto/adicionar",views.produto_adicionar)
]
