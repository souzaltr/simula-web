from django.urls import path
from .views import SimulacaoView, HistoricoView

app_name = "simulacao"

urlpatterns = [
    path("simular/", SimulacaoView.as_view(), name="simular"),
    path("historico/", HistoricoView.as_view(), name="historico"),
]
