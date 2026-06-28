from rest_framework import serializers
from .models import (
    Persona,
    TarjetaNFC,
    Edificio,
    Espacio,
    NodoAcceso,
    Permiso,
    Acceso
)


class PersonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Persona
        fields = "__all__"
        extra_kwargs = {
            "contraseña": {"write_only": True}
        }


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