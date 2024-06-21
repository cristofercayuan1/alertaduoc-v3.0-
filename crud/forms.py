from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils import timezone
from .models import Alerta, Rol, Departamento, Tipo_Incidencia, Usuario, Espacio, SolucionAlerta, Codigo_Qr

# Formularios de Usuario

class LoginForm(forms.Form):
    username = forms.CharField(label='Nombre de usuario', max_length=100)
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)



class UserRegistrationForm(forms.ModelForm):
    """
    Formulario para registrar un nuevo usuario.
    """
    username = forms.CharField(label='Nombre de usuario', max_length=150)
    email = forms.EmailField(label='Correo electrónico')
    first_name = forms.CharField(label='Nombre', max_length=30)
    last_name = forms.CharField(label='Apellidos', max_length=30)
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput)
    rol = forms.ModelChoiceField(label='Rol', queryset=Rol.objects.all())
    departamento = forms.ModelChoiceField(label='Departamento', queryset=Departamento.objects.all(), required=False)

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'rol', 'departamento']

    def __init__(self, *args, **kwargs):
        hide_departamento = kwargs.pop('hide_departamento', False)
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})

        if hide_departamento:
            self.fields['departamento'].widget = forms.HiddenInput()

    def clean(self):
        cleaned_data = super().clean()
        rol = cleaned_data.get('rol')
        departamento = cleaned_data.get('departamento')

        if rol.rol == 'apoyo' and departamento and departamento.idDep == 1:
            raise forms.ValidationError('Un personal de apoyo no puede pertenecer al departamento de administración general.')

        return cleaned_data

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if len(username) < 5:
            raise forms.ValidationError('El nombre de usuario debe tener al menos 5 caracteres.')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Este nombre de usuario ya está en uso. Por favor, elige otro.')
        return username

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if len(password1) < 8:
            raise forms.ValidationError('La contraseña debe tener al menos 8 caracteres.')
        if not any(char.isdigit() for char in password1):
            raise forms.ValidationError('La contraseña debe contener al menos un número.')
        if not any(char.isalpha() for char in password1):
            raise forms.ValidationError('La contraseña debe contener al menos una letra.')
        return password1

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo electrónico ya está registrado. Por favor, utiliza otro.')
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return password2

    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False)
        user.usuario = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password1'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name']
        )

        rol = self.cleaned_data['rol']
        departamento = self.cleaned_data['departamento']

        if rol.rol == 'admin':
            if departamento and departamento.idDep == '1':
                super_group, _ = Group.objects.get_or_create(name='Superusuario')
                staff_group, _ = Group.objects.get_or_create(name='Staff')
                activo_group, _ = Group.objects.get_or_create(name='Activo')
                user.usuario.is_staff = True
                user.usuario.is_superuser = True
                user.usuario.groups.add(super_group, staff_group, activo_group)
            else:
                staff_group, _ = Group.objects.get_or_create(name='Staff')
                activo_group, _ = Group.objects.get_or_create(name='Activo')
                user.usuario.is_active = True
                user.usuario.groups.add(staff_group, activo_group)
        elif rol.rol == 'apoyo':
            activo_group, _ = Group.objects.get_or_create(name='Activo')
            user.usuario.is_active = True
            user.usuario.groups.add(activo_group)

        if commit:
            user.save()
        return user
    


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True

    rol = forms.ModelChoiceField(queryset=Rol.objects.all(), required=False)
    departamento = forms.ModelChoiceField(queryset=Departamento.objects.all(), required=False)

    def save(self, commit=True):
        instance = super().save(commit=False)

        if commit:
            instance.save()

        if commit and hasattr(self, 'instance') and self.instance.usuario:
            usuario_instance = self.instance.usuario
            usuario_instance.rol = self.cleaned_data.get('rol', usuario_instance.rol)
            usuario_instance.departamento = self.cleaned_data.get('departamento', usuario_instance.departamento)
            usuario_instance.save()

        return instance
    









# Formularios de Espacio
class CodigoQrForm(forms.ModelForm):
    class Meta:
        model = Codigo_Qr
        exclude = ['idQr']



