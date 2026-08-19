from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q, F
from django.utils import timezone
from .models import Curso, Profesor, Estudiante, Entregable, Inscripcion
from .forms import CursoForm, ProfesorFormulario, ProfesorForm, EstudianteFormulario, EstudianteForm, EntregableFormulario, EntregableForm
from .decorators import admin_required, profesor_required, es_administrador, profesor_tiene_acceso_a_curso


def _entregables_info_de_curso(curso, inscripciones):
    total_alumnos = inscripciones.count()
    resultado = []
    for entregable in Entregable.objects.filter(curso=curso).order_by('id'):
        entregados_ids = set(
            entregable.estudiantes.filter(inscripciones__curso=curso).values_list('id', flat=True)
        )
        detalle = [
            {'estudiante': inscripcion.estudiante, 'entrego': inscripcion.estudiante_id in entregados_ids}
            for inscripcion in inscripciones
        ]
        cantidad = len(entregados_ids)
        porcentaje = round((cantidad / total_alumnos) * 100) if total_alumnos > 0 else 0
        resultado.append({
            'entregable': entregable,
            'cantidad_entregados': cantidad,
            'total_alumnos': total_alumnos,
            'porcentaje': porcentaje,
            'detalle': detalle,
        })
    return resultado

# 0. Vistas de autenticación

def login_view(request):
    if request.user.is_authenticated:
        return redirect(settings.LOGIN_REDIRECT_URL)

    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect(settings.LOGIN_REDIRECT_URL)
        else:
            error = "Usuario o contraseña incorrectos."

    return render(request, 'myApp/login.html', {'error': error})


def logout_view(request):
    auth_logout(request)
    return redirect('myapp:login')

# 1. Vista de inicio

@login_required
def index(request):
    context = {
        "total_cursos": Curso.objects.count(),
        "total_estudiantes": Estudiante.objects.count(),
        "total_profesores": Profesor.objects.count(),
        "total_entregables": Entregable.objects.count(),
    }
    return render(request, 'myApp/index.html', context)

# 2. Vista para buscar cursos
@login_required
def buscar_curso(request):
    if request.GET.get('camada'):
        camada = request.GET['camada']
        cursos = Curso.objects.filter(camada__icontains=camada)
        return render(request, 'myApp/resultados_busqueda.html', {'cursos': cursos, 'camada': camada})
    return render(request, 'myApp/buscar_curso.html') 

# 3. Vista para listar los cursos
@login_required
def lista_cursos(request):
    if es_administrador(request.user):
        cursos = Curso.objects.all()
    else:
        cursos = Curso.objects.filter(profesores__user=request.user)
    cursos = cursos.prefetch_related('profesores', 'inscripciones')
    return render(request, 'myApp/cursos_list.html', {'cursos': cursos})

@login_required
def lista_estudiantes(request):
    estudiantes = Estudiante.objects.all()
    return render(request, 'myApp/estudiantes_list.html', {'estudiantes': estudiantes})

@login_required
def detalle_estudiante(request, pk):
    estudiante = get_object_or_404(Estudiante, pk=pk)
    inscripciones = estudiante.inscripciones.select_related('curso').all()
    return render(request, 'myApp/estudiante_detail.html', {'estudiante': estudiante, 'inscripciones': inscripciones})

@admin_required
def profesores(request):
    query = request.GET.get('q')
    if query:
        profesores = Profesor.objects.filter(
            Q(nombre__icontains=query) |
            Q(apellido__icontains=query) |
            Q(profesion__icontains=query)
        )
    else:
        profesores = Profesor.objects.all()
    return render(request, 'myApp/profesores.html', {'profesores': profesores, 'query': query})

@admin_required
def profesorFormulario(request):
    if request.method == 'POST':
        form = ProfesorFormulario(request.POST)
        if form.is_valid():
            Profesor(
                nombre=form.cleaned_data['nombre'],
                apellido=form.cleaned_data['apellido'],
                email=form.cleaned_data['email'],
                profesion=form.cleaned_data['profesion'],
            ).save()
            messages.success(request, "Profesor agregado correctamente.")
            return redirect('myapp:profesores')
    else:
        form = ProfesorFormulario()
    return render(request, 'myApp/profesor_formulario.html', {'form': form})

