from rest_framework import serializers
from .models import Seguimiento, Asistencia, Participacion, Tarea, Examen, TipoExamen
from matricula.models import Matricula

class SeguimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seguimiento
        fields = '__all__'

class AsistenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asistencia
        fields = '__all__'

class ParticipacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participacion
        fields = '__all__'

class TareaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tarea
        fields = '__all__'

class ExamenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Examen
        fields = '__all__'
        read_only_fields = ('matricula',)  # La matrícula se asigna automáticamente

    def validate(self, data):
        """
        Validar si el estudiante puede rendir el examen según su matrícula
        """
        seguimiento = data.get('seguimiento')
        fecha_examen = data.get('fecha')
        
        if seguimiento and fecha_examen:
            estudiante = seguimiento.estudiante
            puede_rendir, resultado = Matricula.estudiante_puede_rendir_examen(estudiante, fecha_examen)
            
            if not puede_rendir:
                raise serializers.ValidationError(f"El estudiante no puede rendir el examen: {resultado}")
                
            # Si puede rendir, guardamos la matrícula que lo habilitó
            if isinstance(resultado, Matricula):
                data['matricula'] = resultado
                
        return data

class TipoExamenSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoExamen
        fields = '__all__' 