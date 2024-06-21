import matplotlib
from urllib3 import request
matplotlib.use('Agg')  # Configurar Matplotlib para usar el backend 'Agg'
from datetime import timezone
import json
import locale
from tkinter import Image
from urllib.parse import unquote
from django.forms import model_to_dict
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import AlertaForm, CambiarFotoPerfilForm, EspacioEditForm, LoginForm, SolucionAlertaForm, UserRegistrationForm, CodigoQrForm, EspacioForm, UserEditForm
from django.contrib import messages
from django.urls import reverse
from .models import Alerta, Codigo_Qr, Rol, SolucionAlerta, Tipo_Incidencia, Usuario, Espacio, Departamento
from django.db import transaction
from django.http import Http404, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotAllowed, HttpResponseRedirect, JsonResponse, QueryDict
import qrcode
from io import BytesIO
from django.core.files import File
import os
from django.conf import settings
import uuid
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.utils import timezone
from crud import models
from django.db.models import Count
import matplotlib.pyplot as plt # type: ignore
import io
import urllib, base64
from django.db.models.functions import Coalesce
from django.db.models import Q
from django.core.mail import send_mail
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from django.views.decorators.http import require_POST
from reportlab.lib.pagesizes import letter
from django.utils.timezone import now
from .models import Alerta, SolucionAlerta
from.forms import TransferirAlertaForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

##Vistas Generales##

# Establecer la configuración regional en español
locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')



def generateUUID():
    # Genera un UUID único y lo devuelve como una cadena
    return str(uuid.uuid4())



def plantilla_base(request):
    # Verificar si el usuario está autenticado
    user_authenticated = request.user.is_authenticated
    
    return render(request, 'tu_plantilla_base.html', {'user_authenticated': user_authenticated})



def view_user(request):
    # Aquí puedes agregar lógica para el dashboard
    return render(request, 'view_user.html')



def solicitudes(request):
    return render(request, 'solicitudes.html')



def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # Mostrar un mensaje de bienvenida según el rol del usuario
                if user.usuario.rol.rol == 'admin':
                    messages.success(request, f'Bienvenido, {user.username} (Administrador).')
                    return redirect('view_user')
                elif user.usuario.rol.rol == 'apoyo':
                    messages.success(request, f'Bienvenido, {user.username} (Personal de Apoyo).')
                    return redirect('view_user')
            else:
                # Mostrar un mensaje de error si las credenciales son inválidas
                error_message = "Credenciales inválidas. Inténtalo de nuevo."
                return render(request, 'login.html', {'form': form, 'error_message': error_message})
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})



def logout_view(request):
    if request.user.is_authenticated:
        username = request.user.username
        message = f"¡{username}, cerraste tu sesión! Esperamos verte de nuevo pronto."
        logout(request)
        messages.success(request, message)
    return redirect(reverse('view_user'))  # Redirige a la vista de usuario normal



def scan_qr(request):
    return render(request,'scan_qr.html')



def form_qr(request):
    return render(request,'form_qr.html') 



def limpiar_sesion(request):
    if request.method == 'POST' and request.is_ajax():
        request.session.flush()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'fail'}, status=400)



def formatear_fecha(fecha):
    return fecha.strftime('%d de %B de %Y a las %H:%M')










## Vistas para los Usuarios##

def register_user(request):
    current_user = request.user
    hide_departamento = True
    if current_user.usuario.rol.rol == 'admin' and current_user.usuario.departamento.idDep == '1':
        hide_departamento = False

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, hide_departamento=hide_departamento)
        if form.is_valid():
            rol = form.cleaned_data['rol']
            departamento = form.cleaned_data.get('departamento')

            # Verificar si el rol es 'apoyo' y el departamento es '1'
            if rol.rol == 'apoyo' and departamento and departamento.idDep == '1':
                messages.error(request, 'Un personal de apoyo no puede pertenecer a la administración general.')
            else:
                user = form.save(commit=False)
                user.usuario.set_password(form.cleaned_data['password1'])
                user.usuario.save()

                # Asigna rol al usuario
                user.rol = form.cleaned_data['rol']

                if hide_departamento:
                    # Asignar el departamento del usuario actual si no es admin con idDep 1
                    user.departamento = current_user.usuario.departamento
                else:
                    # Usar el departamento del formulario
                    user.departamento = form.cleaned_data['departamento']

                user.save()

                messages.success(request, f'Se ha registrado al usuario {user.usuario.username} con éxito.')
                return redirect('register_user')
    else:
        form = UserRegistrationForm(initial={'departamento': current_user.usuario.departamento}, hide_departamento=hide_departamento)

    return render(request, 'register.html', {'form': form, 'hide_departamento': hide_departamento})



