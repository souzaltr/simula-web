from django.urls import path
from .views import SimularView, AplicarSimulacaoView, HistoricoView

app_name = "simulacao"

urlpatterns = [
    path("simular/", SimularView.as_view(), name="simular"),
    path("aplicar/", AplicarSimulacaoView.as_view(), name="aplicar"),
    path("historico/", HistoricoView.as_view(), name="historico"),
]
