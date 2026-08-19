from .decorators import es_administrador, es_profesor


def roles(request):
    return {
        'es_admin': es_administrador(request.user),
        'es_profesor': es_profesor(request.user),
    }
