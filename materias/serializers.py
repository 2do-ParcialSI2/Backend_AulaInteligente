from rest_framework import serializers
from materias.models import Materia


class MateriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Materia
        fields = ["id", "nombre", "descripcion"]
