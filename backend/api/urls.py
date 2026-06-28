from django.urls import include, path
from api import views

from rest_framework.routers import DefaultRouter
from .views import (
    PersonaViewSet,
    TarjetaNFCViewSet,
    EdificioViewSet,
    EspacioViewSet,
    NodoAccesoViewSet,
    PermisoViewSet,
    AccesoViewSet
)

router = DefaultRouter()

router.register(r'personas', PersonaViewSet)
router.register(r'tarjetas', TarjetaNFCViewSet)
router.register(r'edificios', EdificioViewSet)
router.register(r'espacios', EspacioViewSet)
router.register(r'nodos', NodoAccesoViewSet)
router.register(r'permisos', PermisoViewSet)
router.register(r'accesos', AccesoViewSet)

urlpatterns = router.urls