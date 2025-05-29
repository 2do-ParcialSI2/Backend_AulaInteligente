from rest_framework import serializers
from .models import Curso


class CursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curso
        fields = ("id", "nombre", "turno")


# to_representation para evitar importación circular.
class CursoConEstudiantesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curso
        fields = ["id", "nombre", "turno", "estudiantes"]

    def to_representation(self, instance):
        # Este método sobrescribe la representación por defecto, personaliza cómo se devuelve la información de los cursos, incluyendo los estudiantes asociados sin provocar un import circular.
        from usuarios.serializers import (
            EstudianteSimpleSerializer,
        )  # Importamos aquí dentro para evitar errores de importación circular

        rep = super().to_representation(instance)

        # Añadimos una lista de estudiantes usando el serializer reducido
        rep["estudiantes"] = EstudianteSimpleSerializer(
            instance.estudiantes.all(),  # Consulta todos los estudiantes del curso
            many=True,  # Indica que es una lista
        ).data

        return rep
