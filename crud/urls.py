from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import edit_espacio, edit_user, limpiar_sesion, solucion_alerta
from .views import detalles_alerta
from .views import estadisticas_alertas
from .views import perfil
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.view_user, name='home'), 
    path('view_user/', views.view_user, name='view_user'),  # Esta es la URL en la que se iniciará el servidor
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('view_user/scan_qr/', views.scan_qr, name='scan_qr'),
    path('form_qr/', views.form_qr, name='form_qr'),
    path('register/', views.register_user, name='register_user'),
    path('gestion_personal/', views.gestion_personal, name='gestion_personal'),
    path('register_espacio/', views.register_espacio, name='register_espacio'),
    path('listado_espacio/', views.listado_espacio, name='listado_espacio'),
    path('formulario_alerta/', views.formulario_alerta, name='formulario_alerta'),
    path('eliminar_espacio/<str:espacio_id>/', views.eliminar_espacio, name='eliminar_espacio'),
    path('eliminar_alerta/<str:alerta_id>/', views.eliminar_espacio, name='eliminar_alerta'),
    path('eliminar-usuario/<int:usuario_id>/', views.eliminar_usuario, name='eliminar_usuario'),
    path('alertas/<str:alerta_id>/modificar_estado/', views.modificar_estado_alerta, name='modificar_estado_alerta'),
    path('alerta/<str:id_alerta>/eliminar-solucion/', views.eliminar_solucion_alerta, name='eliminar_solucion_alerta'),
    path('editar_espacio/<str:idEspacio>/', edit_espacio, name='edit_espacio'),
    path('alertas/', views.listar_alertas, name='listar_alertas'),
    path('alerta/<str:id_alerta>/', detalles_alerta, name='detalles_alerta'),
    path('estadisticas/', estadisticas_alertas, name='estadisticas_alertas'),
    path('solucionar/<str:alerta_id>/', views.solucion_alerta, name='solucion_alerta'),
    path('solucion/<str:solucion_id>/', views.detalles_solucion, name='detalles_solucion'),
    path('resumen_alerta/<str:alerta_id>/', views.resumen_alerta, name='resumen_alerta'),
    path('generar_pdf/<str:alerta_id>/', views.generar_pdf, name='generar_pdf'),
    path('generar_imagen/<str:alerta_id>/', views.generar_imagen, name='generar_imagen'),
    path('limpiar_sesion/', limpiar_sesion, name='limpiar_sesion'),
    path('eliminar_alerta/<int:alerta_id>/', views.eliminar_alerta, name='eliminar_alerta'),
    path('buscar/', views.buscar_alertas, name='buscar_alertas'),
    path('buscar_espacio/', views.buscar_espacio, name='buscar_espacio'),
    path('asignar-alerta/', views.asignar_alerta, name='asignar_alerta'),
    path('desasignar_alerta/', views.desasignar_alerta, name='desasignar_alerta'),
    path('filtrar-mis-alertas/', views.filtrar_mis_alertas, name='filtrar_mis_alertas'),
    path('alertas-por-aprobar/', views.alertas_por_aprobar, name='alertas_por_aprobar'),
    path('tomar-alerta/<str:alerta_id>/', views.tomar_alerta, name='tomar_alerta'),
    path('editar_usuario/<int:id>/', views.edit_user, name='edit_user'),
    path('ver_estado/', views.ver_estado, name='ver_estado'),
    path('detalle_estado_alerta/<str:alerta_id>/', views.detalle_estado_alerta, name='detalle_estado_alerta'),
    path('alerta/<str:alerta_id>/transferir/', views.transferir_alerta, name='transferir_alerta'),
    path('aceptar_solucion/<str:solucion_id>/', views.aceptar_solucion, name='aceptar_solucion'),
    path('rechazar-solucion/<str:solucion_id>/', views.rechazar_solucion, name='rechazar_solucion'),
    path('perfil/', perfil, name='perfil'),
    path('accounts/password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('accounts/password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('cambiar_foto_perfil/', views.cambiar_foto_perfil, name='cambiar_foto_perfil'),

    # Agrega otras URL que puedas necesitar
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
