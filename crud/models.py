from django.utils import timezone
from django.contrib.auth.models import User
from django.db import models
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
import uuid  # Importar uuid para generar IDs únicos
from datetime import datetime
import json

class Rol(models.Model):
    """
    Modelo para representar los roles de usuario.
    """
    ADMINISTRADOR = 'admin'
    PERSONAL_APOYO = 'apoyo'
    ROL_CHOICES = [
        (ADMINISTRADOR, 'Administrador'),
        (PERSONAL_APOYO, 'Personal de Apoyo'),
    ]
    rol = models.CharField(max_length=10, choices=ROL_CHOICES)

    def __str__(self):
        return self.get_rol_display()



class Departamento(models.Model):
    """
    Modelo para representar los departamentos.
    """
    idDep = models.CharField(max_length=3, primary_key=True)
    nombredep = models.CharField(max_length=50)

    def __str__(self):
        return self.nombredep


class Usuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE)
    foto_perfil = models.ImageField(upload_to='perfil/', default='perfil/default.png')

    def __str__(self):
        return self.usuario.username
    


class Codigo_Qr(models.Model):
    idQr = models.CharField(max_length=10, primary_key=True)
    imagenqr = models.ImageField(upload_to='qr_codes', blank=True)

    def save(self, *args, **kwargs):
        # Si no hay una imagen QR asociada o si se ha cambiado el ID del QR, genera un nuevo QR
        if not self.imagenqr or self._state.adding:
            qr = qrcode.QRCode(
                version=1,
                box_size=10,
                border=5
            )
            qr.add_data(self.idQr)
            qr.make(fit=True)
            img = qr.make_image(fill='black', back_color='white')

            # Guardar la imagen del código QR en un buffer de memoria
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)

            # Guardar la imagen en el campo de imagenqr
            self.imagenqr.save(f'qr_code-{self.idQr}.png', ContentFile(buffer.getvalue()), save=False)

        super().save(*args, **kwargs)

class Tipo_Incidencia(models.Model):
    """
    Modelo para representar los tipos de incidencia.
    """
    idIncidencia = models.CharField(max_length=3, primary_key=True)
    incidencia = models.CharField(max_length=20)
    descripcion = models.CharField(max_length=100)
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE)  # Relación con el modelo de Departamento

    def __str__(self):
        return self.incidencia
    


class QrToken(models.Model):
    token = models.CharField(max_length=36, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    def __str__(self):
        return self.token
    


class Alerta(models.Model):
    idAlerta = models.CharField(max_length=6, primary_key=True)
    descripcion = models.CharField(max_length=500)
    estado_choices = [
        ('1', 'Pendiente'),
        ('2', 'Resuelto'),
        ('3', 'En observación'),
    ]
    estado = models.CharField(max_length=1, choices=estado_choices, default='1')
    fecha = models.DateTimeField(null=True)
    evidencia1 = models.ImageField(upload_to='evidencias', blank=True)
    evidencia2 = models.ImageField(upload_to='evidencias', blank=True)
    evidencia3 = models.ImageField(upload_to='evidencias', blank=True)
    tipo_incidencia = models.ForeignKey(Tipo_Incidencia, on_delete=models.CASCADE)
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE)
    nombre_espacio = models.CharField(max_length=50, null=True)
    ubicacion = models.CharField(max_length=50, null=True)
    urgente = models.BooleanField(default=False)
    encargado = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='alertas_encargadas')
    
    def save(self, *args, **kwargs):
        if not self.idAlerta:
            self.idAlerta = self.generate_unique_id()
        super().save(*args, **kwargs)

    def generate_unique_id(self):
        while True:
            new_id = uuid.uuid4().hex[:6]
            if not Alerta.objects.filter(idAlerta=new_id).exists():
                return new_id

    def __str__(self):
        return self.descripcion
    


class SolucionAlerta(models.Model):
    alerta = models.OneToOneField(Alerta, on_delete=models.CASCADE)
    fecha_resolucion = models.DateTimeField(null=True)
    descripcion = models.CharField(max_length=500)  # Aumentado el max_length para permitir más caracteres
    evidencia1 = models.ImageField(upload_to='evidencias_solucion')
    evidencia2 = models.ImageField(upload_to='evidencias_solucion')
    evidencia3 = models.ImageField(upload_to='evidencias_solucion', blank=True, null=True)

    def __str__(self):
        return f"Solución para Alerta ID: {self.alerta.idAlerta}"
    
    

class Espacio(models.Model):
    idEspacio = models.CharField(max_length=3, primary_key=True, unique=True, editable=False)
    nombreEspacio = models.CharField(max_length=50)
    ubicacion = models.CharField(max_length=50)
    codigo_qr = models.OneToOneField(Codigo_Qr, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.nombreEspacio

    def save(self, *args, **kwargs):
        if not self.idEspacio:
            self.idEspacio = self.generate_unique_idEspacio()

        super().save(*args, **kwargs)

        # Crear o actualizar el código QR
        qr_content = {
            "nombre_espacio": self.nombreEspacio,
            "ubicacion": self.ubicacion
        }

        qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=5
        )
        # Convertir los datos a JSON y luego a bytes UTF-8
        json_data = json.dumps(qr_content, ensure_ascii=False).encode('utf-8')
        qr.add_data(json_data)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')

        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        if not self.codigo_qr:
            codigo_qr = Codigo_Qr.objects.create(idQr=str(uuid.uuid4())[:10])
        else:
            codigo_qr = self.codigo_qr

        codigo_qr.imagenqr.save(f'qr_code-{codigo_qr.idQr}.png', ContentFile(buffer.getvalue()), save=False)
        codigo_qr.save()

        self.codigo_qr = codigo_qr
        super().save(*args, **kwargs)

    def generate_unique_idEspacio(self):
        while True:
            new_id = str(uuid.uuid4())[:3]
            if not Espacio.objects.filter(idEspacio=new_id).exists():
                return new_id
            