from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class Seguimiento(models.Model):
    materia_curso = models.ForeignKey('materias.MateriaCurso', on_delete=models.CASCADE)
    trimestre = models.ForeignKey('cursos.Trimestre', on_delete=models.CASCADE)
    estudiante = models.ForeignKey('usuarios.Estudiante', on_delete=models.CASCADE)
    nota_trimestral = models.FloatField(
        default=0.0, 
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )

    class Meta:
        unique_together = ('materia_curso', 'trimestre', 'estudiante')
        verbose_name = "Seguimiento"
        verbose_name_plural = "Seguimientos"

    def __str__(self):
        return f"{self.estudiante} - {self.materia_curso} - {self.trimestre}"
    
    def calcular_nota_trimestral(self):
        """Calcular la nota trimestral basada en tareas, participaciones, exámenes y asistencia"""
        # Promedio de tareas
        tareas = self.tareas.all()
        prom_tareas = sum(t.nota_tarea for t in tareas) / len(tareas) if tareas else 0

        # Promedio de participaciones
        participaciones = self.participaciones.all()
        prom_part = sum(p.nota_participacion for p in participaciones) / len(participaciones) if participaciones else 0

        # Promedio de exámenes
        examenes = self.examenes.all()
        prom_examenes = sum(e.nota_examen for e in examenes) / len(examenes) if examenes else 0

        # Porcentaje de asistencia
        asistencias = self.asistencias.all()
        porcentaje_asistencia = (
            sum(1 for a in asistencias if a.asistencia) / len(asistencias) * 100
            if asistencias else 0
        )

        # Fórmula personalizada (puedes modificar los pesos)
        nota_final = (
            prom_tareas * 0.25 +
            prom_part * 0.15 +
            prom_examenes * 0.50 +
            (porcentaje_asistencia / 100) * 0.10
        )

        self.nota_trimestral = round(nota_final, 2)
        self.save()
        return self.nota_trimestral


class Asistencia(models.Model):
    seguimiento = models.ForeignKey('seguimiento.Seguimiento', on_delete=models.CASCADE, related_name='asistencias')
    fecha = models.DateField()
    asistencia = models.BooleanField(default=False)

    class Meta:
        unique_together = ('seguimiento', 'fecha')
        verbose_name = "Asistencia"
        verbose_name_plural = "Asistencias"

    def __str__(self):
        estado = "Presente" if self.asistencia else "Ausente"
        return f"{self.seguimiento.estudiante} - {self.fecha} - {estado}"


class Participacion(models.Model):
    seguimiento = models.ForeignKey('seguimiento.Seguimiento', on_delete=models.CASCADE, related_name='participaciones')
    fecha_participacion = models.DateField()
    nota_participacion = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    descripcion = models.TextField(blank=True, null=True, help_text="Descripción de la participación")

    class Meta:
        verbose_name = "Participación"
        verbose_name_plural = "Participaciones"

    def __str__(self):
        return f"{self.seguimiento.estudiante} - {self.fecha_participacion} - {self.nota_participacion}"


class Tarea(models.Model):
    seguimiento = models.ForeignKey('seguimiento.Seguimiento', on_delete=models.CASCADE, related_name='tareas')
    fecha = models.DateField()
    nota_tarea = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    titulo = models.CharField(max_length=200, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Tarea"
        verbose_name_plural = "Tareas"

    def __str__(self):
        return f"{self.seguimiento.estudiante} - {self.titulo or 'Tarea'} - {self.nota_tarea}"


class TipoExamen(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Tipo de Examen"
        verbose_name_plural = "Tipos de Examen"

    def __str__(self):
        return self.nombre


class Examen(models.Model):
    seguimiento = models.ForeignKey('seguimiento.Seguimiento', on_delete=models.CASCADE, related_name='examenes')
    tipo_examen = models.ForeignKey('seguimiento.TipoExamen', on_delete=models.SET_NULL, null=True)
    fecha = models.DateField()
    nota_examen = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    matricula = models.ForeignKey('matricula.Matricula', on_delete=models.SET_NULL, null=True, blank=True, help_text="Matrícula que habilitó este examen")
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Examen"
        verbose_name_plural = "Exámenes"

    def __str__(self):
        return f"Examen {self.tipo_examen} - {self.seguimiento.estudiante} - {self.fecha}"
