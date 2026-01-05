from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from functools import wraps
from datetime import timedelta
import calendar
import json
from .forms import RegistroForm, LoginForm, PerfilTutorForm, UserForm, MascotaForm, FichaClinicaForm, EventoClinicoForm, RecuperarClaveForm
from django import forms
from .models import PerfilTutor, Mascota, PesoMascota, FichaClinica, EventoClinico, HistorialFichaClinica, ArchivoAdjunto
from django.db.models import Q


def perfil_completo_required(view_func):
    """
    Decorador que verifica que el usuario tenga el perfil completo.
    Si no lo tiene, muestra un mensaje informativo pero permite el acceso.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        try:
            perfil = PerfilTutor.objects.only('telefono', 'ocupacion').get(user=request.user)
        except PerfilTutor.DoesNotExist:
            perfil = PerfilTutor.objects.create(user=request.user)
        
        if not perfil.perfil_completo:
            messages.info(request, 'Por favor, completa tu perfil para continuar.')
            # No redirigir forzadamente, permitir que el usuario navegue libremente
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view


def inicio_view(request):
    """Vista de la página de inicio"""
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'registro/inicio.html')


def login_view(request):
    """Vista para el login"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # Primero verificar si el perfil está completo
                try:
                    perfil = PerfilTutor.objects.only('telefono', 'ocupacion').get(user=user)
                except PerfilTutor.DoesNotExist:
                    perfil = PerfilTutor.objects.create(user=user)
                
                # Si el perfil no está completo, redirigir a completar_perfil
                if not perfil.perfil_completo:
                    messages.info(request, 'Por favor, completa tu perfil para continuar.')
                    return redirect('completar_perfil')
                
                # Solo después de completar el perfil, verificar si tiene mascotas registradas
                from .models import Mascota
                mascotas_count = Mascota.objects.filter(tutor=user).count()
                if mascotas_count == 0:
                    messages.info(request, f'¡Bienvenido, {user.first_name}! Completa la información de tu primera mascota.')
                    return redirect('registro_mascota')
                
                messages.success(request, f'¡Bienvenido, {user.first_name}!')
                return redirect('home')
            else:
                messages.error(request, 'Credenciales inválidas.')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        form = LoginForm()
    
    # Siempre pasar el formulario de recuperación para que esté disponible
    recuperar_form = RecuperarClaveForm()
    
    return render(request, 'registro/login.html', {'form': form, 'recuperar_form': recuperar_form})


