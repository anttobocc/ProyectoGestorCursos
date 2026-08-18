from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, F
from django.utils import timezone
from .models import Curso, Profesor, Estudiante, Entregable
from .forms import CursoFormulario, CursoForm, ProfesorFormulario, ProfesorForm, EstudianteFormulario, EstudianteForm, EntregableFormulario, EntregableForm

# 1. Vista de inicio

def index(request):
    context = {
        "total_cursos": Curso.objects.count(),
        "total_estudiantes": Estudiante.objects.count(),
        "total_profesores": Profesor.objects.count(),
        "total_entregables": Entregable.objects.count(),
    }
    return render(request, 'myApp/index.html', context)

# 2. Vista para buscar cursos
def buscar_curso(request):
    if request.GET.get('camada'):
        camada = request.GET['camada']
        cursos = Curso.objects.filter(camada__icontains=camada)
        return render(request, 'myApp/resultados_busqueda.html', {'cursos': cursos, 'camada': camada})
    return render(request, 'myApp/buscar_curso.html') 

# 3. Vista para listar los cursos
def lista_cursos(request):
    cursos = Curso.objects.all()
    return render(request, 'myApp/cursos_list.html', {'cursos': cursos})

def lista_estudiantes(request):
    estudiantes = Estudiante.objects.all()
    return render(request, 'myApp/estudiantes_list.html', {'estudiantes': estudiantes})

def detalle_estudiante(request, pk):
    estudiante = get_object_or_404(Estudiante, pk=pk)
    return render(request, 'myApp/estudiante_detail.html', {'estudiante': estudiante})

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

def profesor_eliminar(request, id):
    profesor = get_object_or_404(Profesor, id=id)
    if request.method == 'POST':
        profesor.delete()
        messages.success(request, "Profesor eliminado correctamente.")
        return redirect('myapp:profesores')
    return render(request, 'myApp/profesor_confirm_delete.html', {'profesor': profesor})

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

def estudiante_eliminar(request, id):
    estudiante = get_object_or_404(Estudiante, id=id)
    if request.method == 'POST':
        estudiante.delete()
        messages.success(request, "Estudiante eliminado correctamente.")
        return redirect('myapp:estudiantes')
    return render(request, 'myApp/estudiante_confirm_delete.html', {'estudiante': estudiante})

def entregableFormulario(request):
    if request.method == 'POST':
        form = EntregableFormulario(request.POST)
        if form.is_valid():
            Entregable(
                nombre=form.cleaned_data['nombre'],
                fecha_publicacion=timezone.now(),
                fecha_vencimiento=form.cleaned_data['fecha_vencimiento'],
                cantidad_entregados=0,
            ).save()
            Estudiante.objects.update(proyectos_totales=F('proyectos_totales') + 1)
            messages.success(request, "Entregable agregado correctamente.")
            return redirect('myapp:entregables')
    else:
        form = EntregableFormulario()
    return render(request, 'myApp/entregable_formulario.html', {'form': form})

def entregable_editar(request, id):
    entregable = get_object_or_404(Entregable, id=id)
    if request.method == 'POST':
        estudiantes_antes = set(entregable.estudiantes.all())
        form = EntregableForm(request.POST, instance=entregable)
        if form.is_valid():
            form.save()
            estudiantes_despues = set(entregable.estudiantes.all())

            for estudiante in estudiantes_despues - estudiantes_antes:
                estudiante.proyectos_hechos += 1
                estudiante.save(update_fields=['proyectos_hechos'])

            for estudiante in estudiantes_antes - estudiantes_despues:
                estudiante.proyectos_hechos = max(0, estudiante.proyectos_hechos - 1)
                estudiante.save(update_fields=['proyectos_hechos'])

            entregable.cantidad_entregados = entregable.estudiantes.count()
            entregable.save(update_fields=['cantidad_entregados'])

            messages.success(request, "Entregable actualizado correctamente.")
            return redirect('myapp:entregables')
    else:
        form = EntregableForm(instance=entregable)
    return render(request, 'myApp/entregable_editar.html', {'form': form, 'entregable': entregable})

def entregable_eliminar(request, id):
    entregable = get_object_or_404(Entregable, id=id)
    if request.method == 'POST':
        for estudiante in entregable.estudiantes.all():
            estudiante.proyectos_hechos = max(0, estudiante.proyectos_hechos - 1)
            estudiante.save(update_fields=['proyectos_hechos'])

        entregable.delete()
        Estudiante.objects.update(proyectos_totales=F('proyectos_totales') - 1)
        Estudiante.objects.filter(proyectos_totales__lt=0).update(proyectos_totales=0)

        messages.success(request, "Entregable eliminado correctamente.")
        return redirect('myapp:entregables')
    return render(request, 'myApp/entregable_confirm_delete.html', {'entregable': entregable})

def entregables(request):
    entregables = Entregable.objects.all()
    total_estudiantes = Estudiante.objects.count()
    todos_estudiantes = Estudiante.objects.all()
    return render(request, 'myApp/entregables.html', {
        'entregables': entregables,
        'total_estudiantes': total_estudiantes,
        'todos_estudiantes': todos_estudiantes,
    })



def cursoFormulario(request):
    if request.method == 'POST':
        form = CursoFormulario(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            camada = form.cleaned_data['camada']
            Curso(nombre=nombre, camada=camada).save()
            messages.success(request, "Curso agregado correctamente.")
            return redirect('myapp:cursos')
    else:
        form = CursoFormulario()
    return render(request, 'myApp/curso_form.html', {'form': form})

def curso_editar(request, id):
    curso = get_object_or_404(Curso, id=id)
    if request.method == 'POST':
        form = CursoForm(request.POST, instance=curso)
        if form.is_valid():
            form.save()
            messages.success(request, "Curso actualizado correctamente.")
            return redirect('myapp:cursos')
    else:
        form = CursoForm(instance=curso)
    return render(request, 'myApp/curso_editar.html', {'form': form, 'curso': curso})

def curso_eliminar(request, id):
    curso = get_object_or_404(Curso, id=id)
    if request.method == 'POST':
        curso.delete()
        messages.success(request, "Curso eliminado correctamente.")
        return redirect('myapp:cursos')
    return render(request, 'myApp/curso_confirm_delete.html', {'curso': curso})