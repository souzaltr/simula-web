from django.urls import path
from . import views

app_name = 'jogo_empresa'

urlpatterns = [
    path('home', views.pagina_home, name='home'),
    path('jogos', views.jogos_crud, name='jogos_crud'),
    path('jogos/<int:jogo_id>/empresas/', views.empresas_crud, name='empresas_crud')
]
