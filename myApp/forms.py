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

class CursoImagenForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = ['imagen']

class ProfesorFormulario(forms.Form):
    nombre = forms.CharField(max_length=100, label="Nombre")
    apellido = forms.CharField(max_length=100, label="Apellido")
    email = forms.EmailField(label="Correo Electrónico")

    # CAMPOS PARA CREAR EL USUARIO DEL DOCENTE
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
        help_text="150 caracteres o menos. Solo letras, dígitos y @/./+/-/_. Dejalo vacío si el docente todavía no tiene cuenta.",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Contraseña",
        help_text="Dejá vacío para mantener la contraseña actual. Si el docente no tiene cuenta, es obligatoria para crear una (mínimo 8 caracteres).",
        required=False
    )

    class Meta:
        model = Profesor
        fields = ['nombre', 'apellido', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si estamos editando un docente existente que ya tiene cuenta, cargar su usuario
        if self.instance and self.instance.pk and self.instance.user:
            self.fields['username'].initial = self.instance.user.username
        else:
            self.fields['username'].required = False

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
    # Campo del usuario de Django (para vincular/editar la cuenta de acceso del alumno).
    # El nombre de usuario para iniciar sesión es siempre el documento del alumno.
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Contraseña",
        help_text="Dejá vacío para mantener la contraseña actual. Si el alumno no tiene cuenta, es obligatoria para crear una (mínimo 8 caracteres).",
        required=False
    )

    class Meta:
        model = Estudiante
        fields = ['nombre', 'apellido', 'email', 'documento']  # AGREGADO: documento

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

# Formulario para que el alumno deje su reseña
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

# NUEVO: Formulario para el autorregistro del estudiante
class RegistroEstudianteForm(forms.Form):
    nombre = forms.CharField(max_length=100, label="Nombre")
    apellido = forms.CharField(max_length=100, label="Apellido")
    email = forms.EmailField(label="Correo Electrónico")
    documento = forms.CharField(
        max_length=20,
        label="Documento",
        help_text="DNI sin puntos. Vas a usarlo para iniciar sesión."
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Contraseña",
        help_text="Debe contener al menos 8 caracteres."
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Confirmar contraseña"
    )

    def clean_documento(self):
        documento = self.cleaned_data['documento'].strip()
        if Estudiante.objects.filter(documento=documento).exists():
            raise forms.ValidationError("Ya existe una cuenta registrada con ese documento.")
        return documento

    def clean_password(self):
        password = self.cleaned_data['password']
        if len(password) < 8:
            raise forms.ValidationError("La contraseña debe tener al menos 8 caracteres.")
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')
        if password and password2 and password != password2:
            self.add_error('password2', "Las contraseñas no coinciden.")
        return cleaned_data