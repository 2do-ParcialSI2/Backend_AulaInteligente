from rest_framework import serializers
from .models import Seguimiento, Asistencia, Participacion, Tarea, Examen, TipoExamen
from matricula.models import Matricula

class SeguimientoSerializer(serializers.ModelSerializer):
    resumen_nota = serializers.SerializerMethodField()
    total_asistencias = serializers.SerializerMethodField()
    total_tareas = serializers.SerializerMethodField()
    total_participaciones = serializers.SerializerMethodField()
    total_examenes = serializers.SerializerMethodField()
    
    class Meta:
        model = Seguimiento
        fields = ['id', 'materia_curso', 'trimestre', 'estudiante', 'nota_trimestral', 
                 'resumen_nota', 'total_asistencias', 'total_tareas', 'total_participaciones', 'total_examenes']

    def get_resumen_nota(self, obj):
        return f"{obj.nota_trimestral} / 100"
    
    def get_total_asistencias(self, obj):
        return obj.asistencias.count()
    
    def get_total_tareas(self, obj):
        return obj.tareas.count()
    
    def get_total_participaciones(self, obj):
        return obj.participaciones.count()
    
    def get_total_examenes(self, obj):
        return obj.examenes.count()

class SeguimientoDetalladoSerializer(serializers.ModelSerializer):
    """Serializer expandido con información detallada"""
    estudiante_nombre = serializers.CharField(source='estudiante.usuario.first_name', read_only=True)
    estudiante_apellido = serializers.CharField(source='estudiante.usuario.last_name', read_only=True)
    materia_nombre = serializers.CharField(source='materia_curso.materia.nombre', read_only=True)
    curso_nombre = serializers.CharField(source='materia_curso.curso.nombre', read_only=True)
    trimestre_nombre = serializers.CharField(source='trimestre.nombre', read_only=True)
    docente_nombre = serializers.CharField(source='materia_curso.docente.usuario.first_name', read_only=True)
    docente_apellido = serializers.CharField(source='materia_curso.docente.usuario.last_name', read_only=True)
    
    class Meta:
        model = Seguimiento
        fields = ['id', 'nota_trimestral', 'estudiante_nombre', 'estudiante_apellido',
                 'materia_nombre', 'curso_nombre', 'trimestre_nombre', 'docente_nombre', 'docente_apellido']

class AsistenciaSerializer(serializers.ModelSerializer):
    estudiante_nombre = serializers.CharField(source='seguimiento.estudiante.usuario.first_name', read_only=True)
    
    class Meta:
        model = Asistencia
        fields = ['id', 'seguimiento', 'fecha', 'asistencia', 'estudiante_nombre']
        
    def validate_fecha(self, value):
        """Validar que la fecha no sea futura"""
        from datetime import date
        if value > date.today():
            raise serializers.ValidationError("No se puede registrar asistencia para fechas futuras")
        return value

class ParticipacionSerializer(serializers.ModelSerializer):
    estudiante_nombre = serializers.CharField(source='seguimiento.estudiante.usuario.first_name', read_only=True)
    
    class Meta:
        model = Participacion
        fields = ['id', 'seguimiento', 'fecha_participacion', 'nota_participacion', 'descripcion', 'estudiante_nombre']

class TareaSerializer(serializers.ModelSerializer):
    estudiante_nombre = serializers.CharField(source='seguimiento.estudiante.usuario.first_name', read_only=True)
    
    class Meta:
        model = Tarea
        fields = ['id', 'seguimiento', 'fecha', 'nota_tarea', 'titulo', 'descripcion', 'estudiante_nombre']

class TipoExamenSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoExamen
        fields = ['id', 'nombre', 'descripcion']

class ExamenSerializer(serializers.ModelSerializer):
    estudiante_nombre = serializers.CharField(source='seguimiento.estudiante.usuario.first_name', read_only=True)
    tipo_examen_nombre = serializers.CharField(source='tipo_examen.nombre', read_only=True)
    
    class Meta:
        model = Examen
        fields = ['id', 'seguimiento', 'tipo_examen', 'tipo_examen_nombre', 'fecha', 'nota_examen', 
                 'matricula', 'observaciones', 'estudiante_nombre']
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