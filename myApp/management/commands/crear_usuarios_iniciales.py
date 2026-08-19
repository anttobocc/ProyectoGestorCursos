import getpass

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError

from myApp.models import Profesor

User = get_user_model()


class Command(BaseCommand):
    help = (
        "Crea (de forma idempotente) las cuentas iniciales: "
        "un usuario Administrador y el usuario del profesor Carlos Aguirre, "
        "vinculado a Profesor.user."
    )

    def handle(self, *args, **options):
        try:
            grupo_admin = Group.objects.get(name='Administrador')
            grupo_profesor = Group.objects.get(name='Profesor')
        except Group.DoesNotExist:
            raise CommandError(
                "Los grupos 'Administrador'/'Profesor' no existen. "
                "Ejecutá primero: python manage.py crear_grupos"
            )

        # --- Usuario Administrador ---
        admin_username = input("Nombre de usuario para el Administrador: ").strip()
        if User.objects.filter(username=admin_username).exists():
            self.stdout.write(f"El usuario '{admin_username}' ya existe. No se modifica.")
            admin_user = User.objects.get(username=admin_username)
        else:
            admin_password = getpass.getpass("Contraseña para el Administrador: ")
            admin_user = User.objects.create_user(
                username=admin_username,
                password=admin_password,
            )
            self.stdout.write(self.style.SUCCESS(f"Usuario '{admin_username}' creado."))
        admin_user.groups.add(grupo_admin)

        # --- Usuario para Carlos Aguirre (Profesor id=1) ---
        try:
            carlos = Profesor.objects.get(id=1)
        except Profesor.DoesNotExist:
            raise CommandError("No se encontró el Profesor con id=1 (Carlos Aguirre).")

        if carlos.user is not None:
            self.stdout.write(
                f"Carlos Aguirre ya tiene un usuario vinculado ('{carlos.user.username}'). No se modifica."
            )
        else:
            carlos_username = input("Nombre de usuario para Carlos Aguirre: ").strip()
            if User.objects.filter(username=carlos_username).exists():
                carlos_user = User.objects.get(username=carlos_username)
                self.stdout.write(f"El usuario '{carlos_username}' ya existía, se reutiliza para vincular.")
            else:
                carlos_password = getpass.getpass("Contraseña para Carlos Aguirre: ")
                carlos_user = User.objects.create_user(
                    username=carlos_username,
                    password=carlos_password,
                )
                self.stdout.write(self.style.SUCCESS(f"Usuario '{carlos_username}' creado."))
            carlos_user.groups.add(grupo_profesor)
            carlos.user = carlos_user
            carlos.save(update_fields=['user'])
            self.stdout.write(self.style.SUCCESS("Profesor.user de Carlos Aguirre vinculado correctamente."))
