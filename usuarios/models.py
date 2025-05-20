from django.db import models
from django.contrib.auth.models import AbstractUser

class Permiso(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

class Rol(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    permisos = models.ManyToManyField(Permiso, blank=True)

    def __str__(self):
        return self.nombre

class Usuario(AbstractUser):
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    ]
    username = None  # Deshabilitamos el campo username
    email = models.EmailField(unique=True)  # Usamos el campo email existente
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES, null=True, blank=True)
    activo = models.BooleanField(default=True)
    roles = models.ManyToManyField(Rol, blank=True)

    USERNAME_FIELD = 'email'  # Usamos email como campo principal
    REQUIRED_FIELDS = []  # No necesitamos campos adicionales requeridos

    def __str__(self):
        return self.email

class Estudiante(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='estudiante')
    direccion = models.CharField(max_length=255, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)

class Docente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='docente')
    especialidad = models.CharField(max_length=100, blank=True)

class PadreTutor(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='padretutor')
    parentesco = models.CharField(max_length=100, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