@login_required
def eliminar_usuario(request, usuario_id):
    usuario = get_object_or_404(User, pk=usuario_id)  # Obtener el usuario por su ID

    if request.method == 'POST':
        usuario.delete()  # Eliminar el usuario

        # Redirigir a alguna página de éxito o a donde desees después de eliminar el usuario
        return redirect('gestion_personal')
    else:
        # Manejar el caso en el que la solicitud no sea POST, tal vez redirigir a otra página o mostrar un mensaje de error
        return redirect('gestion_personal')



def edit_user(request, id):
    user_instance = get_object_or_404(User, id=id)
    usuario_instance = get_object_or_404(Usuario, usuario=user_instance)

    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user_instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario editado correctamente.')  # Mensaje de éxito
            return redirect('gestion_personal')
    else:
        initial_data = {
            'username': user_instance.username,
            'email': user_instance.email,
            'first_name': user_instance.first_name,
            'last_name': user_instance.last_name,
            'rol': usuario_instance.rol,
            'departamento': usuario_instance.departamento,
        }
        form = UserEditForm(instance=user_instance, initial=initial_data)
    
    return render(request, 'edit_user.html', {'form': form})



@login_required
def gestion_personal(request):
    usuario_actual = request.user

    # Verificar si el usuario en sesión es un administrador general
    if usuario_actual.usuario.departamento.idDep == '1':
        usuarios = Usuario.objects.exclude(usuario=usuario_actual)
    else:
        usuarios = Usuario.objects.filter(departamento=usuario_actual.usuario.departamento).exclude(usuario=usuario_actual)

    total_usuarios = usuarios.count()  # Total de usuarios antes del filtro

    # Aplicar filtro por rol si se proporciona en el formulario
    rol_filter = request.GET.get('rol', '')
    if rol_filter:
        usuarios = usuarios.filter(rol__rol=rol_filter)

    # Aplicar filtro por departamento si se proporciona en la URL
    departamento_filter = request.GET.get('departamento', '')
    if departamento_filter:
        usuarios = usuarios.filter(departamento__idDep=departamento_filter)

    # Aplicar filtro por búsqueda por caracteres
    buscar = request.GET.get('buscar', '')
    if buscar:
        usuarios = usuarios.filter(
            Q(usuario__username__icontains=buscar) |
            Q(usuario__first_name__icontains=buscar) |
            Q(usuario__last_name__icontains=buscar)
        )

    total_usuarios_filtrados = usuarios.count()  # Total de usuarios después del filtro

    # Obtener los departamentos disponibles
    departamentos = Departamento.objects.all()

    # Obtener los roles disponibles
    roles = Rol.objects.all()

    # URL para el botón de reset de filtros
    reset_url = reverse('gestion_personal')

    return render(request, 'gestion_personal.html', {
        'usuarios': usuarios,
        'departamentos': departamentos,
        'roles': roles,
        'rol_filter': rol_filter,
        'departamento_filter': departamento_filter,
        'buscar': buscar,
        'reset_url': reset_url,
        'total_usuarios': total_usuarios,
        'total_usuarios_filtrados': total_usuarios_filtrados
    })



