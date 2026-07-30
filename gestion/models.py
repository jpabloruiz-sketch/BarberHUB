from django.db import models

# Create your models here.

class Sucursal(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)
    ciudad = models.CharField(max_length=100)
    google_maps_link = models.URLField(blank=True) # Para el botón de "Cómo llegar"

    def __str__(self):
        return f"{self.nombre} - {self.ciudad}"

class Cita(models.Model):
    nombre_cliente = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora = models.TimeField()
    # Cambiamos 'placeholder' por 'help_text' o simplemente lo quitamos
    motivo = models.TextField(help_text="Ej: Cambio de batería, Revisión de alternador")

    def __str__(self):
        return f"Cita de {self.nombre_cliente} el {self.fecha}"