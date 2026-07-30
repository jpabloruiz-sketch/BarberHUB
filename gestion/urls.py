from django.urls import path
from . import views

urlpatterns = [
    # Mapeamos la vista principal a AMBOS nombres para evitar errores
    path('', views.home, name='inicio'),
    path('inicio/', views.home, name='home'),
    
    path('agendar/', views.agendar_cita, name='agendar'),
    path('registro/', views.registro, name='registro'),
    path('correo_prueba/', views.correo_prueba, name='correo_prueba'),
    path('barberias/', views.barberias, name='barberias'),
    path('soporte/', views.soporte, name='soporte'),
]