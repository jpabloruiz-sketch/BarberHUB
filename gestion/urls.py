from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Vistas públicas
    path('', views.home, name='inicio'),
    path('inicio/', views.home, name='home'),
    path('barberias/', views.barberias, name='barberias'),
    path('soporte/', views.soporte, name='soporte'),
    path('pagar-plan/', views.pagar_plan, name='pagar_plan'),
    
    # Autenticación
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('registro/', views.registro, name='registro'),
    
    # Citas
    path('agendar/', views.agendar_cita, name='agendar'),
    
    # Panel Barbero
    path('panel-barbero/', views.panel_barbero, name='panel_barbero'),
    path('panel-barbero/servicio/nuevo/', views.agregar_servicio, name='agregar_servicio'),
    path('panel-barbero/servicio/editar/<int:servicio_id>/', views.editar_servicio, name='editar_servicio'),
    path('panel-barbero/horario/nuevo/', views.agregar_horario, name='agregar_horario'),
    path('panel-barbero/horario/editar/<int:horario_id>/', views.editar_horario, name='editar_horario'),
    path('servicio/eliminar/<int:servicio_id>/', views.eliminar_servicio, name='eliminar_servicio'),
    path('servicio/eliminar/<int:servicio_id>/', views.eliminar_servicio, name='eliminar_servicio'),
    path('horario/eliminar/<int:horario_id>/', views.eliminar_horario, name='eliminar_horario'),
    
    # Utilidades
    path('correo-prueba/', views.correo_prueba, name='correo_prueba'),
]