## Vistas relacionadas con el Espacio y su gestion ##
@login_required
def register_espacio(request):
    if request.method == 'POST':
        espacio_form = EspacioForm(request.POST)
        if espacio_form.is_valid():
            try:
                with transaction.atomic():
                    espacio = espacio_form.save(commit=False)
                    espacio.idEspacio = espacio_form.cleaned_data['idEspacio']
                    espacio.save()
                    messages.success(request, '¡Espacio y código QR registrados correctamente!')
                    return redirect('view_user')
            except Exception as e:
                messages.error(request, f'Ocurrió un error al registrar el espacio y el código QR: {str(e)}')
                return redirect('register_espacio')
    else:
        espacio = Espacio()
        espacio.idEspacio = espacio.generate_unique_idEspacio()
        espacio_form = EspacioForm(instance=espacio)

    return render(request, 'register_espacio.html', {'espacio_form': espacio_form})




@login_required
def eliminar_espacio(request, espacio_id):
    # Obtener el espacio específico o mostrar un error 404 si no existe
    espacio = get_object_or_404(Espacio, idEspacio=espacio_id)
    
    if request.method == 'POST':
        # Verificar si el espacio tiene un código QR asociado
        if espacio.codigo_qr:
            # Obtener el nombre del archivo del código QR
            qr_file_name = espacio.codigo_qr.imagenqr.name
            
            # Eliminar el objeto de la base de datos
            espacio.delete()
            
            # Eliminar el código QR asociado
            espacio.codigo_qr.delete()
            
            # Eliminar la imagen del código QR del sistema de archivos
            if qr_file_name:
                qr_file_path = os.path.join(settings.MEDIA_ROOT, qr_file_name)
                if os.path.exists(qr_file_path):
                    os.remove(qr_file_path)

        # Redirigir a la página de listado de espacios
        return redirect('listado_espacio')
    else:
        # Si no es una solicitud POST, redirigir a la página de listado de espacios
        return redirect('listado_espacio')
    


@login_required
def edit_espacio(request, idEspacio):
    espacio = get_object_or_404(Espacio, idEspacio=idEspacio)

    if request.method == 'POST':
        form = EspacioEditForm(request.POST, instance=espacio)
        if form.is_valid():
            espacio = form.save(commit=False)
            espacio.save()  # Esto actualizará el código QR también
            messages.success(request, 'Espacio editado correctamente.')
            return redirect('listado_espacio')
    else:
        form = EspacioEditForm(instance=espacio)

    return render(request, 'edit_espacio.html', {'form': form})



@login_required
def buscar_espacio(request):
    buscar = request.GET.get('buscar', '')
    ordenar_por = request.GET.get('ordenar_por', 'nombreEspacio')
    orden = request.GET.get('orden', 'asc')

    # Filtrar por nombre del espacio
    espacios = Espacio.objects.all()
    if buscar:
        espacios = espacios.filter(Q(nombreEspacio__icontains=buscar) | Q(ubicacion__icontains=buscar))

    # Ordenar los resultados
    if orden == 'asc':
        espacios = espacios.order_by(ordenar_por)
    else:
        espacios = espacios.order_by('-' + ordenar_por)

    total_espacios = espacios.count()  # Total de espacios filtrados

    context = {
        'espacios': espacios,
        'total_espacios': total_espacios  # Agregar el total de espacios filtrados al contexto
    }
    return render(request, 'listado_espacio.html', context)



@login_required
def listado_espacio(request):
    espacios = Espacio.objects.all()
    return render(request, 'listado_espacio.html', {'espacios': espacios})











## Vistas relacionadas con las Alertas ##

def buscar_alertas(request):
    query = request.GET.get('query')

    # Filtrar las alertas según el criterio de búsqueda
    alertas = Alerta.objects.filter(
        Q(ubicacion__icontains=query) |  # Buscar por ubicación
        Q(nombreAlerta__icontains=query) |  # Buscar por nombre
        Q(fecha__icontains=query) |  # Buscar por fecha
        Q(estado__icontains=query) |  # Buscar por estado
        Q(tipo_incidencia__icontains=query)  # Buscar por tipo
    )

    total_alertas = alertas.count()
    
    return render(request, 'solicitudes.html', {'alertas': alertas, 'total_alertas': total_alertas})



