from datetime import date, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib.auth import logout
from .models import Barberia, Servicio, HorarioAtencion, Cita, PerfilUsuario, PlanBarbero

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
    barberias = Barberia.objects.filter(is_active=True)
    planes = PlanBarbero.objects.all() # <-- CONEXIÓN: Agregado para mostrar los planes en inicio
    return render(request, 'inicio.html', {'barberias': barberias, 'planes': planes})

def barberias(request):
    lista_barberias = Barberia.objects.filter(is_active=True).prefetch_related('horarios').all()
    return render(request, 'barberias.html', {'barberias': lista_barberias})

def soporte(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            nombre = request.user.get_full_name() or request.user.username
            correo = request.user.email
        else:
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
    perfil = getattr(request.user, 'perfilusuario', None) or getattr(request.user, 'perfil', None)
    
    if request.method == 'POST':
        nuevo_plan = request.POST.get('plan')
        if barberia and nuevo_plan:
            barberia.plan_actual = nuevo_plan
            barberia.save()
            messages.success(request, '¡Has actualizado tu plan exitosamente!')
            return redirect('pagar_plan')
            
    context = {
        'barberia': barberia,
        'nombre_cliente': request.user.get_full_name() or request.user.username,
        'email_cliente': request.user.email,
        'telefono_cliente': perfil.telefono if perfil else '',
    }
    return render(request, 'pagar_plan.html', context)


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
        barberia_seleccionada = Barberia.objects.filter(id=barberia_id, is_active=True).first()
        if barberia_seleccionada:
            servicios = barberia_seleccionada.servicios.all()
            horarios = barberia_seleccionada.horarios.all()

    if request.method == 'POST':
        nombre_cliente = request.user.get_full_name() or request.user.username
        
        perfil = getattr(request.user, 'perfilusuario', None) or getattr(request.user, 'perfil', None)
        telefono = perfil.telefono if perfil else request.POST.get('telefono', '')
        
        fecha = request.POST.get('fecha')
        hora = request.POST.get('hora')
        servicios_ids = request.POST.getlist('servicios')

        if not barberia_seleccionada:
            messages.error(request, 'Debe seleccionar una barbería válida y activa.')
            return redirect('barberias')

        if not fecha or not hora:
            messages.error(request, 'Por favor selecciona un día y un bloque de hora válido.')
            return redirect(f"{request.path}?barberia_id={barberia_id}")

        cita = Cita.objects.create(
            nombre_cliente=nombre_cliente,
            telefono=telefono,
            barberia=barberia_seleccionada,
            fecha=fecha,
            hora=hora,
            estado='PENDIENTE'
        )

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
    citas = Cita.objects.filter(
        nombre_cliente=request.user.username
    ).prefetch_related('servicios', 'barberia').order_by('-fecha', '-hora')
    
    return render(request, 'historial.html', {'citas': citas})


@login_required
def modificar_cita(request, cita_id):
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
        cita.estado = 'CANCELADA_CLIENTE'
        cita.save()
        messages.success(request, 'Has cancelado tu cita exitosamente.')

    return redirect('historial')

# ================= PANEL DE BARBERO =================

@login_required
def panel_barbero(request):
    perfil, _ = PerfilUsuario.objects.get_or_create(user=request.user)
    if perfil.rol != 'BARBERO':
        messages.warning(request, 'Esta sección es exclusiva para barberos registrados.')
        return redirect('home')

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
    citas = barberia.citas.all().order_by('-fecha', '-hora') if barberia else []

    return render(request, 'panel_barbero.html', {
        'barberia': barberia,
        'servicios': servicios,
        'horarios': horarios,
        'citas': citas
    })

@login_required
def cambiar_estado_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id, barberia__dueno=request.user)
    
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        
        if nuevo_estado == 'CONFIRMADA':
            cita.estado = 'CONFIRMADA'
            cita.save()
            messages.success(request, f'La cita de {cita.nombre_cliente} ha sido confirmada.')
        elif nuevo_estado == 'CANCELADA':
            cita.estado = 'CANCELADA_BARBERO'
            cita.save()
            messages.success(request, f'Has cancelado la cita de {cita.nombre_cliente}.')
        else:
            messages.error(request, 'Estado no válido.')
            
    return redirect('panel_barbero')

@login_required
def agregar_servicio(request):
    if request.method == 'POST':
        barberia = Barberia.objects.filter(dueno=request.user).first()
        if not barberia:
            messages.error(request, 'Primero debes registrar la información de tu barbería.')
            return redirect('panel_barbero')

        nombre = request.POST.get('nombre')
        precio_raw = request.POST.get('precio', '0')
        precio_limpio = ''.join(filter(str.isdigit, str(precio_raw)))
        precio = int(precio_limpio) if precio_limpio else 0
        
        duracion_raw = request.POST.get('duracion', 30)
        duracion = int(duracion_raw) if str(duracion_raw).isdigit() else 30
        
        if nombre:
            Servicio.objects.create(
                barberia=barberia,
                nombre=nombre,
                precio=precio,
                duracion_minutos=duracion
            )
            messages.success(request, '¡Servicio agregado exitosamente!')
        else:
            messages.error(request, 'El nombre del servicio es obligatorio.')
            
    return redirect('panel_barbero')

