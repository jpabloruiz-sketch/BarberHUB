from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.core.mail import send_mail
from .models import Barberia, Servicio, HorarioAtencion, Cita, PerfilUsuario

# Función auxiliar para formatear la hora (12 horas AM/PM -> 24 horas para la BD)
def construir_hora(hora_val, min_val, ampm_val, fallback_str=None):
    if hora_val and min_val and ampm_val:
        try:
            h = int(hora_val)
            m = int(min_val)
            if ampm_val == 'PM' and h < 12:
                h += 12
            elif ampm_val == 'AM' and h == 12:
                h = 0
            return f"{h:02d}:{m:02d}:00"
        except (ValueError, TypeError):
            pass
    return fallback_str


# ================= VISTAS PÚBLICAS =================

def home(request):
    barberias = Barberia.objects.all()
    return render(request, 'inicio.html', {'barberias': barberias})

def barberias(request):
    lista_barberias = Barberia.objects.prefetch_related('horarios').all()
    return render(request, 'barberias.html', {'barberias': lista_barberias})

def soporte(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        correo = request.POST.get('correo')
        tipo = request.POST.get('tipo')
        mensaje = request.POST.get('mensaje')

        asunto = f"Soporte BarberHUB: {tipo}"
        cuerpo = f"Nombre del remitente: {nombre}\nCorreo de contacto: {correo}\n\nMensaje:\n{mensaje}"

        try:
            send_mail(
                subject=asunto,
                message=cuerpo,
                from_email=None, 
                recipient_list=['soporte.barberhub@gmail.com'],
                fail_silently=False,
            )
            messages.success(request, '¡Mensaje enviado con éxito! Te responderemos pronto.')
        except Exception as e:
            messages.error(request, 'Hubo un error al enviar el mensaje. Inténtalo de nuevo más tarde.')

        return redirect('soporte')
        
    return render(request, 'soporte.html')

@login_required
def pagar_plan(request):
    barberia = Barberia.objects.filter(dueno=request.user).first()
    
    if request.method == 'POST':
        nuevo_plan = request.POST.get('plan')
        if barberia and nuevo_plan:
            barberia.plan_actual = nuevo_plan
            barberia.save()
            messages.success(request, '¡Has actualizado tu plan exitosamente!')
            return redirect('pagar_plan')
            
    return render(request, 'pagar_plan.html', {'barberia': barberia})


# ================= AUTENTICACIÓN =================

def registro(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        rol = request.POST.get('rol', 'CLIENTE')
        telefono = request.POST.get('telefono', '')
        email = request.POST.get('email', '')

        if form.is_valid():
            user = form.save()
            if email:
                user.email = email
                user.save()
            
            # Crea el perfil con el rol y teléfono
            PerfilUsuario.objects.create(
                user=user, 
                rol=rol,
                telefono=telefono
            )
            
            username = form.cleaned_data.get('username')
            messages.success(request, f'¡Cuenta creada para {username}! Ya puedes iniciar sesión.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/registro.html', {'form': form})

from django.contrib.auth import logout

def cerrar_sesion(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('home')


# ================= GESTIÓN DE CITAS =================

@login_required
def agendar_cita(request):
    barberia_id = request.GET.get('barberia_id') or request.POST.get('barberia_id')
    
    barberia_seleccionada = None
    servicios = []
    horarios = []

    if barberia_id:
        barberia_seleccionada = Barberia.objects.filter(id=barberia_id).first()
        if barberia_seleccionada:
            servicios = barberia_seleccionada.servicios.all()
            horarios = barberia_seleccionada.horarios.all()

    if request.method == 'POST':
        nombre_cliente = request.POST.get('nombre_cliente')
        telefono = request.POST.get('telefono')
        fecha = request.POST.get('fecha')
        hora = request.POST.get('hora')
        servicios_ids = request.POST.getlist('servicios')

        if not barberia_seleccionada:
            messages.error(request, 'Debe seleccionar una barbería válida.')
            return redirect('barberias')

        # Crear la cita en la base de datos
        cita = Cita.objects.create(
            nombre_cliente=nombre_cliente,
            telefono=telefono,
            barberia=barberia_seleccionada,
            fecha=fecha,
            hora=hora,
            estado='PENDIENTE'
        )

        # Asociar los servicios seleccionados (relación ManyToMany)
        if servicios_ids:
            cita.servicios.set(servicios_ids)

        messages.success(request, '¡Tu cita ha sido agendada con éxito!')
        return redirect('historial')

    return render(request, 'agendar.html', {
        'barberia_seleccionada': barberia_seleccionada,
        'servicios': servicios,
        'horarios': horarios
    })


@login_required
def historial(request):
    # Consulta las citas agendadas por el usuario actual
    citas = Cita.objects.filter(
        nombre_cliente=request.user.username
    ).prefetch_related('servicios', 'barberia').order_by('-fecha', '-hora')
    
    return render(request, 'historial.html', {'citas': citas})


@login_required
def modificar_cita(request, cita_id):
    # Asegura que la cita pertenezca al usuario logueado
    cita = get_object_or_404(Cita, id=cita_id, nombre_cliente=request.user.username)
    
    if request.method == 'POST':
        nueva_fecha = request.POST.get('fecha')
        nueva_hora = request.POST.get('hora')
        
        if nueva_fecha and nueva_hora:
            cita.fecha = nueva_fecha
            cita.hora = nueva_hora
            cita.save()
            messages.success(request, 'La cita se ha reprogramado correctamente.')
        else:
            messages.error(request, 'Por favor ingresa fecha y hora válidas.')

    return redirect('historial')


@login_required
def cancelar_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id, nombre_cliente=request.user.username)
    
    if request.method == 'POST':
        cita.estado = 'CANCELADA'
        cita.save()
        messages.success(request, 'La cita ha sido cancelada.')

    return redirect('historial')

# ================= PANEL DE BARBERO =================

@login_required
def panel_barbero(request):
    perfil, _ = PerfilUsuario.objects.get_or_create(user=request.user)
    if perfil.rol != 'BARBERO':
        messages.warning(request, 'Esta sección es exclusiva para barberos registrados.')
        return redirect('inicio')

    barberia = Barberia.objects.filter(dueno=request.user).first()

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        direccion = request.POST.get('direccion')
        barrio = request.POST.get('barrio', 'Itagüí')
        descripcion = request.POST.get('descripcion')
        maps = request.POST.get('google_maps_link')

        if not barberia:
            barberia = Barberia.objects.create(
                dueno=request.user,
                nombre=nombre,
                direccion=direccion,
                barrio=barrio,
                descripcion=descripcion,
                google_maps_link=maps
            )
            messages.success(request, '¡Barbería registrada exitosamente!')
        else:
            barberia.nombre = nombre
            barberia.direccion = direccion
            barberia.barrio = barrio
            barberia.descripcion = descripcion
            barberia.google_maps_link = maps
            barberia.save()
            messages.success(request, 'Información actualizada correctamente.')

        return redirect('panel_barbero')

    servicios = barberia.servicios.all() if barberia else []
    horarios = barberia.horarios.all() if barberia else []
    citas = barberia.citas.all() if barberia else []

    return render(request, 'panel_barbero.html', {
        'barberia': barberia,
        'servicios': servicios,
        'horarios': horarios,
        'citas': citas
    })

@login_required
def agregar_servicio(request):
    if request.method == 'POST':
        barberia = Barberia.objects.filter(dueno=request.user).first()
        if barberia:
            nombre = request.POST.get('nombre')
            precio_raw = request.POST.get('precio', '0').replace('.', '').replace(',', '').replace('$', '').strip()
            precio = int(precio_raw) if precio_raw.isdigit() else 0
            duracion = request.POST.get('duracion', 30)
            
            Servicio.objects.create(
                barberia=barberia,
                nombre=nombre,
                precio=precio,
                duracion_minutos=duracion
            )
            messages.success(request, 'Servicio agregado.')
    return redirect('panel_barbero')

@login_required
def editar_servicio(request, servicio_id):
    if request.method == 'POST':
        servicio = get_object_or_404(Servicio, id=servicio_id, barberia__dueno=request.user)
        servicio.nombre = request.POST.get('nombre')
        precio_raw = request.POST.get('precio', '0').replace('.', '').replace(',', '').replace('$', '').strip()
        servicio.precio = int(precio_raw) if precio_raw.isdigit() else 0
        servicio.duracion_minutos = request.POST.get('duracion')
        servicio.save()
        messages.success(request, 'Servicio actualizado correctamente.')
    return redirect('panel_barbero')

@login_required
def eliminar_servicio(request, servicio_id):
    servicio = get_object_or_404(Servicio, id=servicio_id, barberia__dueno=request.user)
    if request.method == 'POST':
        servicio.delete()
        messages.success(request, 'El servicio ha sido eliminado correctamente.')
    return redirect('panel_barbero')

@login_required
def agregar_horario(request):
    if request.method == 'POST':
        barberia = Barberia.objects.filter(dueno=request.user).first()
        if barberia:
            dia = request.POST.get('dia')
            apertura = construir_hora(
                request.POST.get('apertura_hora'),
                request.POST.get('apertura_minuto'),
                request.POST.get('apertura_ampm'),
                request.POST.get('hora_apertura')
            )
            cierre = construir_hora(
                request.POST.get('cierre_hora'),
                request.POST.get('cierre_minuto'),
                request.POST.get('cierre_ampm'),
                request.POST.get('hora_cierre')
            )
            
            if apertura and cierre:
                HorarioAtencion.objects.create(
                    barberia=barberia,
                    dia=dia,
                    hora_apertura=apertura,
                    hora_cierre=cierre
                )
                messages.success(request, 'Horario configurado correctamente.')
    return redirect('panel_barbero')

@login_required
def editar_horario(request, horario_id):
    if request.method == 'POST':
        horario = get_object_or_404(HorarioAtencion, id=horario_id, barberia__dueno=request.user)
        horario.dia = request.POST.get('dia')
        
        apertura = construir_hora(
            request.POST.get('apertura_hora'),
            request.POST.get('apertura_minuto'),
            request.POST.get('apertura_ampm'),
            request.POST.get('hora_apertura')
        )
        cierre = construir_hora(
            request.POST.get('cierre_hora'),
            request.POST.get('cierre_minuto'),
            request.POST.get('cierre_ampm'),
            request.POST.get('hora_cierre')
        )
        
        if apertura and cierre:
            horario.hora_apertura = apertura
            horario.hora_cierre = cierre
            horario.save()
            messages.success(request, 'Horario actualizado correctamente.')
    return redirect('panel_barbero')

@login_required
def eliminar_horario(request, horario_id):
    horario = get_object_or_404(HorarioAtencion, id=horario_id, barberia__dueno=request.user)
    if request.method == 'POST':
        horario.delete()
        messages.success(request, 'El horario ha sido eliminado correctamente.')
    return redirect('panel_barbero')


# ================= UTILIDADES =================

def correo_prueba(request):
    if request.method == "POST":
        destino = request.POST.get("destino")
        try:
            send_mail(
                'Django SMTP prueba',
                '¡Hola! Este es un correo de prueba enviado desde Django.',
                'barberhub15@gmail.com',
                [destino if destino else 'sdiezmarulanda@gmail.com'],
                fail_silently=False,
            )
            messages.success(request, 'Correo enviado exitosamente.')
        except Exception as e:
            messages.error(request, f'Error: {e}')
        return redirect('correo_prueba')
    else:
        return render(request, "correo_prueba.html")