class EspacioForm(forms.ModelForm):
    idEspacio = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}), required=False)
    idQr = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = Espacio
        fields = ['nombreEspacio', 'ubicacion']

    def __init__(self, *args, **kwargs):
        super(EspacioForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
        if self.instance.pk:
            self.fields['idEspacio'].initial = self.instance.idEspacio
        else:
            self.fields['idEspacio'].initial = self.instance.generate_unique_idEspacio()



class EspacioEditForm(forms.ModelForm):
    class Meta:
        model = Espacio
        fields = ['nombreEspacio', 'ubicacion']

    def __init__(self, *args, **kwargs):
        super(EspacioEditForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

    def clean_nombreEspacio(self):
        nombreEspacio = self.cleaned_data.get('nombreEspacio')
        if not nombreEspacio:
            raise forms.ValidationError('Este campo es obligatorio.')
        return nombreEspacio

    def clean_ubicacion(self):
        ubicacion = self.cleaned_data.get('ubicacion')
        if not ubicacion:
            raise forms.ValidationError('Este campo es obligatorio.')
        return ubicacion

    def clean(self):
        cleaned_data = super().clean()
        nombreEspacio = cleaned_data.get('nombreEspacio')
        ubicacion = cleaned_data.get('ubicacion')

        if nombreEspacio and ubicacion:
            if Espacio.objects.filter(nombreEspacio=nombreEspacio, ubicacion=ubicacion).exists():
                raise forms.ValidationError('Este espacio ya está registrado.')

        return cleaned_data
    









# Formularios de Alerta
class AlertaForm(forms.ModelForm):
    ESTADO_CHOICES = [
        ('1', 'Pendiente'),
        ('2', 'Resuelto')
    ]
    estado = forms.ChoiceField(choices=ESTADO_CHOICES, label='Estado', required=False, widget=forms.HiddenInput(), initial='1')
    fecha = forms.DateTimeField(label='Fecha de registro', required=False, disabled=True, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    departamento = forms.ModelChoiceField(queryset=Departamento.objects.all(), label='Departamento', required=False, widget=forms.HiddenInput())
    nombre_espacio = forms.CharField(label='Nombre Espacio', required=False, disabled=True, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    ubicacion = forms.CharField(label='Ubicación', required=False, disabled=True, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    idAlerta = forms.CharField(label='ID Alerta', required=False, disabled=True, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    urgente = forms.BooleanField(label='¿Es urgente?', required=False)

    class Meta:
        model = Alerta
        fields = ['descripcion', 'estado', 'fecha', 'evidencia1', 'evidencia2', 'evidencia3', 'tipo_incidencia', 'departamento', 'nombre_espacio', 'ubicacion', 'idAlerta', 'urgente']

    def __init__(self, *args, **kwargs):
        super(AlertaForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['idAlerta'].initial = self.instance.idAlerta
        else:
            self.fields['idAlerta'].initial = self.instance.generate_unique_id()

        instancia_alerta = kwargs.get('instance')

        if instancia_alerta:
            self.fields['nombre_espacio'].initial = instancia_alerta.nombre_espacio
            self.fields['ubicacion'].initial = instancia_alerta.ubicacion
            self.fields['fecha'].initial = instancia_alerta.fecha.strftime('%Y-%m-%d %H:%M') if instancia_alerta.fecha else None
            self.fields['estado'].initial = instancia_alerta.estado
            self.fields['departamento'].initial = instancia_alerta.departamento
        else:
            self.fields['estado'].initial = '1'

        self.fields['evidencia1'].widget.attrs.update({'accept': 'image/*', 'capture': 'camera'})
        self.fields['evidencia2'].widget.attrs.update({'accept': 'image/*', 'capture': 'camera'})
        self.fields['evidencia3'].widget.attrs.update({'accept': 'image/*', 'capture': 'camera'})

    def clean(self):
        cleaned_data = super().clean()
        tipo_incidencia = cleaned_data.get("tipo_incidencia")
        if tipo_incidencia:
            departamento = tipo_incidencia.departamento
            cleaned_data["departamento"] = departamento
        return cleaned_data



class TransferirAlertaForm(forms.Form):
    departamento_destino = forms.ModelChoiceField(queryset=Departamento.objects.all(), empty_label=None)
    tipo_incidencia = forms.ModelChoiceField(queryset=Tipo_Incidencia.objects.all(), label='Seleccione Tipo de Incidencia')

    

class SolucionAlertaForm(forms.ModelForm):
    descripcion = forms.CharField(
        label='Descripción',
        max_length=500,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'style': 'resize: none; width: 100%;'
        })
    )
    evidencia1 = forms.ImageField(
        label='Evidencia 1',
        widget=forms.ClearableFileInput(attrs={'onchange': 'previewImage(event, 1)'})
    )
    evidencia2 = forms.ImageField(
        label='Evidencia 2',
        widget=forms.ClearableFileInput(attrs={'onchange': 'previewImage(event, 2)'})
    )
    evidencia3 = forms.ImageField(
        label='Evidencia 3',
        required=False,
        widget=forms.ClearableFileInput(attrs={'onchange': 'previewImage(event, 3)'})
    )
    fecha_resolucion = forms.DateTimeField(
        label='Fecha de Resolución',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly',
        })
    )

    class Meta:
        model = SolucionAlerta
        fields = ['descripcion', 'evidencia1', 'evidencia2', 'evidencia3', 'fecha_resolucion']

    def __init__(self, *args, **kwargs):
        super(SolucionAlertaForm, self).__init__(*args, **kwargs)
        self.fields['fecha_resolucion'].initial = timezone.now()

    def clean(self):
        cleaned_data = super().clean()
        descripcion = cleaned_data.get('descripcion')
        evidencia1 = cleaned_data.get('evidencia1')
        evidencia2 = cleaned_data.get('evidencia2')
        evidencia3 = cleaned_data.get('evidencia3')

        if not descripcion or not evidencia1 or not evidencia2:
            raise forms.ValidationError("Todos los campos deben ser completados.")

class CambiarFotoPerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario  # Reemplaza con tu modelo Usuario
        fields = ['foto_perfil']