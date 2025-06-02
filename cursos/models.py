from django.db import models
from django.utils import timezone
from datetime import date


class Curso(models.Model):
    TURNO_CHOICES = [
        ("mañana", "Mañana"),
        ("tarde", "Tarde"),
        ("noche", "Noche"),
    ]
    nombre = models.CharField(max_length=20)  # Ej: "5to A", "3ro B"
    turno = models.CharField(max_length=10, choices=TURNO_CHOICES, default="mañana")
    materias = models.ManyToManyField("materias.Materia", through="materias.MateriaCurso", related_name="cursos")
    activo = models.BooleanField(default=True)

    class Meta:
        unique_together = ("nombre", "turno")  # Permite mismo nombre en diferentes turnos
        verbose_name = "Curso"
        verbose_name_plural = "Cursos"

    def __str__(self):
        return f"{self.nombre} ({self.turno})"


class Trimestre(models.Model):
    nombre = models.CharField(max_length=50)  # Ej: "Primer Trimestre 2025", "Segundo Trimestre 2025"
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()

    class Meta:
        ordering = ['fecha_inicio']
        verbose_name = "Trimestre"
        verbose_name_plural = "Trimestres"

    def __str__(self):
        return f"{self.nombre}"
    
    @property
    def duracion_dias(self):
        """Calcular la duración del trimestre en días"""
        return (self.fecha_fin - self.fecha_inicio).days + 1
    
    def clean(self):
        """Validación a nivel de modelo"""
        from django.core.exceptions import ValidationError
        if self.fecha_inicio >= self.fecha_fin:
            raise ValidationError("La fecha de inicio debe ser anterior a la fecha de fin")
