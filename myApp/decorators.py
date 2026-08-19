from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied


def es_administrador(user):
    return user.is_authenticated and user.groups.filter(name='Administrador').exists()


def es_profesor(user):
    return user.is_authenticated and user.groups.filter(name='Profesor').exists()


def admin_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not es_administrador(request.user):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper


def profesor_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not es_profesor(request.user):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper


def profesor_tiene_acceso_a_curso(user, curso):
    """Un Administrador puede acceder a cualquier curso.
    Un Profesor solo puede acceder a los cursos donde figura en curso.profesores."""
    if es_administrador(user):
        return True
    if not es_profesor(user):
        return False
    try:
        profesor = user.profesor
    except ObjectDoesNotExist:
        return False
    return curso.profesores.filter(pk=profesor.pk).exists()