@login_required
def listar_alertas(request):
    current_user = request.user
    departamento = current_user.usuario.departamento

    # Obtener todas las alertas
    alertas = Alerta.objects.all().order_by('-fecha')
    total_alertas = alertas.count()

    # Obtener todas las ubicaciones y estados posibles
    ubicaciones = Espacio.objects.values_list('ubicacion', flat=True).distinct()
    estados = Alerta.estado_choices

    # Obtener tipos de incidencia si el departamento es idDep: 1
    if departamento.idDep == '1':
        tipos_incidencia = Tipo_Incidencia.objects.all()
    else:
        tipos_incidencia = None

    # Obtener filtros aplicados desde la URL
    ubicacion_filtro = request.GET.get('ubicacion')
    estado_filtro = request.GET.get('estado')
    tipo_filtro = request.GET.get('tipo')

    # Filtrar las alertas según los filtros aplicados
    filtros = {}
    if ubicacion_filtro:
        filtros['ubicacion'] = ubicacion_filtro
    if estado_filtro:
        filtros['estado'] = estado_filtro
    if tipo_filtro:
        filtros['tipo_incidencia'] = tipo_filtro

    # Filtrar alertas según el departamento si no es idDep: 1
    if departamento.idDep != '1':
        alertas = alertas.filter(departamento=departamento)

    # Filtrar alertas asignadas si el usuario es de rol 'apoyo'
    if current_user.usuario.rol == 'apoyo':
        alertas = alertas.filter(encargado=current_user)

    # Aplicar filtros
    alertas = alertas.filter(**filtros)

    total_alertas_filtradas = alertas.count()  # Contador de alertas filtradas

    # Obtener usuarios del mismo departamento
    usuarios = User.objects.filter(usuario__departamento=departamento)

    context = {
        'alertas': alertas,
        'total_alertas': total_alertas,
        'total_alertas_filtradas': total_alertas_filtradas,  # Agregar contador de alertas filtradas
        'ubicaciones': ubicaciones,
        'estados': estados,
        'tipos_incidencia': tipos_incidencia,
        'ubicacion_filtro': ubicacion_filtro,
        'estado_filtro': estado_filtro,
        'tipo_filtro': tipo_filtro,
        'usuarios': usuarios,
    }

    return render(request, 'solicitudes.html', context)



@login_required
def modificar_estado_alerta(request, alerta_id):
    alerta = get_object_or_404(Alerta, idAlerta=alerta_id)
    if request.method == 'POST':
        form = AlertaForm(request.POST, instance=alerta)
        if form.is_valid():
            form.save()
            return redirect('lista_alertas')
    else:
        form = AlertaForm(instance=alerta)
    return render(request, 'modificar_estado_alerta.html', {'form': form})



def eliminar_alerta(request, alerta_id):
    # Obtener la alerta específica o mostrar un error 404 si no existe
    alerta = get_object_or_404(Alerta, idAlerta=alerta_id)
    
    if request.method == 'POST':
        # Eliminar la alerta de la base de datos
        alerta.delete()
        
        # Redirigir a alguna página de éxito o a donde desees después de eliminar la alerta
        return redirect('lista_alertas')
    else:
        # Si la solicitud no es un POST, renderiza el modal de confirmación
        return render(request, 'confirmacion_eliminar_alerta.html', {'alerta': alerta})



def formulario_alerta(request):
    qr_code = request.GET.get('qr_code', '')

    if not qr_code:
        messages.error(request, 'El código QR no contiene la información necesaria.')
        return redirect('view_user')

    try:
        qr_code = urllib.parse.unquote(qr_code)
        qr_data = json.loads(qr_code.replace("'", "\""))
        nombre_espacio = qr_data.get('nombre_espacio', '')
        ubicacion = qr_data.get('ubicacion', '')
    except (json.JSONDecodeError, KeyError):
        messages.error(request, 'Error al decodificar el código QR.')
        return redirect('view_user')

    fecha = timezone.localtime(timezone.now()).strftime('%Y-%m-%d %H:%M')

    if request.method == 'POST':
        form = AlertaForm(request.POST, request.FILES)
        if form.is_valid():
            if Alerta.objects.filter(idAlerta=form.cleaned_data['idAlerta']).exists():
                messages.error(request, 'Debe escanear el código QR nuevamente para generar una alerta.')
                return redirect('view_user')
            alerta = form.save(commit=False)
            alerta.nombre_espacio = nombre_espacio
            alerta.ubicacion = ubicacion
            alerta.fecha = fecha
            alerta.save()

            request.session.flush()

            messages.success(request, '¡Alerta enviada correctamente, se revisará el caso!')
            return HttpResponseRedirect(reverse('resumen_alerta', args=[alerta.pk]))
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        if 'qr_scanned' not in request.session:
            request.session['qr_scanned'] = True
            form = AlertaForm(initial={'nombre_espacio': nombre_espacio, 'ubicacion': ubicacion, 'fecha': fecha})
        else:
            messages.error(request, 'Debe escanear el código QR nuevamente para generar una alerta.')
            return redirect('view_user')

    contexto = {'form': form, 'nombre_espacio': nombre_espacio, 'ubicacion': ubicacion, 'fecha': fecha}
    return render(request, 'formulario_alerta.html', contexto)



