from django import forms
from .models import Curso, Profesor, Estudiante, Entregable

class CursoFormulario(forms.Form):
    nombre = forms.CharField(max_length=100)
    camada = forms.IntegerField()

class CursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = ['nombre', 'camada']

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
    asistencia = forms.IntegerField(label="Asistencia (%)", min_value=0, max_value=100)
    promedio = forms.FloatField(label="Promedio (0-10)", min_value=0.0, max_value=10.0)
    proyectos_hechos = forms.IntegerField(label="Proyectos realizados", min_value=0)
    proyectos_totales = forms.IntegerField(label="Proyectos totales", min_value=0)

class EstudianteForm(forms.ModelForm):
    class Meta:
        model = Estudiante
        fields = ['nombre', 'apellido', 'email', 'asistencia', 'promedio']

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