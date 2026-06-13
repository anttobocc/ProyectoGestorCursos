from django.shortcuts import render

def index(request):
    contexto = {
    "mensaje": "Sistema para la administración de cursos, estudiantes y profesores."
    }

    return render(
        request,
        "cursos/index.html",
        contexto
    )