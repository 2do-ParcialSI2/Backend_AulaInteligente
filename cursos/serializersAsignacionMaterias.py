from rest_framework import serializers
from cursos.models import Curso
from materias.models import Materia


class CursoMateriaAsignacionSerializer(serializers.ModelSerializer):
    materia_ids = serializers.PrimaryKeyRelatedField(
        queryset=Materia.objects.all(), many=True, write_only=True
    )

    class Meta:
        model = Curso
        fields = ["id", "nombre", "turno", "materia_ids"]

    def update(self, instance, validated_data):
        materias = validated_data.pop("materia_ids", [])
        instance.materias.set(materias)  # Reemplaza las materias anteriores
        return instance
