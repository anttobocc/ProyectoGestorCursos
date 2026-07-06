from django.urls import path
from .views import index, buscar_curso, agregar_curso, lista_cursos, lista_estudiantes, detalle_estudiante, profesores, entregables, cursoFormulario

urlpatterns = [
    path('', index, name='index'),
    path('cursos/', lista_cursos, name='lista_cursos'),
    path('curso/nuevo/', agregar_curso, name='agregar_curso'),
    path('buscar-curso/', buscar_curso, name='buscar_curso'),
    path('estudiantes/', lista_estudiantes, name='lista_estudiantes'),
    path('estudiante/<int:pk>/', detalle_estudiante, name='detalle_estudiante'),
    path('profesores/', profesores, name='lista_profesores'),
    path('entregables/', entregables, name='lista_entregables'),
   path('cursoFormulario/', cursoFormulario, name='cursoFormulario'),
]