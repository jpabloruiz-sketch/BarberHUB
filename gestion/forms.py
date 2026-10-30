from django import forms
from .models import Cita

class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['nombre_cliente', 'telefono', 'sucursal', 'fecha', 'hora', 'motivo']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'hora': forms.TimeInput(attrs={'type': 'time'}),
            'motivo': forms.Textarea(attrs={'placeholder': 'Ej: Cambio de batería, Revisión de alternador'}),
        }