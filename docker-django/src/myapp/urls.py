from django.conf.urls import url ,  include

from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings


from django.urls import path
from django.http import HttpResponse

from .import views

urlpatterns = [
    path("home", views.pagina_home)

]