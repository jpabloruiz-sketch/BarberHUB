from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Vistas públicas
    path('', views.home, name='inicio'),
    path('inicio/', views.home, name='home'),
    path('barberias/', views.barberias, name='barberias'),
    path('historial/', views.historial, name='historial'),
    path('soporte/', views.soporte, name='soporte'),
    path('pagar-plan/', views.pagar_plan, name='pagar_plan'),
    path('logout/', views.cerrar_sesion, name='logout'),
    
    # Autenticación
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('registro/', views.registro, name='registro'),
    
    # Citas
    path('agendar/', views.agendar_cita, name='agendar'),
    path('cita/modificar/<int:cita_id>/', views.modificar_cita, name='modificar_cita'),
    path('cita/cancelar/<int:cita_id>/', views.cancelar_cita, name='cancelar_cita'),
    
    # Panel Barbero
    path('panel-barbero/', views.panel_barbero, name='panel_barbero'),
    path('panel-barbero/servicio/nuevo/', views.agregar_servicio, name='agregar_servicio'),
    path('panel-barbero/servicio/editar/<int:servicio_id>/', views.editar_servicio, name='editar_servicio'),
    path('panel-barbero/horario/nuevo/', views.agregar_horario, name='agregar_horario'),
    path('panel-barbero/horario/editar/<int:horario_id>/', views.editar_horario, name='editar_horario'),
    path('servicio/eliminar/<int:servicio_id>/', views.eliminar_servicio, name='eliminar_servicio'),
    path('horario/eliminar/<int:horario_id>/', views.eliminar_horario, name='eliminar_horario'),
    
    # Panel Administrador Exclusivo (Juan Bonilla, Samuel Diez, Juan Pablo Ruiz)
    path('panel-admin/', views.panel_admin_dashboard, name='panel_admin_dashboard'),
    path('panel-admin/usuario/toggle/<int:user_id>/', views.toggle_usuario, name='toggle_usuario'),
    path('panel-admin/barberia/toggle/<int:barberia_id>/', views.toggle_barberia, name='toggle_barberia'),
    
    # Utilidades
    path('correo-prueba/', views.correo_prueba, name='correo_prueba'),
]