@admin_required
def profesor_editar(request, id):
    profesor = get_object_or_404(Profesor, id=id)
    if request.method == 'POST':
        form = ProfesorForm(request.POST, instance=profesor)
        if form.is_valid():
            form.save()
            messages.success(request, "Profesor actualizado correctamente.")
            return redirect('myapp:profesores')
    else:
        form = ProfesorForm(instance=profesor)
    return render(request, 'myApp/profesor_editar.html', {'form': form, 'profesor': profesor})

@admin_required
def profesor_eliminar(request, id):
    profesor = get_object_or_404(Profesor, id=id)
    if request.method == 'POST':
        profesor.delete()
        messages.success(request, "Profesor eliminado correctamente.")
        return redirect('myapp:profesores')
    return render(request, 'myApp/profesor_confirm_delete.html', {'profesor': profesor})

@admin_required
def estudianteFormulario(request):
    if request.method == 'POST':
        form = EstudianteFormulario(request.POST)
        if form.is_valid():
            Estudiante(
                nombre=form.cleaned_data['nombre'],
                apellido=form.cleaned_data['apellido'],
                email=form.cleaned_data['email'],
                asistencia=form.cleaned_data['asistencia'],
                promedio=form.cleaned_data['promedio'],
                proyectos_hechos=form.cleaned_data['proyectos_hechos'],
                proyectos_totales=form.cleaned_data['proyectos_totales'],
            ).save()
            messages.success(request, "Estudiante agregado correctamente.")
            return redirect('myapp:estudiantes')
    else:
        form = EstudianteFormulario()
    return render(request, 'myApp/estudiante_formulario.html', {'form': form})

@admin_required
def estudiante_editar(request, id):
    estudiante = get_object_or_404(Estudiante, id=id)
    if request.method == 'POST':
        form = EstudianteForm(request.POST, instance=estudiante)
        if form.is_valid():
            form.save()
            messages.success(request, "Estudiante actualizado correctamente.")
            return redirect('myapp:estudiantes')
    else:
        form = EstudianteForm(instance=estudiante)
    return render(request, 'myApp/estudiante_editar.html', {'form': form, 'estudiante': estudiante})

@admin_required
def estudiante_eliminar(request, id):
    estudiante = get_object_or_404(Estudiante, id=id)
    if request.method == 'POST':
        estudiante.delete()
        messages.success(request, "Estudiante eliminado correctamente.")
        return redirect('myapp:estudiantes')
    return render(request, 'myApp/estudiante_confirm_delete.html', {'estudiante': estudiante})

@login_required
def entregable_editar(request, id):
    entregable = get_object_or_404(Entregable, id=id)
    curso = entregable.curso
    if curso is None or not profesor_tiene_acceso_a_curso(request.user, curso):
        raise PermissionDenied
    alumnos_del_curso = Estudiante.objects.filter(inscripciones__curso=curso)

    if request.method == 'POST':
        estudiantes_antes = set(entregable.estudiantes.all())
        form = EntregableForm(request.POST, instance=entregable)
        form.fields['estudiantes'].queryset = alumnos_del_curso
        if form.is_valid():
            with transaction.atomic():
                form.save()
                estudiantes_despues = set(entregable.estudiantes.all())

                nuevos = estudiantes_despues - estudiantes_antes
                quitados = estudiantes_antes - estudiantes_despues

                if nuevos:
                    Inscripcion.objects.filter(
                        curso=curso, estudiante__in=nuevos
                    ).update(proyectos_hechos=F('proyectos_hechos') + 1)

                if quitados:
                    Inscripcion.objects.filter(
                        curso=curso, estudiante__in=quitados
                    ).update(proyectos_hechos=F('proyectos_hechos') - 1)
                    Inscripcion.objects.filter(
                        curso=curso, proyectos_hechos__lt=0
                    ).update(proyectos_hechos=0)

                entregable.cantidad_entregados = entregable.estudiantes.filter(
                    inscripciones__curso=curso
                ).count()
                entregable.save(update_fields=['cantidad_entregados'])

            messages.success(request, "Entregable actualizado correctamente.")
            if es_administrador(request.user):
                return redirect('myapp:cursoDetalleAdmin', id=curso.id)
            return redirect('myapp:curso_detail', id=curso.id)
    else:
        form = EntregableForm(instance=entregable)
        form.fields['estudiantes'].queryset = alumnos_del_curso
    return render(request, 'myApp/entregable_editar.html', {'form': form, 'entregable': entregable})

