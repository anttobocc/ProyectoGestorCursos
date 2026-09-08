from django import forms
from django.contrib.auth.models import User
from .models import Curso, Profesor, Estudiante, Entregable, Inscripcion

class CursoForm(forms.ModelForm):
    alumnos = forms.ModelMultipleChoiceField(
        queryset=Estudiante.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label='Alumnos',
    )

    class Meta:
        model = Curso
        fields = ['nombre', 'camada', 'profesores']
        widgets = {
            'profesores': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        }

class ProfesorFormulario(forms.Form):
    nombre = forms.CharField(max_length=100, label="Nombre")
    apellido = forms.CharField(max_length=100, label="Apellido")
    email = forms.EmailField(label="Correo Electrónico")
    profesion = forms.CharField(max_length=100, label="Profesión")
    username = forms.CharField(max_length=150, label="Usuario", required=False)
    password = forms.CharField(max_length=128, label="Contraseña", widget=forms.PasswordInput, required=False)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        if username and User.objects.filter(username=username).exists():
            self.add_error('username', 'Ese nombre de usuario ya está en uso.')
        if password and not username:
            self.add_error('username', 'Ingresá un usuario para crear el acceso.')
        if username and not password:
            self.add_error('password', 'Ingresá una contraseña para crear el acceso.')
        return cleaned_data

class ProfesorForm(forms.ModelForm):
    username = forms.CharField(max_length=150, label="Usuario", required=False)
    password = forms.CharField(
        max_length=128, label="Contraseña", widget=forms.PasswordInput, required=False,
        help_text="Dejar en blanco para no cambiarla."
    )

    class Meta:
        model = Profesor
        fields = ['nombre', 'apellido', 'email', 'profesion']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.user:
            self.fields['username'].initial = self.instance.user.username

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            qs = User.objects.filter(username=username)
            usuario_actual = self.instance.user if (self.instance and self.instance.pk) else None
            if usuario_actual:
                qs = qs.exclude(pk=usuario_actual.pk)
            if qs.exists():
                raise forms.ValidationError('Ese nombre de usuario ya está en uso.')
        return username

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        tiene_cuenta = bool(self.instance and self.instance.pk and self.instance.user)
        if not tiene_cuenta and password and not username:
            self.add_error('username', 'Ingresá un usuario para crear el acceso.')
        if not tiene_cuenta and username and not password:
            self.add_error('password', 'Ingresá una contraseña para crear el acceso.')
        return cleaned_data

class EstudianteFormulario(forms.Form):
    nombre = forms.CharField(max_length=100, label="Nombre")
    apellido = forms.CharField(max_length=100, label="Apellido")
    email = forms.EmailField(label="Correo Electrónico")

class EstudianteForm(forms.ModelForm):
    class Meta:
        model = Estudiante
        fields = ['nombre', 'apellido', 'email']

class InscripcionForm(forms.ModelForm):
    class Meta:
        model = Inscripcion
        fields = ['asistencia', 'promedio']
        labels = {
            'asistencia': 'Asistencia (%)',
            'promedio': 'Promedio (0-10)',
        }

class EntregableFormulario(forms.Form):
    nombre = forms.CharField(max_length=100, label="Nombre")
    fecha_vencimiento = forms.DateTimeField(
        label="Fecha de vencimiento",
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        required=False
    )

class EntregableForm(forms.ModelForm):
    class Meta:
        model = Entregable
        fields = ['nombre', 'fecha_vencimiento', 'estudiantes']
        widgets = {
            'fecha_vencimiento': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'estudiantes': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'estudiantes': 'Alumnos que entregaron',
        }