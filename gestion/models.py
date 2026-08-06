from django.db import models
from django.contrib.auth.models import User

# 1. PERFIL DE USUARIO (Para diferenciar Clientes de Barberos)
class PerfilUsuario(models.Model):
    ROLES = (
        ('CLIENTE', 'Cliente'),
        ('BARBERO', 'Barbero / Dueño'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rol = models.CharField(max_length=10, choices=ROLES, default='CLIENTE')
    telefono = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_rol_display()}"

# 2. SUCURSAL / BARBERÍA
class Barberia(models.Model):
    PLANES = (
        ('INDIVIDUAL', 'Plan Individual ($80.000 COP)'),
        ('STUDIO', 'Plan Studio ($150.000 COP)'),
        ('ELITE', 'Plan Élite ($200.000 COP)'),
    )
    dueno = models.ForeignKey(User, on_delete=models.CASCADE, related_name='barberias')
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)
    barrio = models.CharField(max_length=100, default='Itagüí')
    descripcion = models.TextField(blank=True, help_text="Ej: Especialistas en fades, perfilado de barba...")
    google_maps_link = models.URLField(blank=True)
    plan_actual = models.CharField(max_length=20, choices=PLANES, default='INDIVIDUAL') # NUEVO CAMPO

    def __str__(self):
        return f"{self.nombre} ({self.barrio})"

# 3. SERVICIOS OFRECIDOS POR LA BARBERÍA
class Servicio(models.Model):
    barberia = models.ForeignKey(Barberia, on_delete=models.CASCADE, related_name='servicios')
    nombre = models.CharField(max_length=100) # Ej: Corte Tradicional, Perfilado de Barba
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    duracion_minutos = models.IntegerField(default=30)

    def __str__(self):
        return f"{self.nombre} - ${self.precio} ({self.barberia.nombre})"

# 4. HORARIOS DE ATENCIÓN DE LA BARBERÍA
class HorarioAtencion(models.Model):
    DIAS = (
        ('LUN', 'Lunes'),
        ('MAR', 'Martes'),
        ('MIE', 'Miércoles'),
        ('JUE', 'Jueves'),
        ('VIE', 'Viernes'),
        ('SAB', 'Sábado'),
        ('DOM', 'Domingo'),
    )
    barberia = models.ForeignKey(Barberia, on_delete=models.CASCADE, related_name='horarios')
    dia = models.CharField(max_length=3, choices=DIAS)
    hora_apertura = models.TimeField()
    hora_cierre = models.TimeField()

    def __str__(self):
        return f"{self.barberia.nombre} - {self.get_dia_display()}: {self.hora_apertura} - {self.hora_cierre}"

# 5. CITAS RESERVADAS POR CLIENTES
class Cita(models.Model):
    ESTADOS = (
        ('PENDIENTE', 'Pendiente'),
        ('CONFIRMADA', 'Confirmada'),
        ('CANCELADA', 'Cancelada'),
    )
    nombre_cliente = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    barberia = models.ForeignKey(Barberia, on_delete=models.CASCADE, related_name='citas')
    servicios = models.ManyToManyField(Servicio) # Permite elegir varios servicios en una cita
    fecha = models.DateField()
    hora = models.TimeField()
    estado = models.CharField(max_length=10, choices=ESTADOS, default='PENDIENTE')

    def __str__(self):
        return f"Cita de {self.nombre_cliente} en {self.barberia.nombre} ({self.fecha} {self.hora})"