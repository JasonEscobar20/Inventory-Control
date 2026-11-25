import secrets
import string

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


def generar_password(longitud=14):
    """
    Genera un password aleatorio con letras, números y símbolos.
    """
    if longitud < 8:
        raise ValueError("La longitud mínima recomendada es 8.")

    letras = string.ascii_letters
    numeros = string.digits
    simbolos = "!@#$%&*_-"

    # Garantiza al menos un carácter de cada tipo.
    password = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.ascii_lowercase),
        secrets.choice(numeros),
        secrets.choice(simbolos),
    ]

    caracteres = letras + numeros + simbolos

    password.extend(
        secrets.choice(caracteres)
        for _ in range(longitud - len(password))
    )

    # Mezcla los caracteres de forma segura.
    secrets.SystemRandom().shuffle(password)

    return "".join(password)


class Command(BaseCommand):
    help = "Cambia el password de un listado de usuarios."

    def add_arguments(self, parser):
        parser.add_argument(
            "usuarios",
            nargs="+",
            type=str,
            help="Listado de usernames separados por espacios.",
        )

        parser.add_argument(
            "--longitud",
            type=int,
            default=14,
            help="Longitud del password generado. Valor predeterminado: 14.",
        )

    def handle(self, *args, **options):
        User = get_user_model()

        usernames = options["usuarios"]
        longitud = options["longitud"]

        resultados = []
        no_encontrados = []

        for username in usernames:
            try:
                usuario = User.objects.get(username=username)
            except User.DoesNotExist:
                no_encontrados.append(username)
                continue

            nuevo_password = generar_password(longitud)

            usuario.set_password(nuevo_password)
            usuario.save(update_fields=["password"])

            resultados.append({
                "usuario": username,
                "password": nuevo_password,
            })

        self.stdout.write("\nPasswords actualizados:\n")

        for resultado in resultados:
            self.stdout.write(
                f"Usuario: {resultado['usuario']} | "
                f"Password: {resultado['password']}"
            )

        if no_encontrados:
            self.stdout.write(
                self.style.WARNING("\nUsuarios no encontrados:")
            )

            for username in no_encontrados:
                self.stdout.write(f"- {username}")

        self.stdout.write(
            self.style.SUCCESS(
                f"\nTotal actualizados: {len(resultados)}"
            )
        )
