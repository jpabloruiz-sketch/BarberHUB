from django.urls import path
from . import views

urlpatterns = [
    # Vistas públicas
    path('', views.home, name='inicio'),
    path('inicio/', views.home, name='home'),
    path('barberias/', views.barberias, name='barberias'),
    path('soporte/', views.soporte, name='soporte'),
    path('pagar-plan/', views.pagar_plan, name='pagar_plan'),
    
    # Autenticación y Citas
    path('registro/', views.registro, name='registro'),
    path('agendar/', views.agendar_cita, name='agendar'),
    
    # Panel Barbero
    path('panel-barbero/', views.panel_barbero, name='panel_barbero'),
    path('panel-barbero/servicio/nuevo/', views.agregar_servicio, name='agregar_servicio'),
    path('panel-barbero/servicio/editar/<int:servicio_id>/', views.editar_servicio, name='editar_servicio'),
    path('panel-barbero/horario/nuevo/', views.agregar_horario, name='agregar_horario'),
    path('panel-barbero/horario/editar/<int:horario_id>/', views.editar_horario, name='editar_horario'),
    
    # Utilidades
    path('correo-prueba/', views.correo_prueba, name='correo_prueba'),
]