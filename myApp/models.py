from django.db import models
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

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.profesion}"

class Curso(models.Model):
    nombre = models.CharField(max_length=100)
    camada = models.IntegerField()

    def __str__(self):
        return self.nombre

class Entregable(models.Model):
    nombre = models.CharField(max_length=100)
    fecha_entrega = models.DateField()
    entregado = models.BooleanField()

    def __str__(self):
        return self.nombre