def resumen_alerta(request, alerta_id):
    alerta = get_object_or_404(Alerta, pk=alerta_id)
    fecha_formateada = formatear_fecha(alerta.fecha)
    return render(request, 'resumen_alerta.html', {'alerta': alerta, 'fecha_formateada': fecha_formateada})



# Define un diccionario que mapea los valores numéricos de estado a sus correspondientes descripciones
ESTADO_DICT = {
    '1': 'Pendiente',
    '2': 'Resuelto',
    '3': 'En observación',
}



# Modifica la función de generar PDF para usar la función formatear_estado
def generar_pdf(request, alerta_id):
    alerta = get_object_or_404(Alerta, idAlerta=alerta_id)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="alerta_{alerta.idAlerta}.pdf"'
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Establecer fuente y tamaño de fuente
    p.setFont("Times-Roman", 12)

    # Datos de la alerta
    datos = [
        (f"ID Alerta: {alerta.idAlerta}", height - 100),
        (f"Descripción: {alerta.descripcion}", height - 120),
        (f"Fecha: {formatear_fecha(alerta.fecha)}", height - 140),
        (f"Nombre Espacio: {alerta.nombre_espacio}", height - 160),
        (f"Ubicación: {alerta.ubicacion}", height - 180),
        (f"Tipo de Incidencia: {alerta.tipo_incidencia}", height - 200),
        (f"Estado: {formatear_estado(alerta.estado)}", height - 220),
        (f"Departamento: {alerta.departamento}", height - 240)
    ]

    # Dibujar cada línea de datos
    for texto, y in datos:
        p.drawString(100, y, texto)
    
    p.showPage()
    p.save()
    return response



def generar_imagen(request, alerta_id):
    alerta = get_object_or_404(Alerta, idAlerta=alerta_id)
    image = Image.new('RGB', (800, 400), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)

    try:
        # Intentar cargar la fuente Arial
        font = ImageFont.truetype("arial.ttf", 18)
    except IOError:
        # Si no se puede cargar, utilizar la fuente predeterminada
        font = ImageFont.load_default()

    # Datos de la alerta
    datos = [
        (f"ID Alerta: {alerta.idAlerta}", 50, 50),
        (f"Descripción: {alerta.descripcion}", 50, 80),
        (f"Fecha: {formatear_fecha(alerta.fecha)}", 50, 110),
        (f"Nombre Espacio: {alerta.nombre_espacio}", 50, 140),
        (f"Ubicación: {alerta.ubicacion}", 50, 170),
        (f"Tipo de Incidencia: {alerta.tipo_incidencia}", 50, 200),
        (f"Estado: {formatear_estado(alerta.estado)}", 50, 230),
        (f"Departamento: {alerta.departamento}", 50, 260)
    ]

    # Dibujar borde y cada línea de datos
    for texto, x, y in datos:
        draw.rectangle((45, y, 755, y + 30), outline=(0, 0, 0))  # Borde alrededor de cada dato
        draw.text((x, y), texto, fill=(0, 0, 0), font=font)
    
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='image/png')
    response['Content-Disposition'] = f'attachment; filename="alerta_{alerta.idAlerta}.png"'
    return response



# Define la función formatear_estado para traducir el estado
def formatear_estado(estado):
    return ESTADO_DICT.get(estado, 'Desconocido')



