from django.urls import path
from .views import (
    login_view, logout_view,
    index, buscar_curso,
    lista_cursos, cursoFormulario, curso_editar, curso_eliminar, admin_curso_detail, admin_estudiante_curso_eliminar,
    lista_estudiantes, detalle_estudiante, estudianteFormulario, estudiante_editar, estudiante_eliminar,
    profesores, profesorFormulario, profesor_editar, profesor_eliminar,
    entregable_editar, entregable_eliminar,
    mis_cursos, curso_detail, curso_entregables, estudiante_curso_eliminar, entregable_crear_en_curso, inscripcion_editar,
)

app_name = "myapp"

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('', index, name='index'),
    # Cursos
    path('cursos/', lista_cursos, name='cursos'),
    path('buscar-curso/', buscar_curso, name='buscar_curso'),
    path('cursoFormulario/', cursoFormulario, name='cursoFormulario'),
    path('curso/editar/<int:id>/', curso_editar, name='cursoEditar'),
    path('curso/eliminar/<int:id>/', curso_eliminar, name='cursoEliminar'),
    path('curso/<int:id>/', admin_curso_detail, name='cursoDetalleAdmin'),
    path('curso/<int:curso_id>/alumno/<int:estudiante_id>/baja/', admin_estudiante_curso_eliminar, name='adminEstudianteCursoEliminar'),
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
    path('entregable/editar/<int:id>/', entregable_editar, name='entregableEditar'),
    path('entregable/eliminar/<int:id>/', entregable_eliminar, name='entregableEliminar'),
    # Profesor
    path('mis-cursos/', mis_cursos, name='mis_cursos'),
    path('mis-cursos/<int:id>/', curso_detail, name='curso_detail'),
    path('mis-cursos/<int:id>/entregables/', curso_entregables, name='curso_entregables'),
    path('mis-cursos/<int:curso_id>/alumno/<int:estudiante_id>/baja/', estudiante_curso_eliminar, name='estudianteCursoEliminar'),
    path('mis-cursos/<int:curso_id>/entregables/crear/', entregable_crear_en_curso, name='entregableCrearEnCurso'),
    path('mis-cursos/<int:curso_id>/alumno/<int:estudiante_id>/editar/', inscripcion_editar, name='inscripcionEditar'),
]