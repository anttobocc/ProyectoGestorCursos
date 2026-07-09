from django.db import models

class Estudiante(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return f"{self.nombre} {self.apellido}"
    
    class Meta:
        verbose_name = "Estudiante"
        verbose_name_plural = "Estudiantes"


class Profesor(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField()
    profesion = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"
    
    class Meta:
        verbose_name = "Profesor"
        verbose_name_plural = "Profesores"



class Curso(models.Model):
    nombre = models.CharField(max_length=100)
    camada = models.IntegerField()

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Curso"
        verbose_name_plural = "Cursos"
    


class Entregable(models.Model):
    nombre = models.CharField(max_length=100)
    fecha_entrega = models.DateField()
    entregado = models.BooleanField()

    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Entregable"
        verbose_name_plural = "Entregables"