# from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets

from .models import (
    Persona,
    TarjetaNFC,
    Edificio,
    Espacio,
    NodoAcceso,
    Permiso,
    Acceso
)

from .serializers import (
    PersonaSerializer,
    TarjetaNFCSerializer,
    EdificioSerializer,
    EspacioSerializer,
    NodoAccesoSerializer,
    PermisoSerializer,
    AccesoSerializer
)


class PersonaViewSet(viewsets.ModelViewSet):
    queryset = Persona.objects.all()
    serializer_class = PersonaSerializer


class TarjetaNFCViewSet(viewsets.ModelViewSet):
    queryset = TarjetaNFC.objects.all()
    serializer_class = TarjetaNFCSerializer


class EdificioViewSet(viewsets.ModelViewSet):
    queryset = Edificio.objects.all()
    serializer_class = EdificioSerializer


class EspacioViewSet(viewsets.ModelViewSet):
    queryset = Espacio.objects.all()
    serializer_class = EspacioSerializer


class NodoAccesoViewSet(viewsets.ModelViewSet):
    queryset = NodoAcceso.objects.all()
    serializer_class = NodoAccesoSerializer


class PermisoViewSet(viewsets.ModelViewSet):
    queryset = Permiso.objects.all()
    serializer_class = PermisoSerializer


class AccesoViewSet(viewsets.ModelViewSet):
    queryset = Acceso.objects.all()
    serializer_class = AccesoSerializer