@login_required
def entregable_eliminar(request, id):
    entregable = get_object_or_404(Entregable, id=id)
    curso = entregable.curso
    if curso is None or not profesor_tiene_acceso_a_curso(request.user, curso):
        raise PermissionDenied
    if request.method == 'POST':
        with transaction.atomic():
            estudiantes_que_entregaron = list(
                entregable.estudiantes.filter(inscripciones__curso=curso)
            )
            if estudiantes_que_entregaron:
                Inscripcion.objects.filter(
                    curso=curso, estudiante__in=estudiantes_que_entregaron
                ).update(proyectos_hechos=F('proyectos_hechos') - 1)
                Inscripcion.objects.filter(
                    curso=curso, proyectos_hechos__lt=0
                ).update(proyectos_hechos=0)

            entregable.delete()

            Inscripcion.objects.filter(curso=curso).update(proyectos_totales=F('proyectos_totales') - 1)
            Inscripcion.objects.filter(curso=curso, proyectos_totales__lt=0).update(proyectos_totales=0)

        messages.success(request, "Entregable eliminado correctamente.")
        if es_administrador(request.user):
            return redirect('myapp:cursoDetalleAdmin', id=curso.id)
        return redirect('myapp:curso_detail', id=curso.id)
    return render(request, 'myApp/entregable_confirm_delete.html', {'entregable': entregable, 'curso': curso})



@admin_required
def cursoFormulario(request):
    if request.method == 'POST':
        form = CursoForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                curso = form.save(commit=False)
                curso.save()
                form.save_m2m()  # guarda curso.profesores

                alumnos_seleccionados = form.cleaned_data['alumnos']
                proyectos_totales_inicial = Entregable.objects.filter(curso=curso).count()
                for estudiante in alumnos_seleccionados:
                    Inscripcion.objects.create(
                        estudiante=estudiante,
                        curso=curso,
                        asistencia=0,
                        promedio=0,
                        proyectos_hechos=0,
                        proyectos_totales=proyectos_totales_inicial,
                    )
            messages.success(request, "Curso agregado correctamente.")
            return redirect('myapp:cursos')
    else:
        form = CursoForm()
    return render(request, 'myApp/curso_form.html', {'form': form})

@admin_required
def curso_editar(request, id):
    curso = get_object_or_404(Curso, id=id)
    if request.method == 'POST':
        form = CursoForm(request.POST, instance=curso)
        if form.is_valid():
            with transaction.atomic():
                form.save()  # guarda nombre, camada y curso.profesores

                alumnos_seleccionados = set(form.cleaned_data['alumnos'])
                alumnos_actuales = set(Estudiante.objects.filter(inscripciones__curso=curso))

                nuevos = alumnos_seleccionados - alumnos_actuales
                quitados = alumnos_actuales - alumnos_seleccionados

                proyectos_totales_inicial = Entregable.objects.filter(curso=curso).count()
                for estudiante in nuevos:
                    Inscripcion.objects.create(
                        estudiante=estudiante,
                        curso=curso,
                        asistencia=0,
                        promedio=0,
                        proyectos_hechos=0,
                        proyectos_totales=proyectos_totales_inicial,
                    )

                if quitados:
                    Inscripcion.objects.filter(curso=curso, estudiante__in=quitados).delete()

            messages.success(request, "Curso actualizado correctamente.")
            return redirect('myapp:cursos')
    else:
        form = CursoForm(instance=curso, initial={
            'alumnos': Estudiante.objects.filter(inscripciones__curso=curso),
        })
    return render(request, 'myApp/curso_editar.html', {'form': form, 'curso': curso})

