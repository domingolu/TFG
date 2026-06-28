# lógica reutilizable
import json
import logging
import uuid

import paho.mqtt.client as mqtt

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from api.models import NodoAcceso, EventoMQTT, Acceso, Permiso, Persona, TarjetaNFC

logger = logging.getLogger(__name__)


class MQTTBridge:
    def __init__(self):
        self.client = mqtt.Client(client_id=settings.MQTT_CLIENT_ID)

        if settings.MQTT_USERNAME:
            self.client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

    def connect(self):
        self.client.connect(settings.MQTT_HOST, settings.MQTT_PORT, 60)
        self.client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("MQTT conectado correctamente")
            client.subscribe(f"{settings.MQTT_TOPIC_BASE}/+/estado", qos=1)
            client.subscribe(f"{settings.MQTT_TOPIC_BASE}/+/telemetria", qos=1)
            client.subscribe(f"{settings.MQTT_TOPIC_BASE}/+/ack", qos=1)
            client.subscribe(f"{settings.MQTT_TOPIC_BASE}/+/evento", qos=1)
        else:
            logger.error("Fallo de conexión MQTT rc=%s", rc)

    def on_disconnect(self, client, userdata, rc):
        logger.warning("MQTT desconectado rc=%s", rc)

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
        except json.JSONDecodeError:
            logger.exception("Payload inválido en %s", topic)
            return

        nodo = self._get_nodo_from_topic(topic)
        if not nodo:
            return

        self._register_event(nodo, topic, payload)

        if topic.endswith("/estado"):
            self._handle_estado(nodo, payload)
        elif topic.endswith("/ack"):
            self._handle_ack(nodo, payload)
        elif topic.endswith("/telemetria"):
            self._handle_telemetria(nodo, payload)
        elif topic.endswith("/evento"):
            self._handle_evento(nodo, payload)

    def _register_event(self, nodo, topic, payload):
        EventoMQTT.objects.create(nodo=nodo, topic=topic, payload=payload)

    def _get_nodo_from_topic(self, topic):
        parts = topic.split("/")
        if len(parts) < 3:
            return None

        try:
            nodo_id = int(parts[1])
            return NodoAcceso.objects.select_related("espacio", "espacio__edificio").get(id=nodo_id)
        except (ValueError, NodoAcceso.DoesNotExist):
            logger.warning("Nodo no encontrado para topic %s", topic)
            return None

    @transaction.atomic
    def _handle_estado(self, nodo, payload):
        estado = payload.get("estado")
        if estado:
            nodo.estado = estado
            nodo.last_seen = timezone.now()
            nodo.save(update_fields=["estado", "last_seen"])

    @transaction.atomic
    def _handle_telemetria(self, nodo, payload):
        nodo.last_seen = timezone.now()
        nodo.save(update_fields=["last_seen"])

    @transaction.atomic
    def _handle_ack(self, nodo, payload):
        request_id = payload.get("request_id")
        status = payload.get("status", "unknown")
        accion = payload.get("accion")
        estado_puerta = payload.get("estado_puerta", nodo.estado)

        logger.info(
            "ACK recibido nodo=%s request_id=%s status=%s accion=%s",
            nodo.id,
            request_id,
            status,
            accion,
        )

        if status not in ("ok", "success", "accepted"):
            return

        persona = self._resolve_persona(payload)
        tarjeta = self._resolve_tarjeta(payload)

        if not persona or not tarjeta:
            logger.warning("No se pudo resolver persona/tarjeta para registrar acceso")
            return

        if not self.validar_permiso(persona, nodo.espacio):
            logger.warning(
                "Acceso denegado por permisos: persona=%s espacio=%s",
                persona.id,
                nodo.espacio.id,
            )
            self.registrar_acceso(
                persona=persona,
                espacio=nodo.espacio,
                tarjeta=tarjeta,
                nodo=nodo,
                accion=accion or "ABRIR",
                estado_puerta="DENEGADA",
            )
            return

        self.registrar_acceso(
            persona=persona,
            espacio=nodo.espacio,
            tarjeta=tarjeta,
            nodo=nodo,
            accion=accion or "ABRIR",
            estado_puerta=estado_puerta,
        )

        if estado_puerta in ("ABIERTA", "CERRADA", "FORZADA"):
            nodo.estado = estado_puerta
            nodo.last_seen = timezone.now()
            nodo.save(update_fields=["estado", "last_seen"])

    def _handle_evento(self, nodo, payload):
        evento = payload.get("evento")

        if evento == "tarjeta_leida":
            persona = self._resolve_persona(payload)
            tarjeta = self._resolve_tarjeta(payload)

            if not persona or not tarjeta:
                logger.warning("No se pudo resolver persona/tarjeta en evento tarjeta_leida")
                return

            if self.validar_permiso(persona, nodo.espacio):
                request_id = payload.get("request_id") or str(uuid.uuid4())
                self.publicar_comando(nodo.id, "ABRIR", request_id=request_id)
                nodo.estado = NodoAcceso.Estado.PENDIENTE_ABRIR
                nodo.save(update_fields=["estado"])
            else:
                self.registrar_acceso(
                    persona=persona,
                    espacio=nodo.espacio,
                    tarjeta=tarjeta,
                    nodo=nodo,
                    accion="ABRIR",
                    estado_puerta="DENEGADA",
                )

    def _resolve_persona(self, payload):
        persona_id = payload.get("persona_id")
        dni = payload.get("dni")
        usuario = payload.get("usuario")

        qs = Persona.objects.all()

        if persona_id is not None:
            return qs.filter(id=persona_id).first()
        if dni:
            return qs.filter(dni=dni).first()
        if usuario:
            return qs.filter(usuario=usuario).first()
        return None

    def _resolve_tarjeta(self, payload):
        tarjeta_id = payload.get("tarjeta_id")
        numero_tarjeta = payload.get("numero_tarjeta")

        qs = TarjetaNFC.objects.select_related("persona")

        if tarjeta_id is not None:
            return qs.filter(id=tarjeta_id).first()
        if numero_tarjeta:
            return qs.filter(numero_tarjeta=numero_tarjeta).first()
        return None

    def validar_permiso(self, persona, espacio):
        now = timezone.localtime()
        weekday = now.strftime("%A").upper()

        permisos = Permiso.objects.filter(
            persona=persona,
            espacio=espacio,
            activo=True,
        )

        for permiso in permisos:
            dias = [d.strip().upper() for d in permiso.dias_permitidos.split(",")]
            if weekday in dias and permiso.horario_inicio <= now.time() <= permiso.horario_fin:
                return True
        return False

    def registrar_acceso(self, persona, espacio, tarjeta, nodo, accion, estado_puerta):
        return Acceso.objects.create(
            persona=persona,
            espacio=espacio,
            tarjeta=tarjeta,
            nodo=nodo,
            accion=accion,
            estado_puerta=estado_puerta,
        )

    def publicar_comando(self, nodo_id, accion, request_id=None):
        request_id = request_id or str(uuid.uuid4())
        topic = f"{settings.MQTT_TOPIC_BASE}/{nodo_id}/comando"
        payload = {
            "accion": accion,
            "request_id": request_id,
            "ts": timezone.now().isoformat(),
        }
        self.client.publish(topic, json.dumps(payload), qos=1, retain=False)
        return request_id