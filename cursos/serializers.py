from rest_framework import serializers
from .models import Curso, Trimestre


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


class TrimestreSerializer(serializers.ModelSerializer):
    duracion_dias = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Trimestre
        fields = ['id', 'nombre', 'fecha_inicio', 'fecha_fin', 'duracion_dias']
        
    def validate(self, data):
        """Validar que la fecha de inicio sea anterior a la fecha de fin"""
        if data['fecha_inicio'] >= data['fecha_fin']:
            raise serializers.ValidationError(
                "La fecha de inicio debe ser anterior a la fecha de fin"
            )
        return data


class TrimestreCreateSerializer(serializers.ModelSerializer):
    """Serializer simplificado para crear trimestres"""
    
    class Meta:
        model = Trimestre
        fields = ['nombre', 'fecha_inicio', 'fecha_fin']
        
    def validate(self, data):
        """Validar que la fecha de inicio sea anterior a la fecha de fin"""
        if data['fecha_inicio'] >= data['fecha_fin']:
            raise serializers.ValidationError(
                "La fecha de inicio debe ser anterior a la fecha de fin"
            )
        return data
