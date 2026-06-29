# Create your models here.

from django.db import models
from django.contrib.auth.hashers import make_password

class Persona(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    dni = models.CharField(max_length=20, unique=True)
    es_administrador = models.BooleanField(default=False)
    usuario = models.CharField(max_length=50, unique=True)
    contraseña = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        if self.contraseña and not self.contraseña.startswith("pbkdf2_"):
            self.contraseña = make_password(self.contraseña)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.apellido}, {self.nombre}"



class TarjetaNFC(models.Model):
    numero_tarjeta = models.CharField(max_length=50, unique=True)
    persona = models.OneToOneField(Persona, on_delete=models.CASCADE, related_name="tarjeta_nfc")
    activa = models.BooleanField(default=True)
    fecha_emision = models.DateField(null=True, blank=True)
    fecha_inactivacion = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.apellido}, {self.nombre}"


class Edificio(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)

    def __str__(self):
        return self.nombre
    

class Espacio(models.Model):
    class Tipo(models.TextChoices):
        AULA = "AULA", "Aula"
        OFICINA = "OFICINA", "Oficina"

    edificio = models.ForeignKey(Edificio, on_delete=models.CASCADE, related_name="espacios")
    tipo = models.CharField(max_length=20, choices=Tipo.choices)
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.codigo
    

class NodoAcceso(models.Model):
    class Estado(models.TextChoices):
        ABIERTA = "ABIERTA", "Abierta"
        PENDIENTE_ABRIR = "PENDIENTE_ABRIR", "Pendiente abrir"
        CERRADA = "CERRADA", "Cerrada"
        PENDIENTE_CERRAR = "PENDIENTE_CERRAR", "Pendiente cerrar"
        FORZADA = "FORZADA", "Forzada"

    espacio = models.OneToOneField(Espacio, on_delete=models.CASCADE, related_name="nodo_acceso")
    numero_serie = models.CharField(max_length=100, unique=True)
    #estado = models.CharField(max_length=30, choices=Estado.choices)
    estado = models.CharField(max_length=30, choices=Estado.choices, default=Estado.CERRADA)
    fecha_instalacion = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    last_seen = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.numero_serie
    

class Permiso(models.Model):
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name="permisos")
    espacio = models.ForeignKey(Espacio, on_delete=models.CASCADE, related_name="permisos")
    dias_permitidos = models.CharField(max_length=50)
    horario_inicio = models.TimeField()
    horario_fin = models.TimeField()
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.persona_id} -> {self.espacio_id}"
    

class Acceso(models.Model):
    class Accion(models.TextChoices):
        ABRIR = "ABRIR", "Abrir"
        CERRAR = "CERRAR", "Cerrar"

    persona = models.ForeignKey(Persona, on_delete=models.PROTECT, related_name="accesos")
    espacio = models.ForeignKey(Espacio, on_delete=models.PROTECT, related_name="accesos")
    tarjeta = models.ForeignKey(TarjetaNFC, on_delete=models.PROTECT, related_name="accesos")
    nodo = models.ForeignKey(NodoAcceso, on_delete=models.PROTECT, related_name="accesos")
    estado_puerta = models.CharField(max_length=30, choices=NodoAcceso.Estado.choices)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    accion = models.CharField(max_length=10, choices=Accion.choices)
    request_id = models.CharField(max_length=80, null=True, blank=True)
    autorizado = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.persona_id} - {self.accion} - {self.fecha_hora}"


class EventoMQTT(models.Model):
    nodo = models.ForeignKey(NodoAcceso, on_delete=models.CASCADE, related_name="eventos_mqtt")
    topic = models.CharField(max_length=255)
    payload = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.topic