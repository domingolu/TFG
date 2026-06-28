from django.db import models

# Create your models here.

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

class TarjetaNFC(models.Model):
    numero_tarjeta = models.CharField(max_length=50, unique=True)
    persona = models.OneToOneField(Persona, on_delete=models.CASCADE, related_name="tarjeta_nfc")
    activa = models.BooleanField(default=True)
    fecha_emision = models.DateField(null=True, blank=True)
    fecha_inactivacion = models.DateField(null=True, blank=True)

class Edificio(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)

class Espacio(models.Model):
    class Tipo(models.TextChoices):
        AULA = "AULA", "Aula"
        OFICINA = "OFICINA", "Oficina"

    edificio = models.ForeignKey(Edificio, on_delete=models.CASCADE, related_name="espacios")
    tipo = models.CharField(max_length=20, choices=Tipo.choices)
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=50, unique=True)

class NodoAcceso(models.Model):
    class Estado(models.TextChoices):
        ABIERTA = "ABIERTA", "Abierta"
        PENDIENTE_ABRIR = "PENDIENTE_ABRIR", "Pendiente abrir"
        CERRADA = "CERRADA", "Cerrada"
        PENDIENTE_CERRAR = "PENDIENTE_CERRAR", "Pendiente cerrar"
        FORZADA = "FORZADA", "Forzada"

    espacio = models.OneToOneField(Espacio, on_delete=models.CASCADE, related_name="nodo_acceso")
    numero_serie = models.CharField(max_length=100, unique=True)
    estado = models.CharField(max_length=30, choices=Estado.choices)
    fecha_instalacion = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=True)

class Permiso(models.Model):
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name="permisos")
    espacio = models.ForeignKey(Espacio, on_delete=models.CASCADE, related_name="permisos")
    dias_permitidos = models.CharField(max_length=50)
    horario_inicio = models.TimeField()
    horario_fin = models.TimeField()
    activo = models.BooleanField(default=True)

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