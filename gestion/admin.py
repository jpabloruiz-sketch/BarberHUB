from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import PerfilUsuario, Barberia, Servicio, HorarioAtencion, Cita

# 1. Crear un Inline para mostrar el Perfil junto con el Usuario
class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'Perfil de Usuario (Rol)'

# 2. Re-definir el Admin de Usuarios para incluir el Inline
class UserAdmin(BaseUserAdmin):
    inlines = (PerfilUsuarioInline,)

# 3. Desregistrar el User original y volver a registrarlo personalizado
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# 4. Registrar el resto de modelos de BarberHUB
admin.site.register(PerfilUsuario)
admin.site.register(Barberia)
admin.site.register(Servicio)
admin.site.register(HorarioAtencion)
admin.site.register(Cita)