@admin_required
def admin_curso_detail(request, id):
    curso = get_object_or_404(Curso, id=id)
    inscripciones = Inscripcion.objects.filter(curso=curso).select_related('estudiante')
    entregables_info = _entregables_info_de_curso(curso, inscripciones)
    return render(request, 'myApp/admin_curso_detail.html', {
        'curso': curso,
        'inscripciones': inscripciones,
        'entregables_info': entregables_info,
    })

@login_required
@admin_required
def admin_estudiante_curso_eliminar(request, curso_id, estudiante_id):
    curso = get_object_or_404(Curso, id=curso_id)
    inscripcion = get_object_or_404(Inscripcion, curso=curso, estudiante_id=estudiante_id)
    if request.method == 'POST':
        nombre_estudiante = str(inscripcion.estudiante)
        inscripcion.delete()
        messages.success(request, f"{nombre_estudiante} fue dado de baja de {curso.nombre}.")
        return redirect('myapp:cursoDetalleAdmin', id=curso.id)
    return render(request, 'myApp/admin_estudiante_curso_confirm_delete.html', {
        'curso': curso,
        'inscripcion': inscripcion,
    })

@admin_required
def curso_eliminar(request, id):
    curso = get_object_or_404(Curso, id=id)
    if request.method == 'POST':
        curso.delete()
        messages.success(request, "Curso eliminado correctamente.")
        return redirect('myapp:cursos')
    return render(request, 'myApp/curso_confirm_delete.html', {'curso': curso})

# 4. Vistas del Profesor

@login_required
@profesor_required
def mis_cursos(request):
    cursos = Curso.objects.filter(profesores__user=request.user)
    return render(request, 'myApp/mis_cursos.html', {'cursos': cursos})

@login_required
@profesor_required
def curso_detail(request, id):
    curso = get_object_or_404(Curso, id=id, profesores__user=request.user)
    inscripciones = Inscripcion.objects.filter(curso=curso).select_related('estudiante')
    entregables_info = _entregables_info_de_curso(curso, inscripciones)

    return render(request, 'myApp/curso_detail.html', {
        'curso': curso,
        'inscripciones': inscripciones,
        'entregables_info': entregables_info,
    })

@login_required
@profesor_required
def estudiante_curso_eliminar(request, curso_id, estudiante_id):
    curso = get_object_or_404(Curso, id=curso_id, profesores__user=request.user)
    inscripcion = get_object_or_404(Inscripcion, curso=curso, estudiante_id=estudiante_id)
    if request.method == 'POST':
        nombre_estudiante = str(inscripcion.estudiante)
        inscripcion.delete()
        messages.success(request, f"{nombre_estudiante} fue dado de baja de {curso.nombre}.")
        return redirect('myapp:curso_detail', id=curso.id)
    return render(request, 'myApp/estudiante_curso_confirm_delete.html', {
        'curso': curso,
        'inscripcion': inscripcion,
    })

@login_required
def entregable_crear_en_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    if not profesor_tiene_acceso_a_curso(request.user, curso):
        raise PermissionDenied
    if request.method == 'POST':
        form = EntregableFormulario(request.POST)
        if form.is_valid():
            with transaction.atomic():
                Entregable.objects.create(
                    nombre=form.cleaned_data['nombre'],
                    fecha_publicacion=timezone.now(),
                    fecha_vencimiento=form.cleaned_data['fecha_vencimiento'],
                    cantidad_entregados=0,
                    curso=curso,
                )
                Inscripcion.objects.filter(curso=curso).update(proyectos_totales=F('proyectos_totales') + 1)
            messages.success(request, "Entregable agregado correctamente.")
            if es_administrador(request.user):
                return redirect('myapp:cursoDetalleAdmin', id=curso.id)
            return redirect('myapp:curso_detail', id=curso.id)
    else:
        form = EntregableFormulario()
    return render(request, 'myApp/entregable_crear_en_curso.html', {'form': form, 'curso': curso})