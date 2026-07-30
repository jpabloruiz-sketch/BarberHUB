from django.urls import path
from . import views
from django.urls import path, include

urlpatterns = [
    path('', views.home, name='home'),
    path('agendar/', views.agendar_cita, name='agendar'),
    path('registro/', views.registro, name='registro'), # Nueva ruta
    path('correo_prueba/', views.correo_prueba, name='correo_prueba'),
    path('barberias/', views.barberias, name='barberias'),


]

