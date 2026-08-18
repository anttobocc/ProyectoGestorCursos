from django.urls import path
from .views import (
    index, buscar_curso,
    lista_cursos, cursoFormulario, curso_editar, curso_eliminar,
    lista_estudiantes, detalle_estudiante, estudianteFormulario, estudiante_editar, estudiante_eliminar,
    profesores, profesorFormulario, profesor_editar, profesor_eliminar,
    entregables, entregableFormulario, entregable_editar, entregable_eliminar,
)

app_name = "myapp"

urlpatterns = [
    path('', index, name='index'),
    # Cursos
    path('cursos/', lista_cursos, name='cursos'),
    path('buscar-curso/', buscar_curso, name='buscar_curso'),
    path('cursoFormulario/', cursoFormulario, name='cursoFormulario'),
    path('curso/editar/<int:id>/', curso_editar, name='cursoEditar'),
    path('curso/eliminar/<int:id>/', curso_eliminar, name='cursoEliminar'),
    # Estudiantes
    path('estudiantes/', lista_estudiantes, name='estudiantes'),
    path('estudiante/<int:pk>/', detalle_estudiante, name='detalle_estudiante'),
    path('estudianteFormulario/', estudianteFormulario, name='estudianteFormulario'),
    path('estudiante/editar/<int:id>/', estudiante_editar, name='estudianteEditar'),
    path('estudiante/eliminar/<int:id>/', estudiante_eliminar, name='estudianteEliminar'),
    # Profesores
    path('profesores/', profesores, name='profesores'),
    path('profesorFormulario/', profesorFormulario, name='profesorFormulario'),
    path('profesor/editar/<int:id>/', profesor_editar, name='profesorEditar'),
    path('profesor/eliminar/<int:id>/', profesor_eliminar, name='profesorEliminar'),
    # Entregables
    path('entregables/', entregables, name='entregables'),
    path('entregableFormulario/', entregableFormulario, name='entregableFormulario'),
    path('entregable/editar/<int:id>/', entregable_editar, name='entregableEditar'),
    path('entregable/eliminar/<int:id>/', entregable_eliminar, name='entregableEliminar'),
]