@login_required
def detalles_alerta(request, id_alerta):
    # Obtener la alerta con la ID proporcionada
    alerta = get_object_or_404(Alerta, idAlerta=id_alerta)

    # Obtener la solución asociada a la alerta si existe
    try:
        solucion_alerta = SolucionAlerta.objects.get(alerta=alerta)
    except SolucionAlerta.DoesNotExist:
        solucion_alerta = None

    # Renderizar la plantilla con la información de la alerta y la solución (si existe)
    return render(request, 'detalles_alerta.html', {'alerta': alerta, 'solucion_alerta': solucion_alerta})


def estadisticas_alertas(request):
    total_alertas = Alerta.objects.count()
    total_alertas_resueltas = Alerta.objects.filter(estado='2').count()

    alertas_resueltas_por_departamento = Departamento.objects.annotate(
        total_resueltas=Count('alerta', filter=Q(alerta__estado='2'))
    ).order_by('nombredep')

    alertas_por_tipo_incidencia = Tipo_Incidencia.objects.annotate(
        total=Count('alerta')
    ).order_by('incidencia')

    def generar_grafico(datos, titulo, etiqueta_x, etiqueta_y):
        fig, ax = plt.subplots(figsize=(10, 6))
        etiquetas = [item[0] for item in datos]
        valores = [item[1] for item in datos]
        barras = ax.bar(etiquetas, valores)
        ax.set_title(titulo)
        ax.set_xlabel(etiqueta_x)
        ax.set_ylabel(etiqueta_y)
        ax.set_ylim(0, 100)  # Ajustar el eje y de 0 a 100
        plt.xticks(rotation=45)

        # Añadir etiquetas encima de las barras
        for barra, valor in zip(barras, valores):
            ax.text(barra.get_x() + barra.get_width() / 2, barra.get_height(), f'{valor:.1f}%', 
                    ha='center', va='bottom')

        plt.tight_layout()

        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', bbox_inches='tight')
        buffer.seek(0)
        grafico_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close(fig)
        return grafico_base64

    datos_resueltas = [
        (departamento.nombredep, (departamento.total_resueltas / total_alertas_resueltas) * 100 if total_alertas_resueltas > 0 else 0)
        for departamento in alertas_resueltas_por_departamento
    ]

    datos_incidencia = [
        (tipo_incidencia.incidencia, (tipo_incidencia.total / total_alertas) * 100 if total_alertas > 0 else 0)
        for tipo_incidencia in alertas_por_tipo_incidencia
    ]

    grafico_resueltas = generar_grafico(datos_resueltas, 'Porcentaje de Alertas Resueltas por Departamento', 'Departamento', 'Porcentaje')
    grafico_solicitadas = generar_grafico(datos_incidencia, 'Porcentaje de Alertas por Tipo de Incidencia', 'Tipo de Incidencia', 'Porcentaje')

    context = {
        'alertas_resueltas_por_departamento': alertas_resueltas_por_departamento,
        'alertas_por_tipo_incidencia': alertas_por_tipo_incidencia,
        'grafico_resueltas': grafico_resueltas,
        'grafico_solicitadas': grafico_solicitadas,
    }

    return render(request, 'estadisticas_alertas.html', context)



@login_required
def filtrar_mis_alertas(request):
    current_user = request.user

    # Filtrar las alertas asignadas al usuario actual
    mis_alertas = Alerta.objects.filter(encargado=current_user)

    total_alertas_filtradas = mis_alertas.count()  # Contador de alertas filtradas

    context = {
        'alertas': mis_alertas,
        'total_alertas': total_alertas_filtradas,
        'total_alertas_filtradas': total_alertas_filtradas,
        # Otras variables de contexto que puedas necesitar...
    }

    return render(request, 'solicitudes.html', context)



