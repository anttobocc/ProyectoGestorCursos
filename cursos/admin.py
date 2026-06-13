from django.contrib import admin

#admin.site.site_header = "Gestor de Cursos"
admin.site.site_title = "Administración"
admin.site.index_title = "Panel de Gestión"

from .models import Estudiante, Profesor, Curso, Entregable

admin.site.register(Estudiante)
admin.site.register(Profesor)
admin.site.register(Curso)
admin.site.register(Entregable)