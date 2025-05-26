from django.db import models

# Create your models here.

class Seguimiento(models.Model):
    materia_curso = models.ForeignKey('materias.MateriaCurso', on_delete=models.CASCADE)
    trimestre = models.ForeignKey('cursos.Trimestre', on_delete=models.CASCADE)
    estudiante = models.ForeignKey('usuarios.Estudiante', on_delete=models.CASCADE)
    nota_trimestral = models.FloatField()

    class Meta:
        unique_together = ('materia_curso', 'trimestre', 'estudiante')

    def __str__(self):
        return f"{self.estudiante} - {self.materia_curso} - {self.trimestre}"

class Asistencia(models.Model):
    seguimiento = models.ForeignKey('seguimiento.Seguimiento', on_delete=models.CASCADE, related_name='asistencias')
    fecha = models.DateField()
    asistencia = models.BooleanField()

class Participacion(models.Model):
    seguimiento = models.ForeignKey('seguimiento.Seguimiento', on_delete=models.CASCADE, related_name='participaciones')
    fecha_participacion = models.DateField()
    nota_participacion = models.FloatField()

class Tarea(models.Model):
    seguimiento = models.ForeignKey('seguimiento.Seguimiento', on_delete=models.CASCADE, related_name='tareas')
    fecha = models.DateField()
    nota_tarea = models.FloatField()

class TipoExamen(models.Model):
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre

class Examen(models.Model):
    seguimiento = models.ForeignKey('seguimiento.Seguimiento', on_delete=models.CASCADE, related_name='examenes')
    tipo_examen = models.ForeignKey('seguimiento.TipoExamen', on_delete=models.SET_NULL, null=True)
    fecha = models.DateField()
    nota_examen = models.FloatField()
    matricula = models.ForeignKey('matricula.Matricula', on_delete=models.SET_NULL, null=True, blank=True, help_text="Matrícula que habilitó este examen")

    def __str__(self):
        return f"Examen {self.tipo_examen} - {self.seguimiento.estudiante} - {self.fecha}"
