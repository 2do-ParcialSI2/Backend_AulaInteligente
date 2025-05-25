from django.db import models


class Curso(models.Model):
    TURNO_CHOICES = [
        ("mañana", "Mañana"),
        ("tarde", "Tarde"),
        ("noche", "Noche"),
    ]
    nombre = models.CharField(max_length=20, unique=True)  # Ej: "5to A", "3ro B"
    turno = models.CharField(max_length=10, choices=TURNO_CHOICES, default="mañana")
    materias = models.ManyToManyField(
        "materias.Materia", through="materias.MateriaCurso", related_name="cursos"
    )

    def __str__(self):
        return f"{self.nombre} ({self.turno})"
