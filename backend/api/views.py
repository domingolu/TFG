# Create your views here.
import uuid

from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from api.models import (
    Persona,
    TarjetaNFC,
    Edificio,
    Espacio,
    NodoAcceso,
    Permiso,
    Acceso,
    EventoMQTT,
)
from api.mqtt_bridge import MQTTBridge
from .serializers import (
    PersonaSerializer,
    TarjetaNFCSerializer,
    EdificioSerializer,
    EspacioSerializer,
    NodoAccesoSerializer,
    PermisoSerializer,
    AccesoSerializer,
    EventoMQTTSerializer,
    ComandoPuertaSerializer,
    EventoTarjetaSerializer,
)


class PersonaViewSet(viewsets.ModelViewSet):
    queryset = Persona.objects.all()
    serializer_class = PersonaSerializer


class TarjetaNFCViewSet(viewsets.ModelViewSet):
    queryset = TarjetaNFC.objects.select_related("persona").all()
    serializer_class = TarjetaNFCSerializer


class EdificioViewSet(viewsets.ModelViewSet):
    queryset = Edificio.objects.all()
    serializer_class = EdificioSerializer


class EspacioViewSet(viewsets.ModelViewSet):
    queryset = Espacio.objects.select_related("edificio").all()
    serializer_class = EspacioSerializer


class NodoAccesoViewSet(viewsets.ModelViewSet):
    queryset = NodoAcceso.objects.select_related("espacio", "espacio__edificio").all()
    serializer_class = NodoAccesoSerializer

    @action(detail=True, methods=["post"])
    def abrir(self, request, pk=None):
        return self._enviar_comando(request, pk, "ABRIR")

    @action(detail=True, methods=["post"])
    def cerrar(self, request, pk=None):
        return self._enviar_comando(request, pk, "CERRAR")

    @action(detail=True, methods=["post"])
    def evento_tarjeta(self, request, pk=None):
        nodo = self.get_object()
        serializer = EventoTarjetaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        bridge = MQTTBridge()
        request_id = serializer.validated_data.get("request_id") or str(uuid.uuid4())

        payload = {
            "evento": "tarjeta_leida",
            "persona_id": serializer.validated_data["persona_id"],
            "tarjeta_id": serializer.validated_data["tarjeta_id"],
            "dni": serializer.validated_data.get("dni"),
            "usuario": serializer.validated_data.get("usuario"),
            "numero_tarjeta": serializer.validated_data.get("numero_tarjeta"),
            "request_id": request_id,
        }

        bridge._handle_evento(nodo, payload)

        return Response(
            {"detail": "evento procesado", "nodo_id": nodo.id, "request_id": request_id},
            status=status.HTTP_202_ACCEPTED,
        )

    def _enviar_comando(self, request, pk, accion):
        nodo = get_object_or_404(NodoAcceso.objects.select_related("espacio"), pk=pk)

        serializer = ComandoPuertaSerializer(data={
            "accion": accion,
            "request_id": request.data.get("request_id", "")
        })
        serializer.is_valid(raise_exception=True)

        request_id = serializer.validated_data.get("request_id") or str(uuid.uuid4())

        bridge = MQTTBridge()
        bridge.publicar_comando(nodo.id, accion, request_id)

        if accion == "ABRIR":
            nodo.estado = NodoAcceso.Estado.PENDIENTE_ABRIR
        else:
            nodo.estado = NodoAcceso.Estado.PENDIENTE_CERRAR
        nodo.save(update_fields=["estado"])

        return Response({
            "detail": "comando enviado",
            "nodo_id": nodo.id,
            "accion": accion,
            "request_id": request_id,
            "estado_actual": nodo.estado,
        }, status=status.HTTP_202_ACCEPTED)


class PermisoViewSet(viewsets.ModelViewSet):
    queryset = Permiso.objects.select_related("persona", "espacio").all()
    serializer_class = PermisoSerializer


class AccesoViewSet(viewsets.ModelViewSet):
    queryset = Acceso.objects.select_related("persona", "espacio", "tarjeta", "nodo").all()
    serializer_class = AccesoSerializer


class EventoMQTTViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EventoMQTT.objects.select_related("nodo").all()
    serializer_class = EventoMQTTSerializer