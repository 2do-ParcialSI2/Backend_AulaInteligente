from rest_framework import serializers
from cursos.models import Curso
from materias.serializers import MateriaSerializer


class CursoConMateriasSerializer(serializers.ModelSerializer):
    materias = MateriaSerializer(many=True, read_only=True)

    class Meta:
        model = Curso
        fields = ["id", "nombre", "turno", "materias"]
