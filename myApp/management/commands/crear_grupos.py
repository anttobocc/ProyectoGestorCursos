from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Crea (de forma idempotente) los grupos Administrador y Profesor."

    def handle(self, *args, **options):
        admin_group, admin_creado = Group.objects.get_or_create(name='Administrador')
        profesor_group, profesor_creado = Group.objects.get_or_create(name='Profesor')

        if admin_creado:
            self.stdout.write(self.style.SUCCESS("Grupo 'Administrador' creado."))
        else:
            self.stdout.write("Grupo 'Administrador' ya existía.")

        if profesor_creado:
            self.stdout.write(self.style.SUCCESS("Grupo 'Profesor' creado."))
        else:
            self.stdout.write("Grupo 'Profesor' ya existía.")