@login_required
def editar_servicio(request, servicio_id):
    if request.method == 'POST':
        servicio = get_object_or_404(Servicio, id=servicio_id, barberia__dueno=request.user)
        servicio.nombre = request.POST.get('nombre')
        precio_raw = request.POST.get('precio', '0')
        precio_limpio = ''.join(filter(str.isdigit, str(precio_raw)))
        servicio.precio = int(precio_limpio) if precio_limpio else 0
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

# ================= PANEL DE ADMINISTRADOR EXCLUSIVO =================

def es_admin(user):
    if not user.is_authenticated:
        return False
        
    if user.is_superuser or user.is_staff or user.username in ['juan_bonilla', 'samuel_diez', 'juan_pablo']:
        return True
        
    perfil = getattr(user, 'perfilusuario', None) or getattr(user, 'perfil', None)
    return perfil and perfil.rol == 'ADMIN'

@user_passes_test(es_admin, login_url='login')
def panel_admin_dashboard(request):
    usuarios = User.objects.all().select_related('perfil')
    barberias = Barberia.objects.all().select_related('dueno')
    planes = PlanBarbero.objects.all() # <-- CONEXIÓN: Consulta los planes para administrarlos en el panel
    return render(request, 'admin/dashboard.html', {
        'usuarios': usuarios,
        'barberias': barberias,
        'planes': planes # <-- CONEXIÓN: Los envía al template del panel de administración
    })

@user_passes_test(es_admin, login_url='login')
def toggle_usuario(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)
    if user_obj.username in ['juan_bonilla', 'samuel_diez', 'juan_pablo']:
        messages.error(request, 'No puedes desactivar a un administrador principal.')
        return redirect('panel_admin_dashboard')
    
    user_obj.is_active = not user_obj.is_active
    user_obj.save()
    
    perfil = getattr(user_obj, 'perfil', None)
    if perfil:
        perfil.is_active = user_obj.is_active
        perfil.save()
    
    messages.success(request, f'Estado del usuario {user_obj.username} actualizado.')
    return redirect('panel_admin_dashboard')

@user_passes_test(es_admin, login_url='login')
def toggle_barberia(request, barberia_id):
    barberia = get_object_or_404(Barberia, id=barberia_id)
    if request.method == 'POST':
        barberia.is_active = not barberia.is_active
        barberia.save()
        messages.success(request, f'Estado de la barbería {barberia.nombre} actualizado.')
    return redirect('panel_admin_dashboard')

@user_passes_test(es_admin, login_url='login')
def toggle_rol_barbero(request, user_id):
    usuario_objetivo = get_object_or_404(User, id=user_id)
    
    perfil = getattr(usuario_objetivo, 'perfilusuario', None) or getattr(usuario_objetivo, 'perfil', None)
    if not perfil:
        perfil = PerfilUsuario.objects.create(user=usuario_objetivo, rol='CLIENTE')
    
    if perfil.rol == 'BARBERO':
        perfil.rol = 'CLIENTE'
        messages.success(request, f"Se le quitó el rol de barbero a {usuario_objetivo.username}.")
    else:
        perfil.rol = 'BARBERO'
        messages.success(request, f"¡{usuario_objetivo.username} ahora es Barbero!")
        
    perfil.save()
    return redirect('panel_admin_dashboard')

# ================= GESTIÓN DE PLANES (NUEVAS VISTAS) =================

@user_passes_test(es_admin, login_url='login')
def editar_plan(request, plan_id):
    plan = get_object_or_404(PlanBarbero, id=plan_id)
    if request.method == 'POST':
        plan.nombre = request.POST.get('nombre')
        plan.limite_barberos = request.POST.get('limite_barberos')
        precio_raw = request.POST.get('precio', '0')
        
        # Limpieza segura del precio (remueve puntos o comas si los trae el input)
        precio_limpio = ''.join(filter(str.isdigit, str(precio_raw)))
        plan.precio = int(precio_limpio) if precio_limpio else 0
        plan.descripcion = request.POST.get('descripcion')
        plan.save()
        
        messages.success(request, f'Plan "{plan.nombre}" actualizado correctamente.')
    return redirect('panel_admin_dashboard')

@user_passes_test(es_admin, login_url='login')
def eliminar_plan(request, plan_id):
    plan = get_object_or_404(PlanBarbero, id=plan_id)
    if request.method == 'POST':
        nombre_plan = plan.nombre
        plan.delete()
        messages.success(request, f'El plan "{nombre_plan}" ha sido eliminado correctamente.')
    return redirect('panel_admin_dashboard')

@user_passes_test(es_admin, login_url='login')
def crear_plan(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        limite_barberos = request.POST.get('limite_barberos')
        precio_raw = request.POST.get('precio', '0')
        precio_limpio = ''.join(filter(str.isdigit, str(precio_raw)))
        precio = int(precio_limpio) if precio_limpio else 0
        descripcion = request.POST.get('descripcion')
        imagen = request.POST.get('imagen', '')

        if nombre:
            PlanBarbero.objects.create(
                nombre=nombre,
                limite_barberos=limite_barberos,
                precio=precio,
                descripcion=descripcion,
                imagen=imagen
            )
            messages.success(request, f'¡Plan "{nombre}" creado exitosamente!')
        else:
            messages.error(request, 'El nombre del plan es obligatorio.')
            
    return redirect('panel_admin_dashboard')