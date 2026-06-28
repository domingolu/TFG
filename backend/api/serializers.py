from rest_framework import serializers
from .models import (
    Persona,
    TarjetaNFC,
    Edificio,
    Espacio,
    NodoAcceso,
    Permiso,
    Acceso,
    EventoMQTT
)


class PersonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Persona
        fields = "__all__"
        extra_kwargs = {
            "contraseña": {"write_only": True}
        }

    def create(self, validated_data):
        persona = Persona(**validated_data)
        persona.save()
        return persona


class TarjetaNFCSerializer(serializers.ModelSerializer):
    class Meta:
        model = TarjetaNFC
        fields = "__all__"


class EdificioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Edificio
        fields = "__all__"


class EspacioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Espacio
        fields = "__all__"


class NodoAccesoSerializer(serializers.ModelSerializer):
    class Meta:
        model = NodoAcceso
        fields = "__all__"


class PermisoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permiso
        fields = "__all__"


class AccesoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Acceso
        fields = "__all__"


class EventoMQTTSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventoMQTT
        fields = "__all__"


class ComandoPuertaSerializer(serializers.Serializer):
    accion = serializers.ChoiceField(choices=["ABRIR", "CERRAR"])
    request_id = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        accion = attrs["accion"]
        if accion not in ["ABRIR", "CERRAR"]:
            raise serializers.ValidationError("Acción inválida.")
        return attrs
    

class EventoTarjetaSerializer(serializers.Serializer):
    persona_id = serializers.IntegerField()
    tarjeta_id = serializers.IntegerField()
    dni = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    usuario = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    numero_tarjeta = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    request_id = serializers.CharField(required=False, allow_blank=True)