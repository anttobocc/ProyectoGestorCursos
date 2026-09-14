from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Permite acceder a un valor de un diccionario por su clave en el template."""
    return dictionary.get(key, 0)