#punto de entrada de python manage.py mqtt_bridge

from django.core.management.base import BaseCommand
from api.mqtt_bridge import MQTTBridge

class Command(BaseCommand):
    help = "Ejecuta el bridge MQTT para el backend de api (accesos)"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Iniciando MQTT bridge..."))
        bridge = MQTTBridge()
        bridge.connect()