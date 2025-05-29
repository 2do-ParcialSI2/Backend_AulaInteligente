from django.db import models
from materias.models import MateriaCurso


class Horario(models.Model):

    DIAS_SEMANA = [
        ("Lunes", "Lunes"),
        ("Martes", "Martes"),
        ("Miércoles", "Miércoles"),
        ("Jueves", "Jueves"),
        ("Viernes", "Viernes"),
        ("Sábado", "Sábado"),
    ]
    materia_curso = models.ForeignKey(
        MateriaCurso, on_delete=models.CASCADE, related_name="horarios"
    )
    dia_semana = models.CharField(max_length=10, choices=DIAS_SEMANA)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    def __str__(self):
        return f"{self.materia_curso} - {self.dia_semana} {self.hora_inicio.strftime('%H:%M')} a {self.hora_fin.strftime('%H:%M')}"
