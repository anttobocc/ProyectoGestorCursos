from django import forms
from .models import Curso, Profesor, Estudiante, Entregable, Inscripcion, Nota, Resena

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
    
    # CAMPOS PARA CREAR EL USUARIO DEL PROFESOR
    username = forms.CharField(
        max_length=150, 
        label="Nombre de usuario", 
        help_text="Requerido. 150 caracteres o menos. Solo letras, dígitos y @/./+/-/_",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}), 
        label="Contraseña", 
        help_text="Su contraseña debe contener al menos 8 caracteres."
    )

class ProfesorForm(forms.ModelForm):
    # Campos del usuario de Django
    username = forms.CharField(
        max_length=150,
        label="Nombre de usuario",
        help_text="Requerido. 150 caracteres o menos. Solo letras, dígitos y @/./+/-/_",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    user_email = forms.EmailField(
        label="Email del usuario",
        help_text="Correo electrónico vinculado al usuario del sistema",
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Nueva contraseña (opcional)",
        help_text="Dejá vacío para mantener la contraseña actual. Mínimo 8 caracteres.",
        required=False
    )

    class Meta:
        model = Profesor
        fields = ['nombre', 'apellido', 'email', 'profesion']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si estamos editando un profesor existente, cargar datos del usuario
        if self.instance and self.instance.pk and hasattr(self.instance, 'user'):
            self.fields['username'].initial = self.instance.user.username
            self.fields['user_email'].initial = self.instance.user.email

class EstudianteFormulario(forms.Form):
    nombre = forms.CharField(max_length=100, label="Nombre")
    apellido = forms.CharField(max_length=100, label="Apellido")
    email = forms.EmailField(label="Correo Electrónico")
    
    # NUEVOS CAMPOS PARA CREAR EL USUARIO DEL ESTUDIANTE
    username = forms.CharField(
        max_length=150, 
        label="Nombre de usuario", 
        help_text="Requerido. 150 caracteres o menos. Solo letras, dígitos y @/./+/-/_",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}), 
        label="Contraseña", 
        help_text="Su contraseña debe contener al menos 8 caracteres."
    )

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

# NUEVO: Formulario para que el alumno deje su reseña
class ResenaForm(forms.ModelForm):
    class Meta:
        model = Resena
        fields = ['calificacion', 'comentario']
        widgets = {
            'calificacion': forms.Select(
                choices=[(i, f"{i} {'Estrella' if i == 1 else 'Estrellas'}") for i in range(1, 6)], 
                attrs={'class': 'form-select'}
            ),
            'comentario': forms.Textarea(attrs={
                'rows': 3, 
                'class': 'form-control', 
                'placeholder': 'Contanos tu experiencia con este curso... (opcional)'
            }),
        }
        labels = {
            'calificacion': 'Calificación',
            'comentario': 'Tu opinión',
        }