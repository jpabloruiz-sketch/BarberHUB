from django.shortcuts import render
from django.contrib.auth.decorators import login_required # Importa esto
from .models import Sucursal
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib import messages



def registro(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save() # Guarda el nuevo usuario en la base de datos
            username = form.cleaned_data.get('username')
            messages.success(request, f'¡Cuenta creada para {username}! Ya puedes iniciar sesión.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/registro.html', {'form': form})

def home(request):
    sucursales = Sucursal.objects.all()
    return render(request, 'inicio.html', {'sucursales': sucursales})

@login_required # Esto obliga a loguearse para ver esta vista
def agendar_cita(request):
    # Aquí va tu lógica de citas...
    return render(request, 'agendar.html')

def correo_prueba(request):
    if request.method == "POST":
        destino = request.POST.get("destino")
        try:
            send_mail(
                'Django SMTP prueba',
                '¡Hola! Este es un correo de prueba enviado desde Django.',
                'barberhub15@gmail.com', #sender
                ['sdiezmarulanda@gmail.com'], #receiver
                fail_silently=False,
            )
            messages.success(request, 'Correo enviado exitosamente.')
        except Exception as e:
            messages.error(request, f'Error: {e}')
        return redirect('correo_prueba')
    else:
        return render(request, "correo_prueba.html")

def barberias(request):
    return render(request, 'barberias.html')

def soporte(request):
    return render(request, 'soporte.html')