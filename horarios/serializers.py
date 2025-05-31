from rest_framework import serializers
from .models import Horario


class HorarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Horario
        fields = "__all__"

    def validate(self, data):
        """
        Validar que hora_inicio sea menor que hora_fin
        """
        hora_inicio = data['hora_inicio']
        hora_fin = data['hora_fin']
        

        # Validar que hora_inicio sea menor que hora_fin
        if hora_inicio >= hora_fin:
            raise serializers.ValidationError("La hora de inicio debe ser menor que la hora de fin")

        return data
