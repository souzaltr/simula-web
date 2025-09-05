from django.urls import path
from . import views

app_name = 'myapp'

urlpatterns = [
    path('home', views.pagina_home, name='home'),
    path('jogos', views.jogos_crud, name='jogos_crud')
]
