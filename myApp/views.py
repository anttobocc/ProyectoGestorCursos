from django.shortcuts import render, redirect, get_object_or_404
from .models import Curso, Profesor, Estudiante, Entregable
from django.shortcuts import render
from .forms import CursoFormulario

# 1. Vista de inicio

def index(request):
    context = {"mensaje": "¡Nos alegra tenerlos acá en EduControl!"}
    return render(request, 'myApp/index.html', context)

# 2. Vista para buscar cursos
def buscar_curso(request):
    if request.GET.get('camada'):
        camada = request.GET['camada']
        cursos = Curso.objects.filter(camada__icontains=camada)
        return render(request, 'myApp/resultados_busqueda.html', {'cursos': cursos, 'camada': camada})
    return render(request, 'myApp/buscar_curso.html') 

# 3. Formulario para agregar Curso 
def agregar_curso(request):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        camada = request.POST['camada']
        nuevo_curso = Curso(nombre=nombre, camada=camada)
        nuevo_curso.save()
        return redirect('lista_cursos')
    return render(request, 'myApp/curso_form.html') # <--- REVISÁ QUE ESTÉ ASÍ EN TU ARCHIVO

# 4. Vista para listar los cursos
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
    profesores = Profesor.objects.all()
    return render(request, 'myApp/profesores.html', {'profesores': profesores})

def entregables(request):
    entregables = Entregable.objects.all()
    return render(request, 'myApp/entregables.html', {'entregables': entregables})



def cursoFormulario(request):
    if request.method == 'POST':
        form = CursoFormulario(request.POST)
        
        if form.is_valid():
            info = form.cleaned_data
            # Acá después se guardan los datos en la base de datos
            return render(request, "myApp/index.html") # O la plantilla de tu inicio
    else:
        form = CursoFormulario()
        
    return render(request, "myApp/curso_form.html", {"form": form})