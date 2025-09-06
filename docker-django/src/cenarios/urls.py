from django.urls import path
from django.http import HttpResponse

from .import views

app_name = "cenarios"

urlpatterns = [
    path("", views.cenarios_view, name="home"),
    path("remover/<int:id>",views.removerCenario,name="removerCenario"),
    path("insumos/remover/<int:id>", views.removerInsumo,name="removerInsumo"),
    path("produtos/remover/<int:id>",views.removerProduto,name="removerProduto"),
    path("insumos/editar/<int:id>",views.editarInsumo,name="editarInsumo"),
    path("produtos/editar/<int:id>",views.editarProduto,name="editarProduto"),
    path("editar/<int:id>", views.editarCenario,name="editarCenario"),
]
