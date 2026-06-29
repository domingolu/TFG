from django.contrib import admin

# Register your models here.
from .models import (
    Persona,
    TarjetaNFC,
    Edificio,
    Espacio,
    NodoAcceso,
    Permiso,
    Acceso
)


# admin.site.register(Persona)
@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "apellido", "dni", "usuario", "es_administrador")
    search_fields = ("nombre", "apellido", "dni", "usuario")
    list_filter = ("es_administrador",)


@admin.register(TarjetaNFC)
class TarjetaNFCAdmin(admin.ModelAdmin):
    list_display = ("numero_tarjeta", "persona", "activa", "fecha_emision")
    search_fields = ("numero_tarjeta", "persona__nombre", "persona__apellido")
    list_filter = ("activa",)


@admin.register(Edificio)
class EdificioAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "direccion")
    search_fields = ("nombre", "direccion")


@admin.register(Espacio)
class EspacioAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "codigo", "tipo", "edificio")
    search_fields = ("nombre", "codigo")
    list_filter = ("tipo", "edificio")


@admin.register(NodoAcceso)
class NodoAccesoAdmin(admin.ModelAdmin):
    list_display = (
        "numero_serie",
        "espacio",
        "estado",
        "activo",
        "fecha_instalacion"
    )
    search_fields = ("numero_serie",)
    list_filter = ("estado", "activo")


@admin.register(Permiso)
class PermisoAdmin(admin.ModelAdmin):
    list_display = (
        "persona",
        "espacio",
        "dias_permitidos",
        "horario_inicio",
        "horario_fin",
        "activo"
    )
    list_filter = ("activo",)


@admin.register(Acceso)
class AccesoAdmin(admin.ModelAdmin):
    list_display = (
        "persona",
        "espacio",
        "tarjeta",
        "nodo",
        "accion",
        "estado_puerta",
        "fecha_hora"
    )
    list_filter = ("accion", "estado_puerta")
    search_fields = (
        "persona__nombre",
        "persona__apellido",
        "tarjeta__numero_tarjeta"
    )