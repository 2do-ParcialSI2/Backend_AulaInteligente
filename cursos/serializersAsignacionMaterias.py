from rest_framework import serializers
from django.db import transaction
from cursos.models import Curso
from materias.models import Materia, MateriaCurso
from usuarios.models import Docente
from horarios.models import Horario


class MateriaConDocenteYHorariosSerializer(serializers.Serializer):
    materia_id = serializers.PrimaryKeyRelatedField(queryset=Materia.objects.all())
    docente_id = serializers.PrimaryKeyRelatedField(queryset=Docente.objects.all())
    horarios_ids = serializers.PrimaryKeyRelatedField(
        queryset=Horario.objects.all(), 
        many=True, 
        required=False, 
        allow_empty=True
    )

    def validate_horarios_ids(self, value):
        """Validar que los horarios no se solapen entre sí"""
        if not value:
            return value
            
        for i, horario1 in enumerate(value):
            for j, horario2 in enumerate(value[i+1:], start=i+1):
                if horario1.dia_semana == horario2.dia_semana:
                    if (horario1.hora_inicio < horario2.hora_fin and 
                        horario1.hora_fin > horario2.hora_inicio):
                        raise serializers.ValidationError(
                            f"Horarios solapados para {horario1.dia_semana}: "
                            f"'{horario1.nombre}' ({horario1.hora_inicio}-{horario1.hora_fin}) y "
                            f"'{horario2.nombre}' ({horario2.hora_inicio}-{horario2.hora_fin})"
                        )
        return value


class HorarioSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Horario
        fields = ['id', 'nombre', 'dia_semana', 'hora_inicio', 'hora_fin']


class MateriaCursoReadSerializer(serializers.ModelSerializer):
    materia_nombre = serializers.CharField(source='materia.nombre', read_only=True)
    docente_nombre = serializers.SerializerMethodField()
    horarios = HorarioSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = MateriaCurso
        fields = ['id', 'materia_id', 'materia_nombre', 'docente_id', 'docente_nombre', 'horarios']

    def get_docente_nombre(self, obj):
        return f"{obj.docente.usuario.first_name} {obj.docente.usuario.last_name}"


