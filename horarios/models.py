from django.db import models


class Horario(models.Model):

    DIAS_SEMANA = [
        ("Lunes", "Lunes"),
        ("Martes", "Martes"),
        ("Miércoles", "Miércoles"),
        ("Jueves", "Jueves"),
        ("Viernes", "Viernes"),
        ("Sábado", "Sábado"),
    ]
    
    nombre = models.CharField(
        max_length=100, 
        default="Horario sin nombre",
        help_text="Ej: 'Primera hora mañana', 'Bloque tarde'"
    )
    dia_semana = models.CharField(max_length=10, choices=DIAS_SEMANA)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    activo = models.BooleanField(default=True)

    class Meta:
        unique_together = ("dia_semana", "hora_inicio", "hora_fin")  # Evita horarios duplicados
        verbose_name = "Horario"
        verbose_name_plural = "Horarios"
        ordering = ["dia_semana", "hora_inicio"]

    def __str__(self):
        return f"{self.nombre} - {self.dia_semana} {self.hora_inicio.strftime('%H:%M')} a {self.hora_fin.strftime('%H:%M')}"
