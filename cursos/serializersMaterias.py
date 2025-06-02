from rest_framework import serializers
from cursos.models import Curso
from materias.serializers import MateriaSerializer
from materias.models import MateriaCurso, Materia
from horarios.models import Horario
from django.db.models import Q


class CursoConMateriasSerializer(serializers.ModelSerializer):
    materias = serializers.SerializerMethodField()

    class Meta:
        model = Curso
        fields = ["id", "nombre", "turno", "materias"]

    def get_materias(self, obj):
        # Solo obtener las materias activas del curso
        materias_activas = obj.materias.filter(materiacurso__activo=True)
        return MateriaSerializer(materias_activas, many=True).data


class AsignarMateriasSerializer(serializers.Serializer):
    materias_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="Lista de IDs de materias activas para asignar al curso"
    )

    def validate_materias_ids(self, value):
        # Verificar que todas las materias existan y estén activas
        materias_existentes = Materia.objects.filter(id__in=value, activo=True)
        if len(materias_existentes) != len(value):
            raise serializers.ValidationError("Una o más materias no existen o están inactivas")
        return value

    def create(self, validated_data):
        curso = self.context['curso']
        materias_ids = validated_data['materias_ids']
        
        asignaciones_creadas = []
        for materia_id in materias_ids:
            asignacion, created = MateriaCurso.objects.get_or_create(
                curso=curso,
                materia_id=materia_id
            )
            if created:
                asignaciones_creadas.append(asignacion)
        
        return asignaciones_creadas


class AsignarDocenteSerializer(serializers.Serializer):
    docente_id = serializers.IntegerField()

    def validate(self, data):
        docente_id = data['docente_id']
        materia_curso = self.instance  # La instancia actual de MateriaCurso

        # Si la materia ya tiene horarios asignados, verificar conflictos
        if materia_curso.horarios.exists():
            # Buscar otras materias que dicta el docente
            otras_materias = MateriaCurso.objects.filter(
                docente_id=docente_id
            ).exclude(id=materia_curso.id)

            # Verificar conflictos de horario
            for horario in materia_curso.horarios.all():
                conflictos = otras_materias.filter(
                    horarios__dia_semana=horario.dia_semana,
                    horarios__hora_inicio__lt=horario.hora_fin,
                    horarios__hora_fin__gt=horario.hora_inicio
                )
                
                if conflictos.exists():
                    conflicto = conflictos.first()
                    raise serializers.ValidationError(
                        f"El docente ya tiene asignada la materia '{conflicto.materia.nombre}' "
                        f"en el curso '{conflicto.curso.nombre}' durante el horario "
                        f"{horario.dia_semana} de {horario.hora_inicio} a {horario.hora_fin}"
                    )

        return data

    def update(self, instance, validated_data):
        instance.docente_id = validated_data['docente_id']
        instance.save()
        return instance


class AsignarHorariosSerializer(serializers.Serializer):
    horarios_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="Lista de IDs de horarios para asignar a la materia en este curso"
    )

    def validate_horarios_ids(self, value):
        # Verificar que todos los horarios existan y estén activos
        horarios = Horario.objects.filter(id__in=value, activo=True)
        if len(horarios) != len(value):
            raise serializers.ValidationError("Uno o más horarios no existen o están inactivos")
        return value

    def validate(self, data):
        horarios_ids = data['horarios_ids']
        materia_curso = self.instance  # La instancia actual de MateriaCurso
        nuevos_horarios = Horario.objects.filter(id__in=horarios_ids)

        # Si hay un docente asignado, verificar conflictos
        if materia_curso.docente:
            # Buscar otras materias que dicta el docente
            otras_materias = MateriaCurso.objects.filter(
                docente=materia_curso.docente
            ).exclude(id=materia_curso.id)

            # Verificar conflictos para cada nuevo horario
            for horario in nuevos_horarios:
                conflictos = otras_materias.filter(
                    horarios__dia_semana=horario.dia_semana,
                    horarios__hora_inicio__lt=horario.hora_fin,
                    horarios__hora_fin__gt=horario.hora_inicio
                )
                
                if conflictos.exists():
                    conflicto = conflictos.first()
                    raise serializers.ValidationError(
                        f"El docente {materia_curso.docente.usuario.get_full_name()} "
                        f"ya tiene asignada la materia '{conflicto.materia.nombre}' "
                        f"en el curso '{conflicto.curso.nombre}' durante el horario "
                        f"{horario.dia_semana} de {horario.hora_inicio} a {horario.hora_fin}"
                    )

        return data

    def update(self, instance, validated_data):
        instance.horarios.set(validated_data['horarios_ids'])
        return instance