class CursoMateriaAsignacionSerializer(serializers.ModelSerializer):
    asignaciones = MateriaConDocenteYHorariosSerializer(many=True, write_only=True)
    materias_docentes = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Curso
        fields = ["id", "nombre", "turno", "asignaciones", "materias_docentes"]
        read_only_fields = ["id", "nombre", "turno"]

    def get_materias_docentes(self, obj):
        relaciones = MateriaCurso.objects.filter(curso=obj).prefetch_related('horarios')
        return MateriaCursoReadSerializer(relaciones, many=True).data

    def validate_asignaciones(self, value):
        """Validar que no haya duplicados materia-curso en la request"""
        materias_ids = [item['materia_id'].id for item in value]
        if len(materias_ids) != len(set(materias_ids)):
            raise serializers.ValidationError("No puedes asignar la misma materia dos veces al curso")
        return value

    def _validar_choques_horarios_globales(self, curso, asignaciones_nuevas):
        """Validar choques de horarios considerando asignaciones existentes y nuevas"""
        
        # Obtener todos los horarios ya asignados al curso
        horarios_existentes = Horario.objects.filter(
            materia_cursos__curso=curso
        ).distinct()
        
        # Crear lista de todos los horarios (existentes + nuevos)
        todos_horarios = []
        
        # Añadir horarios existentes que NO van a ser reemplazados
        materias_nuevas_ids = {item['materia_id'].id for item in asignaciones_nuevas}
        for horario in horarios_existentes:
            # Solo incluir si no está siendo reemplazado por una nueva asignación
            materias_curso_del_horario = horario.materia_cursos.filter(curso=curso)
            if not any(mc.materia.id in materias_nuevas_ids for mc in materias_curso_del_horario):
                todos_horarios.append({
                    'dia_semana': horario.dia_semana,
                    'hora_inicio': horario.hora_inicio,
                    'hora_fin': horario.hora_fin,
                    'nombre': horario.nombre,
                    'tipo': 'existente'
                })
        
        # Añadir horarios nuevos
        for asignacion in asignaciones_nuevas:
            for horario in asignacion.get('horarios_ids', []):
                todos_horarios.append({
                    'dia_semana': horario.dia_semana,
                    'hora_inicio': horario.hora_inicio,
                    'hora_fin': horario.hora_fin,
                    'nombre': horario.nombre,
                    'tipo': 'nuevo'
                })
        
        # Verificar choques entre todos los horarios
        for i, horario1 in enumerate(todos_horarios):
            for j, horario2 in enumerate(todos_horarios[i+1:], start=i+1):
                if horario1['dia_semana'] == horario2['dia_semana']:
                    if (horario1['hora_inicio'] < horario2['hora_fin'] and 
                        horario1['hora_fin'] > horario2['hora_inicio']):
                        raise serializers.ValidationError(
                            f"Choque de horarios detectado en {horario1['dia_semana']}: "
                            f"'{horario1['nombre']}' ({horario1['hora_inicio']}-{horario1['hora_fin']}) "
                            f"vs '{horario2['nombre']}' ({horario2['hora_inicio']}-{horario2['hora_fin']})"
                        )

    def _validar_choques_docente_global(self, asignaciones_nuevas):
        """Validar que el docente no tenga choques de horarios con sus otras asignaciones en cualquier curso"""
        
        for asignacion in asignaciones_nuevas:
            docente = asignacion['docente_id']
            horarios_nuevos = asignacion.get('horarios_ids', [])
            
            # Obtener TODOS los horarios actuales del docente en cualquier curso
            horarios_docente_existentes = Horario.objects.filter(
                materia_cursos__docente=docente
            ).distinct()
            
            # Verificar cada horario nuevo contra los existentes del docente
            for horario_nuevo in horarios_nuevos:
                for horario_existente in horarios_docente_existentes:
                    # Verificar si son el mismo día de la semana
                    if horario_nuevo.dia_semana == horario_existente.dia_semana:
                        # Verificar si hay solapamiento de horarios
                        if (horario_nuevo.hora_inicio < horario_existente.hora_fin and 
                            horario_nuevo.hora_fin > horario_existente.hora_inicio):
                            
                            # Obtener información de la materia y curso del horario existente
                            materia_curso_existente = horario_existente.materia_cursos.filter(docente=docente).first()
                            if materia_curso_existente:
                                raise serializers.ValidationError(
                                    f"CHOQUE DE DOCENTE: El docente {docente.usuario.first_name} {docente.usuario.last_name} "
                                    f"ya tiene asignado el horario '{horario_existente.nombre}' "
                                    f"({horario_existente.hora_inicio}-{horario_existente.hora_fin}) "
                                    f"el {horario_existente.dia_semana} para la materia '{materia_curso_existente.materia.nombre}' "
                                    f"en el curso '{materia_curso_existente.curso.nombre} - {materia_curso_existente.curso.turno}'. "
                                    f"No puede ser asignado al horario '{horario_nuevo.nombre}' "
                                    f"({horario_nuevo.hora_inicio}-{horario_nuevo.hora_fin}) al mismo tiempo."
                                )

    @transaction.atomic
    def update(self, instance, validated_data):
        asignaciones = validated_data.pop("asignaciones", [])
        
        # Validar choques de horarios globales antes de hacer cambios
        self._validar_choques_horarios_globales(instance, asignaciones)
        
        # Validar choques de horarios del docente con sus otras asignaciones en cualquier curso
        self._validar_choques_docente_global(asignaciones)
        
        # Validar que no se intente agregar materias que ya existen
        materias_existentes = MateriaCurso.objects.filter(curso=instance).values_list('materia_id', flat=True)
        for asignacion in asignaciones:
            materia_id = asignacion['materia_id'].id
            if materia_id in materias_existentes:
                materia_nombre = asignacion['materia_id'].nombre
                raise serializers.ValidationError(
                    f"La materia '{materia_nombre}' ya está asignada a este curso. "
                    f"Use PUT para actualizar o DELETE para eliminar."
                )
        
        # Crear nuevas asignaciones (solo agregar, no eliminar existentes)
        for asignacion in asignaciones:
            materia = asignacion['materia_id']
            docente = asignacion['docente_id']
            horarios_ids = asignacion.get('horarios_ids', [])
            
            # Crear nueva MateriaCurso
            materia_curso = MateriaCurso.objects.create(
                curso=instance,
                materia=materia,
                docente=docente
            )
            
            # Asignar horarios usando M2M
            materia_curso.horarios.set(horarios_ids)
        
        return instance
