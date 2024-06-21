from django.contrib import admin
from .models import *

admin.site.register(Usuario)
admin.site.register(Rol)
admin.site.register(Codigo_Qr)
admin.site.register(Tipo_Incidencia)
admin.site.register(Departamento)
admin.site.register(QrToken)
admin.site.register(SolucionAlerta)

class EspacioAdmin(admin.ModelAdmin):
    list_display = ('idEspacio', 'nombreEspacio', 'ubicacion', 'codigo_qr')
    readonly_fields = ('idEspacio',)

admin.site.register(Espacio, EspacioAdmin)

class AlertaAdmin(admin.ModelAdmin):
    list_display = ('idAlerta', 'descripcion', 'estado', 'fecha', 'evidencia1', 'evidencia2', 'evidencia3', 'tipo_incidencia', 'departamento', 'nombre_espacio', 'ubicacion')
    readonly_fields = ('idAlerta',)  # Hace que el campo idAlerta sea de solo lectura en el formulario de administración

admin.site.register(Alerta, AlertaAdmin)

# Register your models here.

