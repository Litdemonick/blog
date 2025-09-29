from django.core.management.base import BaseCommand
from django.core import management

class Command(BaseCommand):
    help = "Carga backup.json en la base de datos (solo manual)."

    def handle(self, *args, **options):
        self.stdout.write("Cargando backup.json...")
        management.call_command("loaddata", "backup.json")
        self.stdout.write(self.style.SUCCESS("Backup cargado con éxito"))
