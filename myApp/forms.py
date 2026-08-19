from django import forms
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

class ProfesorForm(forms.ModelForm):
    class Meta:
        model = Profesor
        fields = ['nombre', 'apellido', 'email', 'profesion']

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