@login_required
def alertas_por_aprobar(request):
    current_user = request.user
    departamento = current_user.usuario.departamento

    # Filtrar las alertas por soluciones pendientes de aprobación (en observación)
    alertas_pendientes_aprobacion = Alerta.objects.filter(solucionalerta__isnull=False, estado='3')

    # Filtrar alertas según el departamento si no es idDep: 1
    if departamento.idDep != '1':
        alertas_pendientes_aprobacion = alertas_pendientes_aprobacion.filter(departamento=departamento)

    total_alertas = alertas_pendientes_aprobacion.count()  # Contador de alertas filtradas

    context = {
        'alertas': alertas_pendientes_aprobacion,
        'total_alertas': total_alertas,
    }

    return render(request, 'solicitudes.html', context)



@login_required
def asignar_alerta(request):
    if request.method == 'POST':
        alerta_id = request.POST.get('alerta_id')
        encargado_id = request.POST.get('encargado')
        
        alerta = get_object_or_404(Alerta, idAlerta=alerta_id)
        encargado = get_object_or_404(User, id=encargado_id)
        
        alerta.encargado = encargado
        alerta.save()
        
        messages.success(request, f'Alerta asignada correctamente al usuario {encargado.username}')
        
        return redirect('listar_alertas')

    return HttpResponseNotAllowed(['POST'])



@login_required
@require_POST
def tomar_alerta(request, alerta_id):
    alerta = get_object_or_404(Alerta, idAlerta=alerta_id)

    # Verificar si la alerta ya está asignada
    if alerta.encargado:
        messages.error(request, 'La alerta ya está asignada a otro usuario.')
    else:
        # Asignar la alerta al usuario actual
        alerta.encargado = request.user
        alerta.save()
        messages.success(request, 'Alerta tomada correctamente.')

    return JsonResponse({'success': 'Alerta tomada correctamente.'})



@login_required
def desasignar_alerta(request):
    if request.method == 'POST':
        alerta_id = request.POST.get('alerta_id')
        
        alerta = get_object_or_404(Alerta, idAlerta=alerta_id)
        alerta.encargado = None
        alerta.save()
        
        messages.success(request, 'Alerta desasignada correctamente')
        
        return redirect('listar_alertas')

    return HttpResponseNotAllowed(['POST'])



def transferir_alerta(request, alerta_id):
    alerta = get_object_or_404(Alerta, idAlerta=alerta_id)

    if request.method == 'POST':
        form = TransferirAlertaForm(request.POST)
        if form.is_valid():
            tipo_incidencia = form.cleaned_data['tipo_incidencia']
            # Actualizar la alerta con el nuevo tipo de incidencia y departamento asociado
            alerta.tipo_incidencia = tipo_incidencia
            alerta.departamento = tipo_incidencia.departamento  # Asigna el departamento asociado al tipo de incidencia
            alerta.save()
            messages.success(request, f'Alerta transferida correctamente a {alerta.departamento}')
        
            return redirect('listar_alertas')
    else:
        form = TransferirAlertaForm()

    tipo_incidencias = Tipo_Incidencia.objects.all()

    return render(request, 'transferir_alerta.html', {'alerta': alerta, 'form': form, 'tipo_incidencias': tipo_incidencias})



def ver_estado(request):
    if request.method == 'GET':
        alerta_id = request.GET.get('alerta_id')
        if alerta_id:
            try:
                alerta = Alerta.objects.get(idAlerta=alerta_id)
                return redirect('detalle_estado_alerta', alerta_id=alerta.idAlerta)
            except Alerta.DoesNotExist:
                return render(request, 'ver_estado.html', {'error': 'No se encontró ninguna alerta con ese ID.'})
        else:
            return render(request, 'ver_estado.html')
    return render(request, 'ver_estado.html')



def detalle_estado_alerta(request, alerta_id):
    alerta = get_object_or_404(Alerta, idAlerta=alerta_id)
    solucion_alerta = SolucionAlerta.objects.filter(alerta=alerta).first()  # Recuperar la primera solución asociada a la alerta

    fecha_actual = timezone.now()
    return render(request, 'detalle_estado_alerta.html', {'alerta': alerta, 'solucion_alerta': solucion_alerta, 'fecha_actual': fecha_actual})



## Vistas relacionadas con la Solucion de las Alertas ##

