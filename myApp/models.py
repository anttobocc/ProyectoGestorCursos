from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class Estudiante(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField()
    documento = models.CharField(max_length=20, unique=True, null=True, blank=True, verbose_name="Documento")

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='estudiante',
    )
    
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
    publicado = models.BooleanField(default=True)
    consigna = models.TextField(blank=True, default='')
    archivo = models.FileField(upload_to='entregables/', blank=True, null=True)
    cantidad_entregados = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
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

class Entrega(models.Model):
    entregable = models.ForeignKey(
        Entregable,
        on_delete=models.CASCADE,
        related_name='entregas',
    )
    estudiante = models.ForeignKey(
        Estudiante,
        on_delete=models.CASCADE,
        related_name='entregas',
    )
    fecha_entrega = models.DateTimeField()
    archivo = models.FileField(upload_to='entregas/', blank=True, null=True)
    nota = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(1.0), MaxValueValidator(10.0)]
    )

    class Meta:
        unique_together = ('entregable', 'estudiante')

    def __str__(self):
        return f"{self.estudiante} - {self.entregable}"

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
    observaciones = models.TextField(blank=True, default='')

    class Meta:
        unique_together = ('estudiante', 'curso')

    def __str__(self):
        return f"{self.estudiante} - {self.curso}"

class Nota(models.Model):
    TIPO_ENTREGABLE = 'entregable'
    TIPO_PARTICIPACION = 'participacion'
    TIPO_EVALUACION = 'evaluacion'
    TIPO_CHOICES = [
        (TIPO_ENTREGABLE, 'Entregable'),
        (TIPO_PARTICIPACION, 'Participación'),
        (TIPO_EVALUACION, 'Evaluación'),
    ]

    inscripcion = models.ForeignKey(
        Inscripcion,
        on_delete=models.CASCADE,
        related_name='notas',
    )
    entrega = models.OneToOneField(
        Entrega,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='nota_academica',
    )
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default=TIPO_ENTREGABLE)
    fecha = models.DateField(null=True, blank=True)
    nota = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(10.0)])
    observaciones = models.CharField(max_length=255, blank=True, default='')

    def __str__(self):
        return f"{self.nombre} - {self.inscripcion}"

class RegistroAsistencia(models.Model):
    inscripcion = models.ForeignKey(
        Inscripcion,
        on_delete=models.CASCADE,
        related_name='registros_asistencia',
    )
    fecha = models.DateField()
    presente = models.BooleanField(default=False)

    class Meta:
        unique_together = ('inscripcion', 'fecha')

    def __str__(self):
        return f"{self.inscripcion} - {self.fecha} - {'Presente' if self.presente else 'Ausente'}"

class Resena(models.Model):
    estudiante = models.ForeignKey(
        Estudiante, 
        on_delete=models.CASCADE, 
        related_name='resenas'
    )
    curso = models.ForeignKey(
        Curso, 
        on_delete=models.CASCADE, 
        related_name='resenas'
    )
    calificacion = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comentario = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('estudiante', 'curso')

    def __str__(self):
        return f"Reseña de {self.estudiante} en {self.curso} ({self.calificacion}⭐)"