def recuperar_clave_view(request):
    """Vista para recuperar contraseña"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = RecuperarClaveForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            nueva_password = form.cleaned_data.get('nueva_password')
            
            try:
                user = User.objects.get(email=email)
                user.set_password(nueva_password)
                user.save()
                messages.success(request, '¡Contraseña actualizada exitosamente! Ahora puedes iniciar sesión con tu email y la nueva contraseña.')
                return redirect('login')
            except User.DoesNotExist:
                messages.error(request, 'No existe una cuenta con ese correo electrónico.')
                # Mostrar el formulario de recuperación con errores
                login_form = LoginForm()
                return render(request, 'registro/login.html', {'form': login_form, 'recuperar_form': form, 'mostrar_recuperar': True})
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
            # Mostrar el formulario de recuperación con errores
            login_form = LoginForm()
            return render(request, 'registro/login.html', {'form': login_form, 'recuperar_form': form, 'mostrar_recuperar': True})
    else:
        form = RecuperarClaveForm()
        login_form = LoginForm()
        return render(request, 'registro/login.html', {'form': login_form, 'recuperar_form': form, 'mostrar_recuperar': True})


def registro_view(request):
    # Si el usuario ya está autenticado, verificar si intenta registrarse de nuevo
    if request.user.is_authenticated:
        if request.method == 'POST':
            # Verificar si el email y contraseña coinciden con la cuenta actual
            email = request.POST.get('email', '')
            password = request.POST.get('password1', '')
            
            if email and password:
                # Verificar si el email coincide con el usuario actual
                if request.user.email == email or request.user.username == email:
                    # Verificar si la contraseña es correcta
                    from django.contrib.auth import authenticate
                    user = authenticate(request, username=request.user.username, password=password)
                    if user is not None:
                        # La cuenta ya existe y las credenciales son correctas
                        messages.info(request, 'Esta cuenta ya está creada. Te redirigimos a completar tu perfil.')
                        return redirect('completar_perfil')
                    else:
                        messages.error(request, 'La contraseña no coincide con esta cuenta.')
                else:
                    messages.info(request, 'Ya tienes una sesión activa. Cierra sesión para crear una nueva cuenta.')
                    return redirect('completar_perfil')
            else:
                messages.info(request, 'Ya tienes una sesión activa. Te redirigimos a completar tu perfil.')
                return redirect('completar_perfil')
        else:
            # Si está autenticado y solo está viendo la página, redirigir a completar_perfil
            messages.info(request, 'Ya tienes una cuenta creada. Te redirigimos a completar tu perfil.')
            return redirect('completar_perfil')
    
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'¡Cuenta creada exitosamente! Ingresa con {user.email}')
            return redirect('completar_perfil')
        else:
            # Verificar si el error es porque el email ya existe
            email = form.data.get('email', '')
            if email:
                try:
                    existing_user = User.objects.get(email=email)
                    # Si el email existe, intentar autenticar con la contraseña proporcionada
                    password = form.data.get('password1', '')
                    if password:
                        from django.contrib.auth import authenticate
                        user = authenticate(request, username=existing_user.username, password=password)
                        if user is not None:
                            # La cuenta existe y la contraseña es correcta
                            login(request, user)
                            messages.info(request, 'Esta cuenta ya está creada. Te redirigimos a completar tu perfil.')
                            return redirect('completar_perfil')
                        else:
                            messages.error(request, 'Este correo electrónico ya está registrado, pero la contraseña no coincide.')
                    else:
                        messages.error(request, 'Este correo electrónico ya está registrado.')
                except User.DoesNotExist:
                    pass
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        form = RegistroForm()
    
    return render(request, 'registro/registro.html', {'form': form})


@login_required
@perfil_completo_required
def home_view(request):
    # Obtener el perfil completo incluyendo foto_perfil - siempre recargar desde la BD
    try:
        perfil = PerfilTutor.objects.select_related().get(user=request.user)
        perfil.refresh_from_db()  # Asegurar que tenemos los datos más recientes
    except PerfilTutor.DoesNotExist:
        perfil = PerfilTutor.objects.create(user=request.user)
    except Exception:
        # Si falla el refresh o la obtención, intentar obtener el perfil nuevamente sin refresh
        try:
            perfil = PerfilTutor.objects.get(user=request.user)
        except PerfilTutor.DoesNotExist:
            perfil = None # O manejar la creación si es necesario

    mascotas_qs = Mascota.objects.filter(tutor=request.user, activa=True).select_related('ficha_clinica').prefetch_related('pesos').order_by('nombre')
    mascotas_inactivas_qs = Mascota.objects.filter(tutor=request.user, activa=False).order_by('nombre')

    if not mascotas_qs.exists() and not mascotas_inactivas_qs.exists():
        messages.info(request, 'Necesitas registrar al menos una mascota para ver el panel.')
        return redirect('registro_mascota')

    mascotas_data = []
    total_perros = 0
    total_gatos = 0
    for mascota in mascotas_qs:
        if mascota.especie == Mascota.ESPECIE_PERRO:
            total_perros += 1
        else:
            total_gatos += 1
        color_dot = '#d2de7d'
        color_line = '#d2de7d'

        edad_anios = mascota.edad_en_anios
        if edad_anios is None:
            stage = {
                'label': 'Sin datos',
                'badge_color': '#ed99c5',
            }
        else:
            if edad_anios < 1:
                stage = {
                    'label': 'Cachorro',
                    'badge_color': '#ed99c5',
                }
            elif edad_anios < 7:
                stage = {
                    'label': 'Adulto',
                    'badge_color': '#ed99c5',
                }
            else:
                stage = {
                    'label': 'Senior',
                    'badge_color': '#ed99c5',
                }

        pesos = list(mascota.pesos.order_by('fecha'))
        historial = []
        for registro in pesos:
            historial.append({
                'mes': registro.fecha.strftime('%b'),
                'peso': float(registro.peso),
                'etiqueta': registro.fecha.strftime('%d %b'),
            })

        if historial:
            valores = [p['peso'] for p in historial]
            max_peso = max(valores)
            min_peso = min(valores)
            rango = max_peso - min_peso if max_peso != min_peso else 1
            puntos_svg = []
            total = len(historial) - 1 if len(historial) > 1 else 1
            for index, reg in enumerate(historial):
                normalizado = (reg['peso'] - min_peso) / rango
                reg['offset'] = 10 + normalizado * 70
                x = (index / total) * 100
                y = 100 - reg['offset']
                reg['svg_x'] = x
                reg['svg_y'] = y
                reg['peso_display'] = f"{reg['peso']:.1f} K"
                puntos_svg.append(f"{x},{y}")
            svg_points = ' '.join(puntos_svg)
            ultimo_peso = historial[-1]['peso']
        else:
            svg_points = ''
            ultimo_peso = '—'

        try:
            ficha = mascota.ficha_clinica
            microchip = (ficha.microchip if ficha.microchip else mascota.microchip) or 'No registrado'
        except:
            ficha = None
            microchip = mascota.microchip or 'No registrado'

        # Verificar si la bitácora está completada (peso es obligatorio)
        bitacora_completada = False
        if ficha and ficha.peso is not None:
            bitacora_completada = True

        # Calcular estado de salud basado en la bitácora (0-5)
        if not bitacora_completada:
            # Si la bitácora no está completada
            salud_score = '—'
            salud_estado = 'Completar'
            salud_detalle = 'Bitácora'
        else:
            # Calcular score de salud (0-5)
            score = 5  # Empezamos con 5 (máximo)
            
            # Reducir score por condiciones crónicas
            if ficha.condiciones_cronicas and ficha.condiciones_cronicas.strip():
                score -= 1
            
            # Reducir score por alergias
            if ficha.alergias and ficha.alergias.strip():
                score -= 0.5
            
            # Reducir score si hay medicamentos actuales (puede indicar problemas)
            if ficha.medicamentos_actuales and ficha.medicamentos_actuales.strip():
                score -= 0.5
            
            # Reducir score por historial de enfermedades
            if ficha.historial_enfermedades and ficha.historial_enfermedades.strip():
                score -= 0.5
            
            # Verificar eventos clínicos recientes (últimos 30 días)
            fecha_limite = timezone.now().date() - timedelta(days=30)
            eventos_recientes = ficha.eventos.filter(
                fecha_evento__gte=fecha_limite
            ).exclude(tipo_evento='comentario').count()
            
            if eventos_recientes > 3:
                score -= 0.5
            elif eventos_recientes > 0:
                score -= 0.25
            
            # Asegurar que el score esté entre 0 y 5
            score = max(0, min(5, score))
            
            # Determinar estado y detalle
            if score >= 4.5:
                salud_estado = 'Excelente'
                salud_detalle = 'Sin alertas'
            elif score >= 3.5:
                salud_estado = 'Muy bien'
                salud_detalle = 'Sin alertas'
            elif score >= 2.5:
                salud_estado = 'Bien'
                salud_detalle = 'Atención'
            elif score >= 1.5:
                salud_estado = 'Regular'
                salud_detalle = 'Atención'
            else:
                salud_estado = 'Revisar'
                salud_detalle = 'Atención'
            
            salud_score = f'{int(round(score))}/5'

        # Calcular estado de vacunas basado en la bitácora
        if not bitacora_completada:
            # Si la bitácora no está completada
            vacunas_resumen = '—'
            vacunas_detalle = 'Completar'
        else:
            # Obtener la última vacuna registrada
            ultima_vacuna = ficha.eventos.filter(tipo_evento='vacuna').order_by('-fecha_evento').first()
            
            # Si tiene vacunas_al_dia marcado
            if ficha.vacunas_al_dia:
                if ultima_vacuna:
                    vacunas_resumen = 'Al día'
                    vacunas_detalle = f'Última: {ultima_vacuna.fecha_evento.strftime("%d/%m/%Y")}'
                else:
                    vacunas_resumen = 'Al día'
                    vacunas_detalle = 'Completo'
            else:
                # No tiene vacunas al día
                if ultima_vacuna:
                    vacunas_resumen = 'No al día'
                    vacunas_detalle = f'Última: {ultima_vacuna.fecha_evento.strftime("%d/%m/%Y")}'
                else:
                    vacunas_resumen = 'No al día'
                    vacunas_detalle = 'Sin registro'

        edad_anios_int = int(edad_anios) if edad_anios else None
        edad_display = f"{edad_anios_int} año{'s' if edad_anios_int and edad_anios_int != 1 else ''}" if edad_anios_int is not None else mascota.edad
        
        # Obtener alergias de la ficha clínica
        alergias_display = 'No manifiesta'
        if ficha and ficha.alergias and ficha.alergias.strip():
            alergias_display = ficha.alergias
        
        mascotas_data.append({
            'id': mascota.id,
            'nombre': mascota.nombre,
            'especie': mascota.get_especie_display(),
            'especie_raw': mascota.especie,
            'raza': mascota.raza or 'Sin información',
            'fecha_nacimiento': mascota.fecha_nacimiento,
            'fecha_nacimiento_display': mascota.fecha_nacimiento.strftime('%d/%m/%Y') if mascota.fecha_nacimiento else '—',
            'edad': mascota.edad,
            'edad_anios': edad_anios_int,
            'edad_display': edad_display,
            'color_pelaje': mascota.color_pelaje or '—',
            'sexo': mascota.get_sexo_display() if mascota.sexo else 'Sin información',
            'sexo_raw': mascota.sexo,
            'esterilizado': mascota.esterilizado,
            'microchip': microchip or 'M000001',
            'alergias': alergias_display,
            'foto': mascota.foto,  # Incluir el campo foto para mostrar la imagen
            'historial_peso': historial,
            'svg_points': svg_points,
            'color_dot': color_dot,
            'color_line': color_line,
            'ultimo_peso': ultimo_peso,
            'stage': stage,
            'salud_score': salud_score,
            'salud_estado': salud_estado,
            'salud_detalle': salud_detalle,
            'vacunas_resumen': vacunas_resumen,
            'vacunas_detalle': vacunas_detalle,
        })

    mascotas_data.sort(key=lambda x: x['nombre'])

    # Preparar datos de mascotas inactivas
    mascotas_inactivas_data = []
    for mascota in mascotas_inactivas_qs:
        edad_anios_inactiva = mascota.edad_en_anios
        edad_anios_int_inactiva = int(edad_anios_inactiva) if edad_anios_inactiva else None
        edad_display_inactiva = f"{edad_anios_int_inactiva} año{'s' if edad_anios_int_inactiva and edad_anios_int_inactiva != 1 else ''}" if edad_anios_int_inactiva is not None else mascota.edad
        
        # Obtener microchip de la ficha clínica si existe
        try:
            ficha = mascota.ficha_clinica
            microchip = (ficha.microchip if ficha.microchip else mascota.microchip) or 'No registrado'
        except:
            microchip = mascota.microchip or 'No registrado'
        
        mascotas_inactivas_data.append({
            'id': mascota.id,
            'nombre': mascota.nombre,
            'especie': mascota.get_especie_display(),
            'especie_raw': mascota.especie,
            'raza': mascota.raza or 'Sin información',
            'fecha_nacimiento': mascota.fecha_nacimiento,
            'fecha_nacimiento_display': mascota.fecha_nacimiento.strftime('%d/%m/%Y') if mascota.fecha_nacimiento else '—',
            'edad': mascota.edad,
            'edad_anios': edad_anios_int_inactiva,
            'edad_display': edad_display_inactiva,
            'color_pelaje': mascota.color_pelaje or 'Sin información',
            'sexo': mascota.get_sexo_display() if mascota.sexo else 'Sin información',
            'sexo_raw': mascota.sexo,
            'esterilizado': mascota.esterilizado,
            'microchip': microchip,
            'foto': mascota.foto,  # Incluir el campo foto para mostrar la imagen
        })
    mascotas_inactivas_data.sort(key=lambda x: x['nombre'])

    # Verificar si se debe mostrar el popup de mascota agregada
    mostrar_popup = request.session.pop('mostrar_popup_mascota_home', False)
    mascota_guardada = request.session.pop('mascota_guardada_home', '')

    stats = {
        'mascotas_total': len(mascotas_data),
        'descripcion_mascotas': f"{total_perros} perro{'s' if total_perros != 1 else ''}, {total_gatos} gato{'s' if total_gatos != 1 else ''}",
        'citas_semana': 0,
        'vacunas_porcentaje': '100%' if mascotas_data else '—',
        'estado_salud': 'Excelente' if mascotas_data else 'Sin datos',
        'alerta_salud': 'Sin alertas' if mascotas_data else 'Agrega tus mascotas para ver estadísticas',
    }

    etapas_vida = [
        {
            'icono': '🐾',
            'titulo': 'Cachorro / Gatito',
            'descripcion': '0 - 12 meses · Controles frecuentes · Nutrición especial',
            'color_hex': '#d2de7d',
        },
        {
            'icono': '🐕',
            'titulo': 'Adulto',
            'descripcion': '1 - 7 años · Rutina estable · Ejercicio regular',
            'color_hex': '#e0e0e0',
        },
        {
            'icono': '🐶',
            'titulo': 'Senior',
            'descripcion': '7+ años · Controles cada 6 meses · Cuidados articulares',
            'color_hex': '#a8e3e1',
        },
        {
            'icono': '🐱',
            'titulo': 'Ciclo felino',
            'descripcion': 'Ajusta alimentación y revisiones para cada etapa',
            'color_hex': '#ed99c5',
        },
    ]

    today = timezone.now().date()
    
    # Obtener mes y año desde los parámetros GET o usar el mes actual
    mes_seleccionado = request.GET.get('mes')
    anio_seleccionado = request.GET.get('anio')
    
    if mes_seleccionado and anio_seleccionado:
        try:
            mes = int(mes_seleccionado)
            anio = int(anio_seleccionado)
            # Validar rango de mes y año
            if 1 <= mes <= 12 and 2000 <= anio <= 2100:
                fecha_calendario = timezone.datetime(anio, mes, 1).date()
            else:
                fecha_calendario = today
        except (ValueError, TypeError):
            fecha_calendario = today
    else:
        fecha_calendario = today
    
    calendar_headers = ['L', 'M', 'X', 'J', 'V', 'S', 'D']
    meses_es = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
    calendario = calendar.Calendar(firstweekday=0)
    semanas_calendario = []
    semanas_meta = []
    semana_actual = []
    first_day = timezone.datetime(fecha_calendario.year, fecha_calendario.month, 1).date()
    # Construir semanas del mes con rango de fechas
    week_index = 0
    for dia in calendario.itermonthdates(fecha_calendario.year, fecha_calendario.month):
        # Guardar la fecha completa para calcular correctamente las semanas
        if dia.month == fecha_calendario.month:
            semana_actual.append(dia)
        else:
            semana_actual.append('')
        
        if len(semana_actual) == 7:
            semanas_calendario.append([d.day if d != '' else '' for d in semana_actual])
            # Meta de semana - usar las fechas reales para el rango
            fechas_reales = [d for d in semana_actual if d != '']
            if fechas_reales:
                inicio_sem = fechas_reales[0]
                fin_sem = fechas_reales[-1]
                semanas_meta.append({
                    'index': week_index + 1,
                    'inicio': inicio_sem.strftime('%d %b'),
                    'fin': fin_sem.strftime('%d %b'),
                })
            else:
                semanas_meta.append({
                    'index': week_index + 1,
                    'inicio': '',
                    'fin': '',
                })
            semana_actual = []
            week_index += 1
    if semana_actual:
        while len(semana_actual) < 7:
            semana_actual.append('')
        semanas_calendario.append([d.day if d != '' else '' for d in semana_actual])
        fechas_reales = [d for d in semana_actual if d != '']
        if fechas_reales:
            inicio_sem = fechas_reales[0]
            fin_sem = fechas_reales[-1]
            semanas_meta.append({
                'index': week_index + 1,
                'inicio': inicio_sem.strftime('%d %b'),
                'fin': fin_sem.strftime('%d %b'),
            })
        else:
            semanas_meta.append({
                'index': week_index + 1,
                'inicio': '',
                'fin': '',
            })
    # Pares (semana, meta) para el template
    weeks_paired = list(zip(semanas_calendario, semanas_meta))
    
    # Obtener todos los eventos del mes seleccionado para todas las mascotas del usuario
    eventos_mes = EventoClinico.objects.filter(
        ficha_clinica__mascota__tutor=request.user,
        ficha_clinica__mascota__activa=True,
        fecha_evento__year=fecha_calendario.year,
        fecha_evento__month=fecha_calendario.month
    ).select_related('ficha_clinica__mascota').order_by('fecha_evento')
    
    # Crear diccionario de eventos por día
    eventos_por_dia = {}
    eventos_por_semana = {}  # Para contar TODOS los eventos por semana
    
    for evento in eventos_mes:
        dia = evento.fecha_evento.day
        if dia not in eventos_por_dia:
            eventos_por_dia[dia] = []
        # Obtener hora del evento si existe
        hora_evento = evento.hora_evento.strftime('%H:%M') if evento.hora_evento else None
        eventos_por_dia[dia].append({
            'tipo': evento.tipo_evento,
            'tipo_display': evento.get_tipo_evento_display(),
            'mascota': evento.ficha_clinica.mascota.nombre,
            'descripcion': evento.descripcion[:50] if evento.descripcion else '',
            'hora': hora_evento,
        })
        
        # Contar TODOS los eventos por semana
        semana_num = None
        for idx, (semana, meta) in enumerate(weeks_paired):
            if dia in semana:
                semana_num = idx + 1
                break
        if semana_num:
            if semana_num not in eventos_por_semana:
                eventos_por_semana[semana_num] = 0
            eventos_por_semana[semana_num] += 1
    
    # Contar eventos por semana para el template - crear diccionario indexado por número de semana
    semanas_con_eventos_dict = {}
    for idx, (semana, meta) in enumerate(weeks_paired):
        semana_num = idx + 1
        total_eventos = eventos_por_semana.get(semana_num, 0)
        semanas_con_eventos_dict[semana_num] = {
            'total': total_eventos,
            'meta': total_eventos  # Por ahora, meta = total
        }

    # Manejar formulario de eventos en el home
    evento_form = None
    if request.method == 'POST' and 'guardar_evento_home' in request.POST:
        evento_form = EventoClinicoForm(request.POST, request.FILES)
        if evento_form.is_valid():
            # Obtener la mascota seleccionada
            mascota_id = request.POST.get('mascota_id')
            if mascota_id:
                try:
                    mascota = Mascota.objects.get(pk=mascota_id, tutor=request.user, activa=True)
                    ficha, _ = FichaClinica.objects.get_or_create(mascota=mascota)
                    
                    # Validar archivos adjuntos
                    archivos_adjuntos = request.FILES.getlist('archivos')
                    archivos_validos = []
                    
                    if archivos_adjuntos:
                        formatos_permitidos = ArchivoAdjunto.FORMATOS_PERMITIDOS
                        tamano_maximo = ArchivoAdjunto.TAMANO_MAXIMO
                        
                        for archivo in archivos_adjuntos:
                            # Validar extensión
                            nombre_archivo = archivo.name
                            extension = nombre_archivo.split('.')[-1].lower() if '.' in nombre_archivo else ''
                            
                            if extension not in formatos_permitidos:
                                formatos_str = ', '.join(formatos_permitidos)
                                messages.error(request, f'El archivo "{nombre_archivo}" tiene un formato no permitido. Formatos permitidos: {formatos_str}')
                                continue
                            
                            # Validar tamaño
                            if archivo.size > tamano_maximo:
                                tamano_mb = tamano_maximo / (1024 * 1024)
                                messages.error(request, f'El archivo "{nombre_archivo}" excede el tamaño máximo permitido ({tamano_mb}MB)')
                                continue
                            
                            archivos_validos.append(archivo)
                    
                    evento = evento_form.save(commit=False, archivos_adjuntos=archivos_validos)
                    evento.ficha_clinica = ficha
                    # Asegurar que la hora se guarde correctamente
                    if evento_form.cleaned_data.get('hora_evento'):
                        evento.hora_evento = evento_form.cleaned_data['hora_evento']
                    evento.save()
                    
                    # Guardar archivos adjuntos
                    for archivo in archivos_validos:
                        extension = archivo.name.split('.')[-1].lower() if '.' in archivo.name else ''
                        ArchivoAdjunto.objects.create(
                            evento_clinico=evento,
                            nombre=archivo.name,
                            archivo=archivo,
                            tipo_archivo=extension,
                            tamano=archivo.size
                        )
                    
                    # Guardar información en sesión para mostrar el modal de éxito
                    request.session['evento_agregado'] = True
                    request.session['evento_mascota_nombre'] = mascota.nombre
                    # Calcular número de recordatorios (si está activado el checkbox)
                    activar_recordatorios = request.POST.get('activar_recordatorios') == 'on'
                    num_recordatorios = 3 if activar_recordatorios else 0
                    request.session['evento_num_recordatorios'] = num_recordatorios
                    
                    # No mostrar mensajes de éxito tradicionales, solo el modal
                    
                    # El modal de éxito se mostrará automáticamente desde la sesión
                    return redirect('home')
                except Mascota.DoesNotExist:
                    messages.error(request, 'Mascota no encontrada.')
            else:
                messages.error(request, 'Debes seleccionar una mascota.')
        else:
            messages.error(request, 'Revisa los datos del evento.')
    else:
        evento_form = EventoClinicoForm()
    
    # Verificar si hay un evento agregado exitosamente (para mostrar el modal)
    mostrar_popup_evento = request.session.pop('evento_agregado', False)
    evento_mascota_nombre = request.session.pop('evento_mascota_nombre', '')
    evento_num_recordatorios = request.session.pop('evento_num_recordatorios', 0)
    
    context = {
        'user_name': perfil.nombre_para_mostrar,
        'perfil': perfil,
        'mascotas': mascotas_data,
        'mascotas_inactivas': mascotas_inactivas_data,
        'proximas_citas': [],
        'etapas_vida': etapas_vida,
        'stats': stats,
        'calendar_headers': calendar_headers,
        'calendar_weeks': semanas_calendario,
        'weeks_paired': weeks_paired,
        'weeks_meta': semanas_meta,
        'current_month': f"{meses_es[fecha_calendario.month - 1]} {fecha_calendario.year}",
        'today': today,
        'fecha_calendario': fecha_calendario,
        'mes_calendario': fecha_calendario.month,
        'anio_calendario': fecha_calendario.year,
        'eventos_por_dia': eventos_por_dia,
        'semanas_con_eventos': semanas_con_eventos_dict,
        'total_eventos_mes': len(eventos_mes),
        'mostrar_popup': mostrar_popup,
        'mascota_guardada': mascota_guardada,
        'evento_form': evento_form,
        'mostrar_popup_evento': mostrar_popup_evento,
        'evento_mascota_nombre': evento_mascota_nombre,
        'evento_num_recordatorios': evento_num_recordatorios,
    }
    
    # Obtener el nombre del usuario y foto para el banner
    # Asegurarse de que el perfil esté actualizado (ya se hizo refresh_from_db al inicio)
    user_name = request.user.first_name or request.user.username
    foto_perfil_url = None
    
    if perfil:
        if perfil.sobrenombre and perfil.sobrenombre.strip():
            user_name = perfil.sobrenombre.strip()
        
        # Obtener la URL de la foto si existe
        if perfil.foto_perfil:
            try:
                # Asegurarse de que el archivo existe antes de obtener la URL
                foto_perfil_url = perfil.foto_perfil.url
            except (ValueError, AttributeError) as e:
                # Si hay un error, intentar recargar el perfil una vez más
                try:
                    perfil.refresh_from_db()
                    if perfil.foto_perfil:
                        foto_perfil_url = perfil.foto_perfil.url
                    else:
                        foto_perfil_url = None
                except:
                    foto_perfil_url = None
        else:
            foto_perfil_url = None
    
    context['user_name'] = user_name
    context['foto_perfil_url'] = foto_perfil_url
    
    return render(request, 'registro/home.html', context)


@login_required
def completar_perfil_view(request):
    try:
        perfil = PerfilTutor.objects.get(user=request.user)
    except PerfilTutor.DoesNotExist:
        # Crear perfil sin acceder a campos que pueden no existir
        perfil = PerfilTutor(user=request.user)
        perfil.save()

    if perfil.perfil_completo:
        return redirect('registro_mascota')
    
    if request.method == 'POST':
        # Crear formulario sin instance para evitar acceder a campos que pueden no existir
        form = PerfilTutorForm(request.POST, request.FILES)
        if form.is_valid():
            # Guardar solo los campos básicos que siempre existen
            update_fields = ['telefono', 'ocupacion']
            
            perfil.telefono = form.cleaned_data.get('telefono')
            perfil.ocupacion = form.cleaned_data.get('ocupacion')
            
            fecha_nacimiento = form.cleaned_data.get('fecha_nacimiento')
            if fecha_nacimiento:
                perfil.fecha_nacimiento = fecha_nacimiento
                update_fields.append('fecha_nacimiento')
            
            sobrenombre = form.cleaned_data.get('sobrenombre', '')
            if sobrenombre and sobrenombre.strip():
                perfil.sobrenombre = sobrenombre.strip()
                update_fields.append('sobrenombre')
            else:
                perfil.sobrenombre = None
                update_fields.append('sobrenombre')
            
            # Guardar foto de perfil si se subió una
            if 'foto_perfil' in request.FILES:
                perfil.foto_perfil = request.FILES['foto_perfil']
                update_fields.append('foto_perfil')
            
            # Intentar guardar campos adicionales solo si existen en la base de datos
            # Usar SQL directo para evitar errores si las columnas no existen
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("PRAGMA table_info(registro_perfiltutor)")
                columns = [row[1] for row in cursor.fetchall()]
                
                if 'calle' in columns and 'calle' in form.cleaned_data:
                    perfil.calle = form.cleaned_data.get('calle') or ''
                    update_fields.append('calle')
                if 'numero' in columns and 'numero' in form.cleaned_data:
                    perfil.numero = form.cleaned_data.get('numero') or ''
                    update_fields.append('numero')
                if 'ciudad' in columns and 'ciudad' in form.cleaned_data:
                    perfil.ciudad = form.cleaned_data.get('ciudad') or ''
                    update_fields.append('ciudad')
                if 'comuna' in columns and 'comuna' in form.cleaned_data:
                    perfil.comuna = form.cleaned_data.get('comuna') or ''
                    update_fields.append('comuna')
            
            # Guardar solo los campos especificados
            perfil.save(update_fields=update_fields)
            messages.success(request, f'¡Perfil completado exitosamente! Ingresa con {request.user.email}')
            return redirect('registro_mascota')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        # Crear formulario sin usar instance para evitar acceder a campos que pueden no existir
        initial_data = {}
        try:
            initial_data['telefono'] = perfil.telefono
            initial_data['ocupacion'] = perfil.ocupacion
            initial_data['sobrenombre'] = perfil.sobrenombre
            initial_data['fecha_nacimiento'] = perfil.fecha_nacimiento
        except:
            pass
        form = PerfilTutorForm(initial=initial_data)
    
    return render(request, 'registro/completar_perfil.html', {
        'form': form,
        'user_email': request.user.email,
        'user_name': request.user.first_name or request.user.username,
        'perfil': perfil
    })


@login_required
@perfil_completo_required
def perfil_view(request):
    perfil, created = PerfilTutor.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Si solo se envía la foto desde el banner (sin otros campos del formulario)
        if 'foto_perfil' in request.FILES and not request.POST.get('first_name'):
            # Actualizar solo la foto de perfil
            perfil.foto_perfil = request.FILES['foto_perfil']
            perfil.save(update_fields=['foto_perfil'])
            perfil.refresh_from_db()
            messages.success(request, 'Foto de perfil actualizada correctamente.')
            return redirect('perfil_tutor')
        
        user_form = UserForm(request.POST, instance=request.user)
        perfil_form = PerfilTutorForm(request.POST, request.FILES, instance=perfil)
        
        if user_form.is_valid() and perfil_form.is_valid():
            user_form.save()
            
            # IMPORTANTE: Guardar el formulario directamente primero para que procese el archivo
            # Django procesará automáticamente el archivo cuando guardamos el formulario completo
            perfil = perfil_form.save()
            
            # Ahora modificar el teléfono si es necesario (después de guardar la foto)
            telefono = perfil_form.cleaned_data.get('telefono', '')
            necesita_guardar_telefono = False
            if telefono:
                # Limpiar el valor de espacios y guiones
                telefono = telefono.strip().replace('-', '').replace(' ', '')
                if not telefono.startswith('+569'):
                    if telefono.startswith('569'):
                        telefono = f'+{telefono}'
                    else:
                        telefono = f'+569{telefono}'
                if perfil.telefono != telefono:
                    perfil.telefono = telefono
                    necesita_guardar_telefono = True
            elif perfil.telefono: # Si el teléfono estaba y ahora está vacío
                perfil.telefono = ''
                necesita_guardar_telefono = True
            
            # Si el teléfono cambió, guardarlo
            if necesita_guardar_telefono:
                perfil.save(update_fields=['telefono'])
            
            # Refrescar desde la BD para asegurar que tenemos la URL actualizada
            perfil.refresh_from_db()
            
            # Guardar en sesión para mostrar el modal de éxito
            request.session['mostrar_modal_perfil_actualizado'] = True
            return redirect('perfil_tutor')
        else:
            messages.error(request, 'Revisa los datos del perfil.')
    else:
        user_form = UserForm(instance=request.user)
        perfil_form = PerfilTutorForm(instance=perfil)
        
        if perfil.telefono and perfil.telefono.startswith('+569'):
            perfil_form.fields['telefono'].initial = perfil.telefono[4:]
    
    # Verificar si se debe mostrar el modal de éxito
    mostrar_modal = request.session.pop('mostrar_modal_perfil_actualizado', False)
    
    # Asegurarse de que el perfil esté actualizado desde la base de datos (incluyendo la foto)
    perfil = PerfilTutor.objects.get(pk=perfil.pk)
    
    # Actualizar el formulario con la instancia actualizada
    perfil_form = PerfilTutorForm(instance=perfil)
    if perfil.telefono and perfil.telefono.startswith('+569'):
        perfil_form.fields['telefono'].initial = perfil.telefono[4:]
    
    return render(request, 'registro/perfil.html', {
        'user_form': user_form,
        'perfil_form': perfil_form,
        'perfil': perfil,
        'user': request.user,
        'mostrar_modal': mostrar_modal,
    })


@login_required
@perfil_completo_required
def registro_mascota_view(request):
    # Usar .only() para evitar acceder a campos que pueden no existir
    try:
        perfil = PerfilTutor.objects.only('id', 'user_id').get(user=request.user)
    except PerfilTutor.DoesNotExist:
        perfil = PerfilTutor.objects.create(user=request.user)

    mascotas = Mascota.objects.filter(tutor=request.user, activa=True).order_by('nombre')
    mascotas_totales = Mascota.objects.filter(tutor=request.user).count()
    
    # Determinar si viene del flujo inicial (recién completando perfil) o es usuario establecido
    # Si no tiene mascotas y viene del flujo inicial, debe volver a completar_perfil
    # Si ya tiene mascotas o viene del home, debe volver al home
    viene_del_home = request.GET.get('from') == 'home'
    es_flujo_inicial = mascotas_totales == 0 and not viene_del_home
    
    if request.method == 'POST':
        if 'continuar' in request.POST:
            if mascotas.exists():
                return redirect('home')
            messages.error(request, 'Registra al menos una mascota antes de continuar.')
            form = MascotaForm()
        elif 'completar_despues' in request.POST:
            messages.info(request, 'Puedes registrar tus mascotas más tarde desde el panel.')
            return redirect('home')
        else:
            form = MascotaForm(request.POST, request.FILES)
            if form.is_valid():
                mascota = form.save(commit=False)
                mascota.tutor = request.user
                mascota.save()
                
                if not mascota.microchip:
                    mascota.microchip = f"M{mascota.id:06d}"
                    Mascota.objects.filter(pk=mascota.pk).update(microchip=mascota.microchip)
                    mascota.refresh_from_db()
                
                ficha, _ = FichaClinica.objects.get_or_create(mascota=mascota)
                if not ficha.microchip and mascota.microchip:
                    ficha.microchip = mascota.microchip
                    ficha.save(update_fields=['microchip'])
                
                messages.success(request, f"Mascota '{mascota.nombre}' registrada correctamente con ID: {mascota.microchip}.")
                
                # Siempre mostrar popup después de guardar una mascota
                request.session['mostrar_popup_mascota'] = True
                request.session['mascota_guardada'] = mascota.nombre
                return redirect('registro_mascota')
            else:
                messages.error(request, 'Revisa los datos ingresados.')
    else:
        form = MascotaForm()

    puede_continuar = mascotas.exists()
    
    # Verificar si se debe mostrar el popup
    mostrar_popup = request.session.pop('mostrar_popup_mascota', False)
    mascota_guardada = request.session.pop('mascota_guardada', '')

    return render(request, 'registro/registro_mascota.html', {
        'form': form,
        'mascotas': mascotas,
        'user_name': perfil.nombre_para_mostrar,
        'puede_continuar': puede_continuar,
        'mostrar_popup': mostrar_popup,
        'mascota_guardada': mascota_guardada,
        'es_flujo_inicial': es_flujo_inicial,
    })


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión correctamente.')
    return redirect('login')


@login_required
@perfil_completo_required
def bitacora_mascota_view(request, mascota_id):
    # Manejar caso en que el id no exista o no pertenezca al usuario, evitando 404 crudo
    try:
        mascota = Mascota.objects.prefetch_related('pesos').get(pk=mascota_id, tutor=request.user, activa=True)
    except Mascota.DoesNotExist:
        messages.error(request, 'No existe ninguna mascota con esa referencia o no tienes permiso para verla.')
        return redirect('home')
    ficha, _ = FichaClinica.objects.get_or_create(mascota=mascota)
    
    # Filtrado de historial clínico
    filtro_fecha_desde = request.GET.get('fecha_desde', '')
    filtro_fecha_hasta = request.GET.get('fecha_hasta', '')
    filtro_tipo_evento = request.GET.get('tipo_evento', '')
    
    # Eventos clínicos asociados a la ficha
    eventos = ficha.eventos.all()
    
    # Solo consideramos eventos que ya ocurrieron (historial),
    # las próximas citas se visualizan en el calendario.
    hoy = timezone.now().date()
    eventos = eventos.filter(fecha_evento__lte=hoy)
    
    # Aplicar filtros
    if filtro_fecha_desde:
        try:
            from datetime import datetime
            fecha_desde = datetime.strptime(filtro_fecha_desde, '%Y-%m-%d').date()
            eventos = eventos.filter(fecha_evento__gte=fecha_desde)
        except ValueError:
            pass
    
    if filtro_fecha_hasta:
        try:
            from datetime import datetime
            fecha_hasta = datetime.strptime(filtro_fecha_hasta, '%Y-%m-%d').date()
            eventos = eventos.filter(fecha_evento__lte=fecha_hasta)
        except ValueError:
            pass
    
    if filtro_tipo_evento:
        eventos = eventos.filter(tipo_evento=filtro_tipo_evento)
    
    eventos = eventos.order_by('-fecha_evento')
    # Verificar si se solicita editar
    mostrar_formulario = request.GET.get('editar') == '1'
    
    # Siempre tratamos como "nuevo registro" si ya existen datos,
    # para que se oculten campos fijos y solo se pidan variables.
    es_nuevo_registro = ficha.tiene_datos
    
    # Inicializar formulario de eventos
    evento_form = EventoClinicoForm()
    
    # Inicializar ficha_form siempre (para evitar errores cuando se accede más adelante)
    ficha_form = FichaClinicaForm(instance=ficha, mascota=mascota, es_nuevo_registro=es_nuevo_registro)

    if request.method == 'POST':
        if 'guardar_evento' in request.POST:
            # Manejar registro de evento clínico con archivos
            evento_form = EventoClinicoForm(request.POST, request.FILES)
            if evento_form.is_valid():
                # Validar archivos adjuntos
                archivos_adjuntos = request.FILES.getlist('archivos')
                archivos_validos = []
                
                if archivos_adjuntos:
                    formatos_permitidos = ArchivoAdjunto.FORMATOS_PERMITIDOS
                    tamano_maximo = ArchivoAdjunto.TAMANO_MAXIMO
                    
                    for archivo in archivos_adjuntos:
                        nombre_archivo = archivo.name
                        extension = nombre_archivo.split('.')[-1].lower() if '.' in nombre_archivo else ''
                        
                        if extension not in formatos_permitidos:
                            formatos_str = ', '.join(formatos_permitidos)
                            messages.error(request, f'El archivo "{nombre_archivo}" tiene un formato no permitido. Formatos permitidos: {formatos_str}')
                            continue
                        
                        if archivo.size > tamano_maximo:
                            tamano_mb = tamano_maximo / (1024 * 1024)
                            messages.error(request, f'El archivo "{nombre_archivo}" excede el tamaño máximo permitido ({tamano_mb}MB)')
                            continue
                        
                        archivos_validos.append(archivo)
                
                evento = evento_form.save(commit=False, archivos_adjuntos=archivos_validos)
                evento.ficha_clinica = ficha
                evento.save()
                
                # Guardar archivos adjuntos
                for archivo in archivos_validos:
                    extension = archivo.name.split('.')[-1].lower() if '.' in archivo.name else ''
                    ArchivoAdjunto.objects.create(
                        evento_clinico=evento,
                        nombre=archivo.name,
                        archivo=archivo,
                        tipo_archivo=extension,
                        tamano=archivo.size
                    )
                
                if archivos_validos:
                    messages.success(request, f'Evento registrado exitosamente con {len(archivos_validos)} archivo(s) adjunto(s).')
                else:
                    messages.success(request, 'Evento registrado exitosamente.')
                return redirect('bitacora_mascota', mascota_id=mascota.id)
            else:
                messages.error(request, 'Revisa los datos del evento.')
        elif 'guardar_vacuna' in request.POST:
            # Manejar registro de vacuna
            nombre_vacuna = request.POST.get('nombre_vacuna', '').strip()
            fecha_aplicacion = request.POST.get('fecha_aplicacion', '')
            proxima_dosis = request.POST.get('proxima_dosis', '')
            veterinario = request.POST.get('veterinario_vacuna', '').strip()
            
            if nombre_vacuna and fecha_aplicacion:
                try:
                    from datetime import datetime
                    fecha_apl = datetime.strptime(fecha_aplicacion, '%Y-%m-%d').date()
                    
                    # Crear descripción con el nombre de la vacuna y próxima dosis si existe
                    descripcion = nombre_vacuna
                    if proxima_dosis:
                        try:
                            fecha_prox = datetime.strptime(proxima_dosis, '%Y-%m-%d').date()
                            descripcion += f"\nPróxima dosis: {fecha_prox.strftime('%d/%m/%Y')}"
                        except ValueError:
                            pass
                    
                    # Crear evento de tipo vacuna
                    evento_vacuna = EventoClinico.objects.create(
                        ficha_clinica=ficha,
                        fecha_evento=fecha_apl,
                        tipo_evento='vacuna',
                        descripcion=descripcion,
                        veterinario=veterinario if veterinario else None,
                    )
                    messages.success(request, f'Vacuna "{nombre_vacuna}" registrada exitosamente.')
                    return redirect('bitacora_mascota', mascota_id=mascota.id)
                except ValueError:
                    messages.error(request, 'La fecha de aplicación no es válida.')
            else:
                messages.error(request, 'El nombre de la vacuna y la fecha de aplicación son obligatorios.')
        elif 'guardar_control' in request.POST:
            # Manejar registro de control veterinario
            tipo_consulta = request.POST.get('tipo_consulta', '').strip()
            fecha_control = request.POST.get('fecha_control', '')
            veterinario_control = request.POST.get('veterinario_control', '').strip()
            notas_control = request.POST.get('notas_control', '').strip()
            
            if tipo_consulta and fecha_control:
                try:
                    from datetime import datetime
                    fecha_ctrl = datetime.strptime(fecha_control, '%Y-%m-%d').date()
                    
                    # Crear descripción con tipo de consulta y notas
                    descripcion = tipo_consulta
                    if notas_control:
                        descripcion += f"\n{notas_control}"
                    
                    # Crear evento de tipo cita_general
                    evento_control = EventoClinico.objects.create(
                        ficha_clinica=ficha,
                        fecha_evento=fecha_ctrl,
                        tipo_evento='cita_general',
                        descripcion=descripcion,
                        veterinario=veterinario_control if veterinario_control else None,
                    )
                    messages.success(request, f'Control veterinario "{tipo_consulta}" registrado exitosamente.')
                    return redirect('bitacora_mascota', mascota_id=mascota.id)
                except ValueError:
                    messages.error(request, 'La fecha del control no es válida.')
            else:
                messages.error(request, 'El tipo de consulta y la fecha son obligatorios.')
        elif 'guardar_ficha' in request.POST:
            es_nuevo_registro_post = ficha.tiene_datos
            ficha_form = FichaClinicaForm(request.POST, request.FILES, instance=ficha, mascota=mascota, es_nuevo_registro=es_nuevo_registro_post)
            if ficha_form.is_valid():
                # Guardar foto de la mascota si se subió una
                if 'foto_mascota' in request.FILES:
                    mascota.foto = request.FILES['foto_mascota']
                    mascota.save(update_fields=['foto'])
                
                # Guardar fecha_nacimiento y color_pelaje de la mascota
                if 'fecha_nacimiento' in request.POST and request.POST['fecha_nacimiento']:
                    from datetime import datetime
                    try:
                        fecha_nac = datetime.strptime(request.POST['fecha_nacimiento'], '%Y-%m-%d').date()
                        mascota.fecha_nacimiento = fecha_nac
                        mascota.save(update_fields=['fecha_nacimiento'])
                    except ValueError:
                        pass
                
                if 'color_pelaje' in request.POST:
                    mascota.color_pelaje = request.POST['color_pelaje']
                    mascota.save(update_fields=['color_pelaje'])
                # Guardar snapshot del estado anterior antes de actualizar
                if ficha.tiene_datos:
                    # Extraer información de vacuna del comentario anterior
                    ultima_vacuna_nombre_anterior = None
                    ultima_vacuna_fecha_anterior = None
                    if ficha.comentarios and 'Última vacuna:' in ficha.comentarios:
                        import re
                        match = re.search(r'Última vacuna: ([^-]+)(?: - Fecha: (\d{2}/\d{2}/\d{4}))?', ficha.comentarios)
                        if match:
                            ultima_vacuna_nombre_anterior = match.group(1).strip()
                            if match.group(2):
                                from datetime import datetime
                                try:
                                    ultima_vacuna_fecha_anterior = datetime.strptime(match.group(2), '%d/%m/%Y').date()
                                except:
                                    pass
                    
                    # Crear registro histórico
                    HistorialFichaClinica.objects.create(
                        ficha_clinica=ficha,
                        tipo_sangre=ficha.tipo_sangre,
                        peso=ficha.peso,
                        temperatura=ficha.temperatura,
                        esterilizado=ficha.esterilizado,
                        vacunas_al_dia=ficha.vacunas_al_dia,
                        vacuna_nombre=ultima_vacuna_nombre_anterior,
                        vacuna_fecha=ultima_vacuna_fecha_anterior,
                        alergias=ficha.alergias,
                        condiciones_cronicas=ficha.condiciones_cronicas,
                        medicamentos_actuales=ficha.medicamentos_actuales,
                        historial_enfermedades=ficha.historial_enfermedades,
                        comentarios=ficha.comentarios,
                    )
                
                ficha = ficha_form.save()
                # Manejar el campo no_tengo_temperatura (no está en el modelo)
                if request.POST.get('no_tengo_temperatura'):
                    ficha.temperatura = None
                    ficha.save(update_fields=['temperatura'])
                # Manejar el campo no_tengo_vacunas
                if request.POST.get('no_tengo_vacunas'):
                    ficha.vacunas_al_dia = False
                    ficha.save(update_fields=['vacunas_al_dia'])
                # Los campos ultima_vacuna_nombre y ultima_vacuna_fecha se guardan en comentarios
                # (no están en el modelo, se procesan en clean())
                if ficha.microchip and mascota.microchip != ficha.microchip:
                    mascota.microchip = ficha.microchip
                    mascota.save(update_fields=['microchip'])
                messages.success(request, 'Ficha clínica guardada exitosamente.')
                return redirect('bitacora_mascota', mascota_id=mascota.id)
            else:
                messages.error(request, 'Revisa los datos de la bitácora.')
                mostrar_formulario = True
        elif 'subir_archivo_ficha' in request.POST:
            # Manejar subida de archivos desde la sección de archivos adjuntos
            archivos_adjuntos = request.FILES.getlist('archivos_ficha')
            archivos_validos = []
            
            if archivos_adjuntos:
                formatos_permitidos = ArchivoAdjunto.FORMATOS_PERMITIDOS
                tamano_maximo = ArchivoAdjunto.TAMANO_MAXIMO
                
                for archivo in archivos_adjuntos:
                    nombre_archivo = archivo.name
                    extension = nombre_archivo.split('.')[-1].lower() if '.' in nombre_archivo else ''
                    
                    if extension not in formatos_permitidos:
                        formatos_str = ', '.join(formatos_permitidos)
                        messages.error(request, f'El archivo "{nombre_archivo}" tiene un formato no permitido. Formatos permitidos: {formatos_str}')
                        continue
                    
                    if archivo.size > tamano_maximo:
                        tamano_mb = tamano_maximo / (1024 * 1024)
                        messages.error(request, f'El archivo "{nombre_archivo}" excede el tamaño máximo permitido ({tamano_mb}MB)')
                        continue
                    
                    archivos_validos.append(archivo)
                
                if archivos_validos:
                    # Crear un evento de tipo comentario para los archivos
                    from datetime import date
                    evento_archivos = EventoClinico.objects.create(
                        ficha_clinica=ficha,
                        fecha_evento=date.today(),
                        tipo_evento=EventoClinico.TIPO_COMENTARIO,
                        descripcion='Archivos adjuntos a la bitácora'
                    )
                    
                    # Guardar archivos adjuntos
                    for archivo in archivos_validos:
                        extension = archivo.name.split('.')[-1].lower() if '.' in archivo.name else ''
                        ArchivoAdjunto.objects.create(
                            evento_clinico=evento_archivos,
                            nombre=archivo.name,
                            archivo=archivo,
                            tipo_archivo=extension,
                            tamano=archivo.size
                        )
                    
                    messages.success(request, f'{len(archivos_validos)} archivo(s) subido(s) correctamente.')
            else:
                messages.info(request, 'No se seleccionaron archivos para subir.')
            
            return redirect('bitacora_mascota', mascota_id=mascota.id)
        elif 'eliminar_registro' in request.POST:
            # Eliminar un registro histórico específico (o el último si no se especifica)
            registro_id = request.POST.get('registro_id')
            try:
                if registro_id:
                    registro = ficha.historial_registros.get(pk=registro_id)
                else:
                    registro = ficha.historial_registros.order_by('-creado_en').first()
                if registro:
                    registro.delete()
                    messages.success(request, 'Registro eliminado correctamente.')
                else:
                    messages.info(request, 'No hay registros para eliminar.')
            except Exception:
                messages.error(request, 'No se pudo eliminar el registro.')
            return redirect('bitacora_mascota', mascota_id=mascota.id)
    else:
        ficha_form = FichaClinicaForm(instance=ficha, mascota=mascota, es_nuevo_registro=es_nuevo_registro)
        if not mascota.microchip or (isinstance(mascota.microchip, str) and not mascota.microchip.strip()):
            mascota.microchip = f"M{mascota.id:06d}"
            Mascota.objects.filter(pk=mascota.pk).update(microchip=mascota.microchip)
            mascota.refresh_from_db()
        
        if not ficha.microchip or (isinstance(ficha.microchip, str) and not ficha.microchip.strip()):
            ficha.microchip = mascota.microchip
            ficha.save(update_fields=['microchip'])
        
        ficha_form.fields['microchip'].initial = mascota.microchip
        
        # Si la temperatura es None, marcar el checkbox "no tengo temperatura"
        if ficha.temperatura is None:
            ficha_form.fields['no_tengo_temperatura'].initial = True
    
    # Extraer información de vacunas de comentarios (para ambos casos: GET y POST)
    ultima_vacuna_nombre = None
    ultima_vacuna_fecha_str = None
    if ficha.comentarios and 'Última vacuna:' in ficha.comentarios:
        import re
        match = re.search(r'Última vacuna: ([^-]+)(?: - Fecha: (\d{2}/\d{2}/\d{4}))?', ficha.comentarios)
        if match:
            ultima_vacuna_nombre = match.group(1).strip()
            if match.group(2):
                ultima_vacuna_fecha_str = match.group(2).strip()
    
    # Extraer información de esterilizado
    esterilizado_display = 'Desconocido'
    if ficha.esterilizado is True:
        esterilizado_display = 'Sí'
    elif ficha.esterilizado is False:
        esterilizado_display = 'No'
    
    # Extraer información de vacunas para display
    vacunas_display = 'Desconocido'
    if ficha.vacunas_al_dia:
        vacunas_display = 'Sí'
    elif ultima_vacuna_nombre:
        vacunas_display = ultima_vacuna_nombre
    elif not ficha.vacunas_al_dia and ficha.vacunas_al_dia is not None:
        vacunas_display = 'No'

    # Obtener historial de registros en orden ascendente (antiguo arriba, nuevo abajo)
    historial_registros = ficha.historial_registros.all().order_by('creado_en')[:50]

    # Contar total de registros
    total_registros = ficha.historial_registros.count()
    
    # Último registro histórico (para acciones rápidas como eliminar)
    ultimo_registro_hist = ficha.historial_registros.order_by('-creado_en').first()
    ultimo_registro_id = ultimo_registro_hist.id if ultimo_registro_hist else None
    
    # Verificar si los campos fijos están ocultos
    tipo_sangre_oculto = isinstance(ficha_form.fields.get('tipo_sangre', None).widget, forms.HiddenInput) if 'tipo_sangre' in ficha_form.fields else False
    esterilizado_oculto = isinstance(ficha_form.fields.get('esterilizado', None).widget, forms.HiddenInput) if 'esterilizado' in ficha_form.fields else False
    
    # Obtener eventos con archivos adjuntos para mostrar en el historial
    eventos_con_archivos = []
    todos_los_archivos = []  # Para la sección de archivos adjuntos
    for evento in eventos:
        archivos = evento.archivos_adjuntos.all()
        eventos_con_archivos.append({
            'evento': evento,
            'archivos': archivos,
        })
        # Recopilar todos los archivos
        for archivo in archivos:
            todos_los_archivos.append({
                'archivo': archivo,
                'evento': evento,
            })
    
    # Ordenar archivos por fecha de subida (más recientes primero)
    todos_los_archivos.sort(key=lambda x: x['archivo'].fecha_subida, reverse=True)
    
    # ========== LÓGICA DEL CALENDARIO (similar a home_view) ==========
    today = timezone.now().date()
    
    # Obtener mes y año desde los parámetros GET o usar el mes actual
    mes_seleccionado = request.GET.get('mes')
    anio_seleccionado = request.GET.get('anio')
    
    if mes_seleccionado and anio_seleccionado:
        try:
            mes = int(mes_seleccionado)
            anio = int(anio_seleccionado)
            if 1 <= mes <= 12 and 2000 <= anio <= 2100:
                fecha_calendario = timezone.datetime(anio, mes, 1).date()
            else:
                fecha_calendario = today
        except (ValueError, TypeError):
            fecha_calendario = today
    else:
        fecha_calendario = today
    
    meses_es = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
    calendario = calendar.Calendar(firstweekday=0)
    semanas_calendario = []
    semanas_meta = []
    semana_actual = []
    
    # Construir semanas del mes con rango de fechas
    week_index = 0
    for dia in calendario.itermonthdates(fecha_calendario.year, fecha_calendario.month):
        if dia.month == fecha_calendario.month:
            semana_actual.append(dia)
        else:
            semana_actual.append('')
        
        if len(semana_actual) == 7:
            semanas_calendario.append([d.day if d != '' else '' for d in semana_actual])
            fechas_reales = [d for d in semana_actual if d != '']
            if fechas_reales:
                inicio_sem = fechas_reales[0]
                fin_sem = fechas_reales[-1]
                semanas_meta.append({
                    'index': week_index + 1,
                    'inicio': inicio_sem.strftime('%d %b'),
                    'fin': fin_sem.strftime('%d %b'),
                })
            else:
                semanas_meta.append({
                    'index': week_index + 1,
                    'inicio': '',
                    'fin': '',
                })
            semana_actual = []
            week_index += 1
    if semana_actual:
        while len(semana_actual) < 7:
            semana_actual.append('')
        semanas_calendario.append([d.day if d != '' else '' for d in semana_actual])
        fechas_reales = [d for d in semana_actual if d != '']
        if fechas_reales:
            inicio_sem = fechas_reales[0]
            fin_sem = fechas_reales[-1]
            semanas_meta.append({
                'index': week_index + 1,
                'inicio': inicio_sem.strftime('%d %b'),
                'fin': fin_sem.strftime('%d %b'),
            })
        else:
            semanas_meta.append({
                'index': week_index + 1,
                'inicio': '',
                'fin': '',
            })
    
    weeks_paired = list(zip(semanas_calendario, semanas_meta))
    
    # Obtener eventos del mes seleccionado solo para esta mascota específica en la bitácora
    eventos_mes = EventoClinico.objects.filter(
        ficha_clinica__mascota=mascota,
        fecha_evento__year=fecha_calendario.year,
        fecha_evento__month=fecha_calendario.month
    ).select_related('ficha_clinica__mascota').order_by('fecha_evento', 'hora_evento')
    
    # Crear diccionario de eventos por día
    eventos_por_dia = {}
    for evento in eventos_mes:
        dia = evento.fecha_evento.day
        if dia not in eventos_por_dia:
            eventos_por_dia[dia] = []
        hora_evento = evento.hora_evento.strftime('%H:%M') if evento.hora_evento else None
        eventos_por_dia[dia].append({
            'id': evento.id,
            'tipo': evento.tipo_evento,
            'tipo_display': evento.get_tipo_evento_display(),
            'mascota': evento.ficha_clinica.mascota.nombre,
            'descripcion': evento.descripcion[:50] if evento.descripcion else '',
            'hora': hora_evento,
        })
    
    # Obtener todas las mascotas del usuario para el modal de eventos
    todas_las_mascotas = Mascota.objects.filter(tutor=request.user, activa=True).order_by('nombre')
    
    # Manejar formulario de eventos en la bitácora (similar a home)
    mostrar_popup_evento = False
    evento_mascota_nombre = ''
    evento_num_recordatorios = 0
    if request.method == 'POST' and 'guardar_evento_home' in request.POST:
        evento_form = EventoClinicoForm(request.POST, request.FILES)
        if evento_form.is_valid():
            mascota_id = request.POST.get('mascota_id')
            if mascota_id:
                try:
                    mascota_evento = Mascota.objects.get(pk=mascota_id, tutor=request.user, activa=True)
                    ficha_evento, _ = FichaClinica.objects.get_or_create(mascota=mascota_evento)
                    
                    archivos_adjuntos = request.FILES.getlist('archivos')
                    archivos_validos = []
                    
                    if archivos_adjuntos:
                        formatos_permitidos = ArchivoAdjunto.FORMATOS_PERMITIDOS
                        tamano_maximo = ArchivoAdjunto.TAMANO_MAXIMO
                        
                        for archivo in archivos_adjuntos:
                            nombre_archivo = archivo.name
                            extension = nombre_archivo.split('.')[-1].lower() if '.' in nombre_archivo else ''
                            
                            if extension not in formatos_permitidos:
                                formatos_str = ', '.join(formatos_permitidos)
                                messages.error(request, f'El archivo "{nombre_archivo}" tiene un formato no permitido. Formatos permitidos: {formatos_str}')
                                continue
                            
                            if archivo.size > tamano_maximo:
                                tamano_mb = tamano_maximo / (1024 * 1024)
                                messages.error(request, f'El archivo "{nombre_archivo}" excede el tamaño máximo permitido ({tamano_mb}MB)')
                                continue
                            
                            archivos_validos.append(archivo)
                    
                    evento = evento_form.save(commit=False, archivos_adjuntos=archivos_validos)
                    evento.ficha_clinica = ficha_evento
                    evento.save()
                    
                    for archivo in archivos_validos:
                        extension = archivo.name.split('.')[-1].lower() if '.' in archivo.name else ''
                        ArchivoAdjunto.objects.create(
                            evento_clinico=evento,
                            nombre=archivo.name,
                            archivo=archivo,
                            tipo_archivo=extension,
                            tamano=archivo.size
                        )
                    
                    mostrar_popup_evento = True
                    evento_mascota_nombre = mascota_evento.nombre
                    evento_num_recordatorios = 0  # Por ahora, no hay recordatorios implementados
                    
                    # Redirigir para recargar el calendario con el nuevo evento
                    return redirect('bitacora_mascota', mascota_id=mascota.id)
                except Mascota.DoesNotExist:
                    messages.error(request, 'La mascota seleccionada no existe.')
            else:
                messages.error(request, 'Debes seleccionar una mascota.')
        else:
            messages.error(request, 'Revisa los datos del evento.')
    else:
        # Si no hay POST, inicializar el formulario
        evento_form = EventoClinicoForm()
    
    # ========== FIN LÓGICA DEL CALENDARIO ==========
    
    # ========== LÓGICA DE EVOLUCIÓN DEL PESO ==========
    # Mapeo de meses en español
    meses_es_peso = {
        1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
    }
    
    # Historial de peso desde registros de peso
    historial_peso = []
    historial_peso_json = []
    pesos = mascota.pesos.order_by('fecha')
    for registro in pesos:
        historial_peso.append({
            'id': registro.id,
            'fecha': registro.fecha,
            'fecha_display': registro.fecha.strftime('%d/%m/%Y'),
            'mes_abrev': meses_es_peso.get(registro.fecha.month, registro.fecha.strftime('%b')),
            'peso': float(registro.peso),
        })
        historial_peso_json.append({
            'fecha': registro.fecha.strftime('%Y-%m-%d'),
            'peso': float(registro.peso),
        })
    
    # Agregar peso del historial de registros clínicos
    historial_registros_qs = ficha.historial_registros.all().order_by('creado_en')
    for registro in historial_registros_qs:
        if registro.peso:
            fecha_registro = registro.creado_en.date()
            historial_peso.append({
                'id': None,
                'fecha': fecha_registro,
                'fecha_display': fecha_registro.strftime('%d/%m/%Y'),
                'mes_abrev': meses_es_peso.get(fecha_registro.month, fecha_registro.strftime('%b')),
                'peso': float(registro.peso),
            })
            historial_peso_json.append({
                'fecha': fecha_registro.strftime('%Y-%m-%d'),
                'peso': float(registro.peso),
            })
    
    # Agregar peso actual si existe
    if ficha.peso:
        fecha_actual = ficha.actualizado_en.date()
        historial_peso.append({
            'id': None,
            'fecha': fecha_actual,
            'fecha_display': fecha_actual.strftime('%d/%m/%Y'),
            'mes_abrev': meses_es_peso.get(fecha_actual.month, fecha_actual.strftime('%b')),
            'peso': float(ficha.peso),
        })
        historial_peso_json.append({
            'fecha': fecha_actual.strftime('%Y-%m-%d'),
            'peso': float(ficha.peso),
        })
    
    # Ordenar por fecha (ascendente para el gráfico)
    historial_peso.sort(key=lambda x: x['fecha'])
    historial_peso_json.sort(key=lambda x: x['fecha'])
    
    # Crear lista de últimos registros ordenada descendente (más reciente primero)
    ultimos_registros_peso = sorted(historial_peso, key=lambda x: x['fecha'], reverse=True)
    historial_peso_json = json.dumps(historial_peso_json)
    
    # Cambio total de peso
    cambio_peso_display = None
    if len(historial_peso) >= 2:
        peso_inicial = historial_peso[0]['peso']
        peso_final = historial_peso[-1]['peso']
        delta = peso_final - peso_inicial
        signo = '+' if delta > 0 else ('-' if delta < 0 else '±')
        cambio_peso_display = f"{signo}{abs(delta):.1f} kg ({peso_inicial:.1f} kg → {peso_final:.1f} kg)"
    # ========== FIN LÓGICA DE EVOLUCIÓN DEL PESO ==========
    
    # Obtener última vacuna y próxima visita
    ultima_vacuna = ficha.eventos.filter(tipo_evento='vacuna').order_by('-fecha_evento').first()
    proximas_visitas = ficha.eventos.filter(
        tipo_evento__in=['cita_general', 'cita_especialista'],
        fecha_evento__gte=hoy
    ).order_by('fecha_evento')
    proxima_visita = proximas_visitas.first()
    
    # ========== LÓGICA DE REGISTRO DE VACUNAS ==========
    eventos_vacunas_raw = ficha.eventos.filter(tipo_evento='vacuna').order_by('-fecha_evento')
    eventos_vacunas = []
    hoy_date = timezone.now().date()
    
    for evento in eventos_vacunas_raw:
        # Extraer nombre de la vacuna de la descripción o usar "Vacuna" por defecto
        nombre_vacuna = evento.descripcion.split('\n')[0].strip() if evento.descripcion else 'Vacuna'
        if not nombre_vacuna or nombre_vacuna == '':
            nombre_vacuna = 'Vacuna'
        
        # Calcular próxima fecha (asumiendo 1 año después de la aplicación)
        fecha_aplicada = evento.fecha_evento
        from datetime import timedelta
        proxima_fecha = fecha_aplicada + timedelta(days=365)
        es_proxima = proxima_fecha > hoy_date
        
        eventos_vacunas.append({
            'id': evento.id,
            'nombre': nombre_vacuna,
            'fecha_aplicada': fecha_aplicada,
            'proxima_fecha': proxima_fecha if es_proxima else None,
            'veterinario': evento.veterinario or '',
            'es_proxima': es_proxima,
        })
    # ========== FIN LÓGICA DE REGISTRO DE VACUNAS ==========
    
    # ========== LÓGICA DE CONTROLES VETERINARIOS ==========
    eventos_controles_raw = ficha.eventos.filter(
        tipo_evento__in=['cita_general', 'cita_especialista']
    ).order_by('-fecha_evento')
    eventos_controles = []
    
    for evento in eventos_controles_raw:
        # Extraer tipo de consulta de la descripción o usar el tipo de evento
        tipo_consulta = evento.descripcion.split('\n')[0].strip() if evento.descripcion else evento.get_tipo_evento_display()
        if not tipo_consulta or tipo_consulta == '':
            tipo_consulta = evento.get_tipo_evento_display()
        
        eventos_controles.append({
            'id': evento.id,
            'tipo': tipo_consulta,
            'fecha': evento.fecha_evento,
            'veterinario': evento.veterinario or '',
            'descripcion': evento.descripcion or '',
        })
    # ========== FIN LÓGICA DE CONTROLES VETERINARIOS ==========
    
    return render(request, 'registro/bitacora_mascota.html', {
        'mascota': mascota,
        'ficha_form': ficha_form,
        'evento_form': evento_form,
        'ficha': ficha,
        'mostrar_formulario': mostrar_formulario,
        'es_nuevo_registro': es_nuevo_registro,
        'tipo_sangre_oculto': tipo_sangre_oculto,
        'esterilizado_oculto': esterilizado_oculto,
        'ultima_vacuna_nombre': ultima_vacuna_nombre,
        'ultima_vacuna_fecha_str': ultima_vacuna_fecha_str,
        'esterilizado_display': esterilizado_display,
        'vacunas_display': vacunas_display,
        'historial_registros': historial_registros,
        'total_registros': total_registros,
        'ultimo_registro_id': ultimo_registro_id,
        'eventos_con_archivos': eventos_con_archivos,
        'todos_los_archivos': todos_los_archivos,
        'filtro_fecha_desde': filtro_fecha_desde,
        'filtro_fecha_hasta': filtro_fecha_hasta,
        'filtro_tipo_evento': filtro_tipo_evento,
        'tipos_evento_choices': EventoClinico.TIPO_EVENTO_CHOICES,
        # Variables del calendario
        'weeks_paired': weeks_paired,
        'current_month': f"{meses_es[fecha_calendario.month - 1]} {fecha_calendario.year}",
        'fecha_calendario': fecha_calendario,
        'eventos_por_dia': eventos_por_dia,
        'total_eventos_mes': len(eventos_mes),
        'todas_las_mascotas': todas_las_mascotas,
        'mostrar_popup_evento': mostrar_popup_evento,
        'evento_mascota_nombre': evento_mascota_nombre,
        'evento_num_recordatorios': evento_num_recordatorios,
        # Variables de evolución del peso
        'historial_peso_json': historial_peso_json,
        'ultimos_registros_peso': ultimos_registros_peso,
        'cambio_peso_display': cambio_peso_display,
        # Variables de vacunas y visitas
        'ultima_vacuna': ultima_vacuna,
        'proxima_visita': proxima_visita,
        'eventos_vacunas': eventos_vacunas,
        'eventos_controles': eventos_controles,
    })


@login_required
@perfil_completo_required
def perfil_mascota_view(request, mascota_id):
    try:
        mascota = Mascota.objects.prefetch_related('pesos').get(pk=mascota_id, tutor=request.user, activa=True)
    except Mascota.DoesNotExist:
        messages.error(request, 'No existe ninguna mascota con esa referencia o no tienes permiso para verla.')
        return redirect('home')
    ficha, _ = FichaClinica.objects.get_or_create(mascota=mascota)
    
    # Crear evento desde el calendario (modal)
    if request.method == 'POST':
        if request.POST.get('agregar_evento_perfil') == '1':
            evento_form_perfil = EventoClinicoForm(request.POST, request.FILES)
            fecha_str = request.POST.get('fecha_evento_perfil')
            if evento_form_perfil.is_valid() and fecha_str:
                try:
                    from datetime import datetime
                    fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
                    
                    # Validar archivos adjuntos
                    archivos_adjuntos = request.FILES.getlist('archivos')
                    archivos_validos = []
                    
                    if archivos_adjuntos:
                        formatos_permitidos = ArchivoAdjunto.FORMATOS_PERMITIDOS
                        tamano_maximo = ArchivoAdjunto.TAMANO_MAXIMO
                        
                        for archivo in archivos_adjuntos:
                            nombre_archivo = archivo.name
                            extension = nombre_archivo.split('.')[-1].lower() if '.' in nombre_archivo else ''
                            
                            if extension not in formatos_permitidos:
                                continue
                            if archivo.size > tamano_maximo:
                                continue
                            
                            archivos_validos.append(archivo)
                    
                    evento = evento_form_perfil.save(commit=False, archivos_adjuntos=archivos_validos)
                    evento.ficha_clinica = ficha
                    evento.fecha_evento = fecha
                    evento.save()
                    
                    # Guardar archivos adjuntos
                    for archivo in archivos_validos:
                        extension = archivo.name.split('.')[-1].lower() if '.' in archivo.name else ''
                        ArchivoAdjunto.objects.create(
                            evento_clinico=evento,
                            nombre=archivo.name,
                            archivo=archivo,
                            tipo_archivo=extension,
                            tamano=archivo.size
                        )
                    
                    messages.success(request, 'Evento agregado al calendario.')
                except Exception:
                    messages.error(request, 'No se pudo agregar el evento.')
            else:
                messages.error(request, 'Revisa los datos del evento.')
            return redirect('perfil_mascota', mascota_id=mascota.id)
        elif request.POST.get('guardar_evento') == '1':
            evento_form = EventoClinicoForm(request.POST, request.FILES)
            if evento_form.is_valid():
                # Validar archivos adjuntos
                archivos_adjuntos = request.FILES.getlist('archivos')
                archivos_validos = []
                
                if archivos_adjuntos:
                    formatos_permitidos = ArchivoAdjunto.FORMATOS_PERMITIDOS
                    tamano_maximo = ArchivoAdjunto.TAMANO_MAXIMO
                    
                    for archivo in archivos_adjuntos:
                        nombre_archivo = archivo.name
                        extension = nombre_archivo.split('.')[-1].lower() if '.' in nombre_archivo else ''
                        
                        if extension not in formatos_permitidos:
                            formatos_str = ', '.join(formatos_permitidos)
                            messages.error(request, f'El archivo "{nombre_archivo}" tiene un formato no permitido. Formatos permitidos: {formatos_str}')
                            continue
                        
                        if archivo.size > tamano_maximo:
                            tamano_mb = tamano_maximo / (1024 * 1024)
                            messages.error(request, f'El archivo "{nombre_archivo}" excede el tamaño máximo permitido ({tamano_mb}MB)')
                            continue
                        
                        archivos_validos.append(archivo)
                
                evento = evento_form.save(commit=False, archivos_adjuntos=archivos_validos)
                evento.ficha_clinica = ficha
                evento.save()
                
                # Guardar archivos adjuntos
                for archivo in archivos_validos:
                    extension = archivo.name.split('.')[-1].lower() if '.' in archivo.name else ''
                    ArchivoAdjunto.objects.create(
                        evento_clinico=evento,
                        nombre=archivo.name,
                        archivo=archivo,
                        tipo_archivo=extension,
                        tamano=archivo.size
                    )
                
                if archivos_validos:
                    messages.success(request, f'Evento registrado exitosamente con {len(archivos_validos)} archivo(s) adjunto(s).')
                else:
                    messages.success(request, 'Evento registrado exitosamente.')
                return redirect('perfil_mascota', mascota_id=mascota.id)
            else:
                messages.error(request, 'Revisa los datos del evento.')
    
    # Última visita veterinario (excluyendo comentarios)
    ultima_visita_veterinario = ficha.eventos.exclude(tipo_evento='comentario').order_by('-fecha_evento').first()
    
    # Próxima visita veterinario (eventos futuros más cercanos)
    today = timezone.now().date()
    proximas_visitas = ficha.eventos.filter(
        tipo_evento__in=[EventoClinico.TIPO_CITA_GENERAL, EventoClinico.TIPO_CITA_ESPECIALISTA],
        fecha_evento__gte=today
    ).order_by('fecha_evento', 'hora_evento')
    proxima_visita_veterinario = proximas_visitas.first()
    
    # Calcular datos para el perfil
    bitacora_completada = ficha.tiene_datos
    
    # Calcular score de salud (simplificado)
    salud_score = 0
    if ficha.esterilizado:
        salud_score += 1
    if ficha.vacunas_al_dia:
        salud_score += 1
    if ficha.peso:
        salud_score += 1
    if ficha.temperatura:
        salud_score += 1
    if not ficha.alergias and not ficha.condiciones_cronicas:
        salud_score += 1
    
    # Última vacuna
    ultima_vacuna = ficha.eventos.filter(tipo_evento=EventoClinico.TIPO_VACUNA).order_by('-fecha_evento').first()
    
    # Extraer información de vacunas de comentarios
    ultima_vacuna_nombre = None
    ultima_vacuna_fecha_str = None
    if ficha.comentarios and 'Última vacuna:' in ficha.comentarios:
        import re
        match = re.search(r'Última vacuna: ([^-]+)(?: - Fecha: (\d{2}/\d{2}/\d{4}))?', ficha.comentarios)
        if match:
            ultima_vacuna_nombre = match.group(1).strip()
            if match.group(2):
                ultima_vacuna_fecha_str = match.group(2).strip()
    
    # Calcular etapa de vida
    edad_anios = mascota.edad_en_anios
    if edad_anios is None:
        etapa_label = 'Sin datos'
    elif edad_anios < 1:
        etapa_label = 'Cachorro' if mascota.especie == Mascota.ESPECIE_PERRO else 'Gatito'
    elif edad_anios < 7:
        etapa_label = 'Adulto'
    else:
        etapa_label = 'Senior'
    
    # Mapeo de meses en español
    meses_es = {
        1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
    }
    
    # Historial de peso desde registros de peso
    historial_peso = []
    historial_peso_json = []
    pesos = mascota.pesos.order_by('fecha')
    for registro in pesos:
        historial_peso.append({
            'id': registro.id,
            'fecha': registro.fecha,
            'fecha_display': registro.fecha.strftime('%d/%m/%Y'),
            'mes_abrev': meses_es.get(registro.fecha.month, registro.fecha.strftime('%b')),
            'peso': float(registro.peso),
        })
        historial_peso_json.append({
            'fecha': registro.fecha.strftime('%Y-%m-%d'),
            'peso': float(registro.peso),
        })
    
    # Obtener historial de registros clínicos (QuerySet primero para cálculos)
    historial_registros_qs = ficha.historial_registros.all().order_by('creado_en')
    
    # Mapeo de meses en español
    meses_es = {
        1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
    }
    
    # Agregar peso del historial de registros clínicos
    for registro in historial_registros_qs:
        if registro.peso:
            fecha_registro = registro.creado_en.date()
            historial_peso.append({
                'id': None,  # No tiene ID porque viene de historial clínico
                'fecha': fecha_registro,
                'fecha_display': fecha_registro.strftime('%d/%m/%Y'),
                'mes_abrev': meses_es.get(fecha_registro.month, fecha_registro.strftime('%b')),
                'peso': float(registro.peso),
            })
            historial_peso_json.append({
                'fecha': fecha_registro.strftime('%Y-%m-%d'),
                'peso': float(registro.peso),
            })
    
    # Agregar peso actual si existe
    if ficha.peso:
        fecha_actual = ficha.actualizado_en.date()
        historial_peso.append({
            'id': None,  # No tiene ID porque viene de ficha clínica
            'fecha': fecha_actual,
            'fecha_display': fecha_actual.strftime('%d/%m/%Y'),
            'mes_abrev': meses_es.get(fecha_actual.month, fecha_actual.strftime('%b')),
            'peso': float(ficha.peso),
        })
        historial_peso_json.append({
            'fecha': fecha_actual.strftime('%Y-%m-%d'),
            'peso': float(ficha.peso),
        })
    
    # Ordenar por fecha (ascendente para el gráfico)
    historial_peso.sort(key=lambda x: x['fecha'])
    historial_peso_json.sort(key=lambda x: x['fecha'])
    
    # Crear lista de últimos registros ordenada descendente (más reciente primero)
    ultimos_registros_peso = sorted(historial_peso, key=lambda x: x['fecha'], reverse=True)
    historial_peso_json = json.dumps(historial_peso_json)
    # Cambio total de peso
    cambio_peso_display = None
    if len(historial_peso) >= 2:
        peso_inicial = historial_peso[0]['peso']
        peso_final = historial_peso[-1]['peso']
        delta = peso_final - peso_inicial
        signo = '+' if delta > 0 else ('-' if delta < 0 else '±')
        cambio_peso_display = f"{signo}{abs(delta):.1f} kg  ({peso_inicial:.1f} kg → {peso_final:.1f} kg)"
    
    # Historial de temperatura para gráficos
    historial_temperatura = []
    historial_temperatura_json = []
    for registro in historial_registros_qs:
        if registro.temperatura:
            fecha_registro = registro.creado_en.date()
            historial_temperatura.append({
                'fecha': fecha_registro,
                'fecha_display': fecha_registro.strftime('%d/%m/%Y'),
                'temperatura': float(registro.temperatura),
            })
            historial_temperatura_json.append({
                'fecha': fecha_registro.strftime('%Y-%m-%d'),
                'temperatura': float(registro.temperatura),
            })
    
    if ficha.temperatura:
        fecha_actual = ficha.actualizado_en.date()
        historial_temperatura.append({
            'fecha': fecha_actual,
            'fecha_display': fecha_actual.strftime('%d/%m/%Y'),
            'temperatura': float(ficha.temperatura),
        })
        historial_temperatura_json.append({
            'fecha': fecha_actual.strftime('%Y-%m-%d'),
            'temperatura': float(ficha.temperatura),
        })
    
    historial_temperatura.sort(key=lambda x: x['fecha'])
    historial_temperatura_json.sort(key=lambda x: x['fecha'])
    historial_temperatura_json = json.dumps(historial_temperatura_json)
    
    # Total de visitas (eventos clínicos)
    total_visitas = ficha.eventos.exclude(tipo_evento='comentario').count()
    
    # Convertir historial_registros a lista e incluir registro actual si existe
    historial_registros_list = list(historial_registros_qs.order_by('-creado_en'))
    
    # Si la ficha tiene datos, agregar el registro actual al historial
    if ficha.tiene_datos:
        class RegistroActual:
            def __init__(self):
                self.creado_en = ficha.actualizado_en
                self.peso = ficha.peso
                self.temperatura = ficha.temperatura
                self.vacuna_nombre = ultima_vacuna_nombre
                self.vacuna_fecha = ultima_vacuna_fecha_str
                self.alergias = ficha.alergias
                self.condiciones_cronicas = ficha.condiciones_cronicas
                self.medicamentos_actuales = ficha.medicamentos_actuales
        
        registro_actual = RegistroActual()
        historial_registros_list.insert(0, registro_actual)
    
    historial_registros = historial_registros_list
    ultimo_registro = historial_registros[0] if historial_registros else None
    total_registros = len(historial_registros)
    
    # ========== LÓGICA DEL CALENDARIO CON NAVEGACIÓN DE MESES ==========
    today = timezone.now().date()
    
    # Obtener mes y año desde los parámetros GET o usar el mes actual
    mes_seleccionado = request.GET.get('mes')
    anio_seleccionado = request.GET.get('anio')
    
    if mes_seleccionado and anio_seleccionado:
        try:
            mes = int(mes_seleccionado)
            anio = int(anio_seleccionado)
            if 1 <= mes <= 12 and 2000 <= anio <= 2100:
                fecha_calendario = timezone.datetime(anio, mes, 1).date()
            else:
                fecha_calendario = today
        except (ValueError, TypeError):
            fecha_calendario = today
    else:
        fecha_calendario = today
    
    calendar_headers = ['L', 'M', 'X', 'J', 'V', 'S', 'D']
    meses_es = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
    calendario = calendar.Calendar(firstweekday=0)
    semanas_calendario = []
    semanas_meta = []
    semana_actual = []
    
    # Construir semanas del mes con rango de fechas
    week_index = 0
    for dia in calendario.itermonthdates(fecha_calendario.year, fecha_calendario.month):
        if dia.month == fecha_calendario.month:
            semana_actual.append(dia)
        else:
            semana_actual.append('')
        
        if len(semana_actual) == 7:
            semanas_calendario.append([d.day if d != '' else '' for d in semana_actual])
            fechas_reales = [d for d in semana_actual if d != '']
            if fechas_reales:
                inicio_sem = fechas_reales[0]
                fin_sem = fechas_reales[-1]
                semanas_meta.append({
                    'index': week_index + 1,
                    'inicio': inicio_sem.strftime('%d %b').replace('.', ''),
                    'fin': fin_sem.strftime('%d %b').replace('.', ''),
                })
            else:
                semanas_meta.append({
                    'index': week_index + 1,
                    'inicio': '',
                    'fin': '',
                })
            semana_actual = []
            week_index += 1
    if semana_actual:
        while len(semana_actual) < 7:
            semana_actual.append('')
        semanas_calendario.append([d.day if d != '' else '' for d in semana_actual])
        fechas_reales = [d for d in semana_actual if d != '']
        if fechas_reales:
            inicio_sem = fechas_reales[0]
            fin_sem = fechas_reales[-1]
            semanas_meta.append({
                'index': week_index + 1,
                'inicio': inicio_sem.strftime('%d %b').replace('.', ''),
                'fin': fin_sem.strftime('%d %b').replace('.', ''),
            })
        else:
            semanas_meta.append({
                'index': week_index + 1,
                'inicio': '',
                'fin': '',
            })
    
    weeks_paired = list(zip(semanas_calendario, semanas_meta))
    
    # Obtener eventos del mes seleccionado solo para esta mascota específica
    eventos_mes = EventoClinico.objects.filter(
        ficha_clinica__mascota=mascota,
        fecha_evento__year=fecha_calendario.year,
        fecha_evento__month=fecha_calendario.month
    ).select_related('ficha_clinica__mascota').order_by('fecha_evento', 'hora_evento')
    
    # Crear diccionario de eventos por día
    eventos_por_dia = {}
    for evento in eventos_mes:
        dia = evento.fecha_evento.day
        if dia not in eventos_por_dia:
            eventos_por_dia[dia] = []
        hora_evento = evento.hora_evento.strftime('%H:%M') if evento.hora_evento else None
        eventos_por_dia[dia].append({
            'id': evento.id,
            'tipo': evento.tipo_evento,
            'tipo_display': evento.get_tipo_evento_display(),
            'mascota': evento.ficha_clinica.mascota.nombre,
            'descripcion': evento.descripcion[:50] if evento.descripcion else '',
            'hora': hora_evento,
        })
    # ========== FIN LÓGICA DEL CALENDARIO ==========
    
    # Agrupar eventos por fecha para pintar en el calendario
    eventos_por_fecha = {}
    eventos_medicacion_por_fecha = {}
    for ev in ficha.eventos.all():
        if ev.fecha_evento:
            key = ev.fecha_evento.strftime('%Y-%m-%d')
            eventos_por_fecha.setdefault(key, []).append(ev)
            if ev.tipo_evento == 'medicacion':
                eventos_medicacion_por_fecha[key] = eventos_medicacion_por_fecha.get(key, 0) + 1
    
    # Calcular dosis por semana para el calendario
    dosis_por_semana = []
    for semana, meta in weeks_paired:
        dosis_semana = 0
        for d in semana:
            if d:
                fecha_key = f"{today.year}-{today.month:02d}-{d:02d}"
                if fecha_key in eventos_medicacion_por_fecha:
                    dosis_semana += eventos_medicacion_por_fecha[fecha_key]
        dosis_por_semana.append(dosis_semana)
    
    # Crear diccionario de días con medicación para el calendario
    dias_con_medicacion = set()
    for fecha_key in eventos_medicacion_por_fecha.keys():
        try:
            from datetime import datetime
            fecha = datetime.strptime(fecha_key, '%Y-%m-%d').date()
            if fecha.month == today.month and fecha.year == today.year:
                dias_con_medicacion.add(fecha.day)
        except:
            pass
    
    # Filtrado de historial clínico (CU14)
    filtro_fecha_desde = request.GET.get('fecha_desde', '')
    filtro_fecha_hasta = request.GET.get('fecha_hasta', '')
    filtro_tipo_evento = request.GET.get('tipo_evento', '')
    filtro_buscar = request.GET.get('buscar', '')
    
    eventos = ficha.eventos.all()
    
    # Aplicar filtros
    if filtro_fecha_desde:
        try:
            from datetime import datetime
            fecha_desde = datetime.strptime(filtro_fecha_desde, '%Y-%m-%d').date()
            eventos = eventos.filter(fecha_evento__gte=fecha_desde)
        except ValueError:
            pass
    
    if filtro_fecha_hasta:
        try:
            from datetime import datetime
            fecha_hasta = datetime.strptime(filtro_fecha_hasta, '%Y-%m-%d').date()
            eventos = eventos.filter(fecha_evento__lte=fecha_hasta)
        except ValueError:
            pass
    
    if filtro_tipo_evento:
        eventos = eventos.filter(tipo_evento=filtro_tipo_evento)
    
    # Filtro de búsqueda por descripción o veterinario
    if filtro_buscar:
        eventos = eventos.filter(
            Q(descripcion__icontains=filtro_buscar) |
            Q(veterinario__icontains=filtro_buscar)
        )
    
    eventos = eventos.order_by('-fecha_evento')
    
    # Obtener archivos adjuntos para cada evento
    eventos_con_archivos = []
    for evento in eventos:
        archivos = evento.archivos_adjuntos.all()
        eventos_con_archivos.append({
            'evento': evento,
            'archivos': archivos,
        })
    
    # Eventos por tipo (para estadísticas, sin filtros)
    eventos_por_tipo = {}
    for evento in ficha.eventos.all():
        tipo_display = evento.get_tipo_evento_display()
        eventos_por_tipo[tipo_display] = eventos_por_tipo.get(tipo_display, 0) + 1
    
    # Calcular resumen del tratamiento
    eventos_medicacion = ficha.eventos.filter(tipo_evento='medicacion').order_by('fecha_evento')
    eventos_controles = ficha.eventos.filter(tipo_evento__in=['cita_general', 'cita_especialista']).count()
    
    resumen_tratamiento = {
        'medicamento': ficha.medicamentos_actuales or '—',
        'total_dosis': eventos_medicacion.count(),
        'dosis_administradas': eventos_medicacion.count(),  # Por ahora igual al total
        'controles_medicos': eventos_controles,
        'duracion': '—',  # Se puede calcular si hay fechas de inicio y fin
        'recomendaciones': ficha.comentarios or '—',
    }
    
    # Calcular duración si hay eventos de medicación
    if eventos_medicacion.exists():
        primera_fecha = eventos_medicacion.first().fecha_evento
        ultima_fecha = eventos_medicacion.last().fecha_evento
        if primera_fecha and ultima_fecha:
            dias = (ultima_fecha - primera_fecha).days
            semanas = dias // 7
            if semanas > 0:
                resumen_tratamiento['duracion'] = f"{semanas} semana{'s' if semanas != 1 else ''}"
            else:
                resumen_tratamiento['duracion'] = f"{dias} día{'s' if dias != 1 else ''}"
    
    return render(request, 'registro/perfil_mascota.html', {
        'mascota': mascota,
        'ficha': ficha,
        'bitacora_completada': bitacora_completada,
        'salud_score': salud_score,
        'ultima_vacuna': ultima_vacuna,
        'ultima_vacuna_nombre': ultima_vacuna_nombre,
        'ultima_vacuna_fecha_str': ultima_vacuna_fecha_str,
        'ultima_visita_veterinario': ultima_visita_veterinario,
        'proxima_visita_veterinario': proxima_visita_veterinario,
        'historial_peso': historial_peso,
        'historial_peso_json': historial_peso_json,
        'ultimos_registros_peso': ultimos_registros_peso,
        'cambio_peso_display': cambio_peso_display,
        'historial_temperatura': historial_temperatura,
        'historial_temperatura_json': historial_temperatura_json,
        'eventos_por_tipo': eventos_por_tipo,
        'etapa_label': etapa_label,
        'total_visitas': total_visitas,
        'ultimo_registro': ultimo_registro,
        'total_registros': total_registros,
        'historial_registros': historial_registros,
        'calendar_headers': calendar_headers,
        'weeks_paired': weeks_paired,
        'current_month': f"{meses_es[fecha_calendario.month - 1].capitalize()} {fecha_calendario.year}",
        'fecha_calendario': fecha_calendario,
        'mes_calendario': fecha_calendario.month,
        'anio_calendario': fecha_calendario.year,
        'eventos_por_dia': eventos_por_dia,
        'total_eventos_mes': len(eventos_mes),
        'eventos_por_fecha': eventos_por_fecha,
        'eventos_medicacion_por_fecha': eventos_medicacion_por_fecha,
        'dosis_por_semana': dosis_por_semana,
        'dias_con_medicacion': dias_con_medicacion,
        'today': today,
        'evento_form_perfil': EventoClinicoForm(),
        'resumen_tratamiento': resumen_tratamiento,
        'eventos_con_archivos': eventos_con_archivos,
        'filtro_fecha_desde': filtro_fecha_desde,
        'filtro_fecha_hasta': filtro_fecha_hasta,
        'filtro_tipo_evento': filtro_tipo_evento,
        'filtro_buscar': filtro_buscar,
        'tipos_evento_choices': EventoClinico.TIPO_EVENTO_CHOICES,
        'evento_form': EventoClinicoForm(),
    })


@login_required
@perfil_completo_required
@csrf_protect
def desactivar_mascota_view(request, mascota_id):
    mascota = get_object_or_404(Mascota, pk=mascota_id, tutor=request.user, activa=True)
    
    if request.method == 'POST':
        mascota.activa = False
        mascota.save()
        messages.success(request, f'La mascota "{mascota.nombre}" ha sido desactivada correctamente.')
        return redirect('home')
    
    return redirect('perfil_mascota', mascota_id=mascota.id)


@login_required
@perfil_completo_required
@csrf_protect
def actualizar_foto_perfil_banner_view(request):
    """Vista para actualizar la foto de perfil desde el banner"""
    if request.method == 'POST':
        perfil, created = PerfilTutor.objects.get_or_create(user=request.user)
        
        if 'foto_perfil' in request.FILES:
            perfil.foto_perfil = request.FILES['foto_perfil']
            perfil.save()
            messages.success(request, 'Foto de perfil actualizada correctamente.')
            return redirect('home')
        else:
            messages.error(request, 'No se seleccionó ninguna imagen.')
            return redirect('home')
    
    return redirect('home')


@login_required
@perfil_completo_required
@csrf_protect
def actualizar_foto_mascota_view(request, mascota_id):
    """Vista para actualizar la foto de la mascota desde el perfil o bitácora"""
    try:
        mascota = Mascota.objects.get(pk=mascota_id, tutor=request.user, activa=True)
    except Mascota.DoesNotExist:
        messages.error(request, 'Mascota no encontrada.')
        return redirect('home')
    
    if request.method == 'POST':
        if 'foto' in request.FILES:
            mascota.foto = request.FILES['foto']
            mascota.save()
            messages.success(request, f'Foto de {mascota.nombre} actualizada correctamente.')
            # Redirigir a bitácora si viene desde ahí, sino al perfil
            next_url = request.POST.get('next', '')
            if next_url:
                return redirect(next_url)
            return redirect('perfil_mascota', mascota_id=mascota.id)
        else:
            messages.error(request, 'No se seleccionó ninguna imagen.')
            next_url = request.POST.get('next', '')
            if next_url:
                return redirect(next_url)
            return redirect('perfil_mascota', mascota_id=mascota.id)
    
    return redirect('perfil_mascota', mascota_id=mascota.id)


@login_required
@perfil_completo_required
@csrf_protect
def agregar_peso_mascota_view(request, mascota_id):
    """Vista para agregar un nuevo registro de peso a una mascota"""
    try:
        mascota = Mascota.objects.get(pk=mascota_id, tutor=request.user, activa=True)
    except Mascota.DoesNotExist:
        return JsonResponse({'error': 'Mascota no encontrada'}, status=404)
    
    if request.method == 'POST':
        try:
            peso_str = request.POST.get('peso', '').strip()
            if not peso_str:
                return JsonResponse({'error': 'El peso es requerido'}, status=400)
            
            # Convertir a decimal, permitiendo solo 1 decimal
            peso = float(peso_str)
            peso = round(peso, 1)  # Redondear a 1 decimal
            
            if peso <= 0:
                return JsonResponse({'error': 'El peso debe ser mayor a 0'}, status=400)
            
            # Crear el registro de peso con la fecha actual
            from datetime import date
            registro_peso = PesoMascota.objects.create(
                mascota=mascota,
                peso=peso,
                fecha=date.today()
            )
            
            # Retornar los datos del nuevo registro para actualizar el gráfico
            return JsonResponse({
                'success': True,
                'peso': float(registro_peso.peso),
                'fecha': registro_peso.fecha.strftime('%Y-%m-%d'),
                'fecha_display': registro_peso.fecha.strftime('%d/%m/%Y'),
                'id': registro_peso.id
            })
        except ValueError:
            return JsonResponse({'error': 'El peso debe ser un número válido'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)