@login_required
def solucion_alerta(request, alerta_id):
    alerta = get_object_or_404(Alerta, idAlerta=alerta_id)

    if request.method == 'POST':
        form = SolucionAlertaForm(request.POST, request.FILES)
        if form.is_valid():
            solucion_alerta = form.save(commit=False)
            solucion_alerta.alerta = alerta
            solucion_alerta.fecha_resolucion = now()  # Asegúrate de tener definida la función now() adecuadamente
            solucion_alerta.save()

            alerta.estado = '3'  # Cambiar el estado de la alerta si es necesario
            alerta.save()

            messages.info(request, 'Tu solución está siendo verificada por la administración.')
            return redirect('detalles_alerta', id_alerta=alerta_id)
    else:
        form = SolucionAlertaForm()

    return render(request, 'solucion_alerta.html', {'form': form, 'alerta': alerta})



@require_POST
def eliminar_solucion_alerta(request, id_alerta):
    # Obtener la alerta con la ID proporcionada
    alerta = get_object_or_404(Alerta, idAlerta=id_alerta)

    try:
        # Obtener la solución asociada a la alerta y eliminarla
        solucion_alerta = SolucionAlerta.objects.get(alerta=alerta)
        solucion_alerta.delete()
        return HttpResponse(status=204)  # Respuesta exitosa sin contenido
    except SolucionAlerta.DoesNotExist:
        return HttpResponseBadRequest("No existe una solución para esta alerta.")
    


def detalles_solucion(request, solucion_id):
    solucion_alerta = get_object_or_404(SolucionAlerta, id=solucion_id)
    return render(request, 'detalles_solucion.html', {'solucion_alerta': solucion_alerta})



@require_POST
def aceptar_solucion(request, solucion_id):
    try:
        solucion = get_object_or_404(SolucionAlerta, alerta__idAlerta=solucion_id)
        alerta = get_object_or_404(Alerta, idAlerta=solucion_id)

        # Cambiar estado de la alerta a "Resuelta"
        alerta.estado = '2'
        alerta.save()

        # Actualizar fecha de resolución de la solución
        solucion.fecha_resolucion = timezone.now()
        solucion.save()

        # Preparar el mensaje de éxito para enviar como JSON
        mensaje = 'La solución ha sido aceptada correctamente.'
        return JsonResponse({'mensaje': mensaje})
    
    except Alerta.DoesNotExist:
        return JsonResponse({'error': 'La alerta especificada no existe.'}, status=404)
    
    except SolucionAlerta.DoesNotExist:
        return JsonResponse({'error': 'La solución especificada no existe.'}, status=404)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def rechazar_solucion(request, solucion_id):
    print(f'Rechazando solución para solución ID: {solucion_id}')
    solucion = get_object_or_404(SolucionAlerta, pk=solucion_id)
    
    if request.method == 'POST':
        print('Método POST recibido')
        # Eliminar la instancia de SolucionAlerta
        solucion.delete()

        # Aquí puedes realizar otras acciones adicionales si es necesario

        return JsonResponse({'mensaje': 'Solución rechazada correctamente.'})
    
    return JsonResponse({'error': 'Método no permitido.'}, status=405)


@login_required
def perfil(request):
    if request.method == 'POST' and 'cambiar_contraseña' in request.POST:
        form_contraseña = PasswordChangeForm(request.user, request.POST)
        if form_contraseña.is_valid():
            user = form_contraseña.save()
            update_session_auth_hash(request, user)  # Mantener sesión activa
            messages.success(request, '¡Tu contraseña ha sido actualizada con éxito!')
            return redirect('perfil')
        else:
            for error in form_contraseña.errors.values():
                messages.error(request, error)
    else:
        form_contraseña = PasswordChangeForm(request.user)

    context = {
        'user': request.user,
        'form_contraseña': form_contraseña,
    }
    return render(request, 'perfil.html', context)

@csrf_exempt
@login_required
def cambiar_foto_perfil(request):
    if request.method == 'POST' and request.FILES.get('foto_perfil'):
        user = request.user
        user.usuario.foto_perfil = request.FILES['foto_perfil']
        user.usuario.save()
        return JsonResponse({
            'success': True,
            'foto_perfil_url': user.usuario.foto_perfil.url,
        })
    return JsonResponse({'success': False})



