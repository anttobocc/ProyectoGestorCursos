from django import forms
from .models import Curso, Profesor, Estudiante, Entregable, Inscripcion, Nota

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
        fields = ['observaciones']
        widgets = {
            'observaciones': forms.Textarea(attrs={'rows': 2}),
        }
        labels = {
            'observaciones': 'Observaciones generales',
        }

class NotaForm(forms.ModelForm):
    class Meta:
        model = Nota
        fields = ['nombre', 'tipo', 'fecha', 'nota', 'observaciones']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'nota': forms.NumberInput(attrs={'step': '0.1', 'min': '0', 'max': '10'}),
        }
        labels = {
            'nota': 'Nota (0-10)',
        }

class EntregableForm(forms.ModelForm):
    class Meta:
        model = Entregable
        fields = ['nombre', 'fecha_publicacion', 'fecha_vencimiento', 'publicado', 'consigna', 'archivo']
        widgets = {
            'fecha_publicacion': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'fecha_vencimiento': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'publicado': forms.CheckboxInput(),
            'consigna': forms.Textarea(attrs={'rows': 8}),
        }
        labels = {
            'publicado': 'Publicado (visible para los alumnos)',
        }