from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class Estudiante(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField()
    
    asistencia = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    promedio = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )   
    proyectos_hechos = models.IntegerField(default=0) 
    proyectos_totales = models.IntegerField(default=15) 

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

class Profesor(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField()
    profesion = models.CharField(max_length=100)

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='profesor',
    )

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.profesion}"

class Curso(models.Model):
    nombre = models.CharField(max_length=100)
    camada = models.IntegerField()

    profesores = models.ManyToManyField(
        Profesor,
        related_name='cursos',
        blank=True,
    )

    def __str__(self):
        return self.nombre

class Entregable(models.Model):
    nombre = models.CharField(max_length=100)
    fecha_publicacion = models.DateTimeField(null=True, blank=True)
    fecha_vencimiento = models.DateTimeField(null=True, blank=True)
    cantidad_entregados = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    estudiantes = models.ManyToManyField(
        Estudiante,
        related_name='entregables_completados',
        blank=True
    )
    curso = models.ForeignKey(
        Curso,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='entregables',
    )

    def __str__(self):
        return self.nombre

class Inscripcion(models.Model):
    estudiante = models.ForeignKey(
        Estudiante,
        on_delete=models.CASCADE,
        related_name='inscripciones',
    )
    curso = models.ForeignKey(
        Curso,
        on_delete=models.CASCADE,
        related_name='inscripciones',
    )

    asistencia = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    promedio = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )
    proyectos_hechos = models.IntegerField(default=0)
    proyectos_totales = models.IntegerField(default=0)

    class Meta:
        unique_together = ('estudiante', 'curso')

    def __str__(self):
        return f"{self.estudiante} - {self.curso}"
