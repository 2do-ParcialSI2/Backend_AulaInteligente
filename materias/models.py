from django.db import models
from usuarios.models import Docente


class Materia(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class MateriaCurso(models.Model):
    curso = models.ForeignKey("cursos.Curso", on_delete=models.CASCADE)
    materia = models.ForeignKey("materias.Materia", on_delete=models.CASCADE)
    docente = models.ForeignKey(
        Docente, 
        on_delete=models.CASCADE, 
        related_name="materias_asignadas",
        null=True,  # Hacer opcional
        blank=True  # Permitir campo vacío en formularios
    )
    horarios = models.ManyToManyField(
        "horarios.Horario", 
        blank=True, 
        related_name="materia_cursos",
        help_text="Horarios asignados a esta materia en este curso"
    )
    activo = models.BooleanField(default=True)

    class Meta:
        unique_together = ("curso", "materia")  # evita duplicados
        verbose_name = "Materia por curso"
        verbose_name_plural = "Materias por curso"

    def __str__(self):
        return f"{self.materia.nombre} en {self.curso.nombre}"
