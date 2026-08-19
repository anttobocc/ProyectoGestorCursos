from django.db import migrations


def migrar_datos(apps, schema_editor):
    Estudiante = apps.get_model('myApp', 'Estudiante')
    Profesor = apps.get_model('myApp', 'Profesor')
    Curso = apps.get_model('myApp', 'Curso')
    Entregable = apps.get_model('myApp', 'Entregable')
    Inscripcion = apps.get_model('myApp', 'Inscripcion')

    curso = Curso.objects.get(id=2)  # Laboratorio de Programación

    # 1. Asignar a Carlos Aguirre como profesor del curso
    carlos = Profesor.objects.get(id=1)
    curso.profesores.add(carlos)

    # 2. Asignar los 3 entregables existentes al curso
    Entregable.objects.filter(id__in=[1, 3, 4]).update(curso=curso)

    # 3. Crear las 4 Inscripciones, copiando exactamente los valores actuales
    datos_estudiantes = {
        1: {'asistencia': 84, 'promedio': 8.5, 'proyectos_hechos': 3, 'proyectos_totales': 3},  # Mimbí Cáceres
        2: {'asistencia': 85, 'promedio': 8.0, 'proyectos_hechos': 2, 'proyectos_totales': 3},  # Lucero Lasala
        3: {'asistencia': 75, 'promedio': 7.0, 'proyectos_hechos': 2, 'proyectos_totales': 3},  # Bianca Godoy Longoni
        5: {'asistencia': 80, 'promedio': 9.0, 'proyectos_hechos': 3, 'proyectos_totales': 3},  # Antonella Boccalandro
    }

    for estudiante_id, valores in datos_estudiantes.items():
        estudiante = Estudiante.objects.get(id=estudiante_id)
        Inscripcion.objects.create(
            estudiante=estudiante,
            curso=curso,
            asistencia=valores['asistencia'],
            promedio=valores['promedio'],
            proyectos_hechos=valores['proyectos_hechos'],
            proyectos_totales=valores['proyectos_totales'],
        )

    # 4. Reconstruir únicamente el M2M de Proyecto 1 (id=1) con los 4 estudiantes
    proyecto1 = Entregable.objects.get(id=1)
    proyecto1.estudiantes.set(Estudiante.objects.filter(id__in=[1, 2, 3, 5]))
    # Nota: NO se toca proyecto1.cantidad_entregados (ya vale 4, coincide con el M2M reconstruido)


def revertir_datos(apps, schema_editor):
    Estudiante = apps.get_model('myApp', 'Estudiante')
    Profesor = apps.get_model('myApp', 'Profesor')
    Curso = apps.get_model('myApp', 'Curso')
    Entregable = apps.get_model('myApp', 'Entregable')
    Inscripcion = apps.get_model('myApp', 'Inscripcion')

    curso = Curso.objects.get(id=2)
    carlos = Profesor.objects.get(id=1)

    curso.profesores.remove(carlos)
    Entregable.objects.filter(id__in=[1, 3, 4]).update(curso=None)
    Inscripcion.objects.filter(curso=curso, estudiante_id__in=[1, 2, 3, 5]).delete()

    proyecto1 = Entregable.objects.get(id=1)
    proyecto1.estudiantes.clear()


class Migration(migrations.Migration):

    dependencies = [
        ('myApp', '0008_curso_profesores_entregable_curso_profesor_user_and_more'),
    ]

    operations = [
        migrations.RunPython(migrar_datos, revertir_datos),
    ]
