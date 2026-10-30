from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from gestion.models import PerfilUsuario

class Command(BaseCommand):
    help = 'Crea o asegura los 3 administradores fijos de BarberHUB'

    def handle(self, *args, **options):
        admins = [
            {'username': 'juan_bonilla', 'email': 'juan@barberhub.com', 'nombre': 'Juan Esteban', 'apellido': 'Bonilla'},
            {'username': 'samuel_diez', 'email': 'samuel@barberhub.com', 'nombre': 'Samuel', 'apellido': 'Diez Marulanda'},
            {'username': 'juan_pablo', 'email': 'juanpablo@barberhub.com', 'nombre': 'Juan Pablo', 'apellido': 'Ruiz'},
        ]

        for data in admins:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': data['email'],
                    'first_name': data['nombre'],
                    'last_name': data['apellido'],
                    'is_staff': True,
                    'is_superuser': True
                }
            )
            if created:
                user.set_password('AdminBarber2026*')  # Contraseña provisional
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Administrador creado: {data['username']}"))
            else:
                user.is_staff = True
                user.is_superuser = True
                user.save()
                self.stdout.write(self.style.WARNING(f"Administrador ya existe, permisos actualizados: {data['username']}"))

            perfil, _ = PerfilUsuario.objects.get_or_create(user=user)
            perfil.rol = 'ADMIN'
            perfil.is_active = True
            perfil.save()