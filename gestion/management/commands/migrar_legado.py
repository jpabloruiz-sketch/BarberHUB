from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from gestion.models import PerfilUsuario
import json
import os

class Command(BaseCommand):
    help = 'Importa y sincroniza datos de usuarios desde un archivo JSON legado.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--json_file',
            type=str,
            required=True,
            help='Ruta del archivo JSON con los datos a migrar'
        )

    def handle(self, *args, **options):
        file_path = options['json_file']

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'El archivo {file_path} no existe.'))
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        registros_procesados = 0
        self.stdout.write(self.style.SUCCESS('Iniciando migración hacia la base de datos de BarberHUB...'))

        for item in data:
            email = item.get('email')
            if not email:
                continue

            try:
                with transaction.atomic():
                    # 1. Obtener o crear el usuario nativo de Django usando el email como username
                    username = email.split('@')[0]
                    user, user_created = User.objects.get_or_create(
                        email=email,
                        defaults={
                            'username': username,
                            'first_name': item.get('nombre', ''),
                            'is_active': item.get('is_active', True)
                        }
                    )

                    # 2. Obtener o actualizar el PerfilUsuario asociado al User
                    perfil, perfil_created = PerfilUsuario.objects.get_or_create(
                        user=user,
                        defaults={
                            'rol': item.get('rol', 'CLIENTE'),
                            'telefono': item.get('telefono', ''),
                            'is_active': item.get('is_active', True)
                        }
                    )

                    # Si el perfil ya existía, se actualizan sus valores
                    if not perfil_created:
                        perfil.is_active = item.get('is_active', True)
                        if 'rol' in item:
                            perfil.rol = item['rol']
                        if 'telefono' in item:
                            perfil.telefono = item['telefono']
                        perfil.save()

                    registros_procesados += 1

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error procesando {email}: {str(e)}"))

        self.stdout.write(
            self.style.SUCCESS(f'Migración finalizada con éxito. Se procesaron {registros_procesados} registros.')
        )