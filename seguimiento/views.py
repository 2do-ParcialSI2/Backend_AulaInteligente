from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Seguimiento, Asistencia, Participacion, Tarea, Examen, TipoExamen
from .serializers import (
    SeguimientoSerializer, SeguimientoDetalladoSerializer, AsistenciaSerializer, 
    ParticipacionSerializer, TareaSerializer, ExamenSerializer, TipoExamenSerializer
)
from matricula.models import Matricula
from datetime import date

# Create your views here.

class SeguimientoViewSet(viewsets.ModelViewSet):
    queryset = Seguimiento.objects.all()
    serializer_class = SeguimientoSerializer
    
    def get_serializer_class(self):
        if self.action == 'detallado':
            return SeguimientoDetalladoSerializer
        return SeguimientoSerializer
    
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('trimestre', openapi.IN_QUERY, description="ID del trimestre", type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('curso', openapi.IN_QUERY, description="ID del curso", type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('estudiante', openapi.IN_QUERY, description="ID del estudiante", type=openapi.TYPE_INTEGER, required=False),
        ]
    )
    @action(detail=False, methods=['get'])
    def detallado(self, request):
        """Obtener seguimientos con información detallada"""
        seguimientos = self.get_queryset()
        trimestre_id = request.query_params.get('trimestre', None)
        curso_id = request.query_params.get('curso', None)
        estudiante_id = request.query_params.get('estudiante', None)
        
        if trimestre_id:
            seguimientos = seguimientos.filter(trimestre_id=trimestre_id)
        if curso_id:
            seguimientos = seguimientos.filter(materia_curso__curso_id=curso_id)
        if estudiante_id:
            seguimientos = seguimientos.filter(estudiante_id=estudiante_id)
            
        serializer = SeguimientoDetalladoSerializer(seguimientos, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def calcular_nota(self, request, pk=None):
        """Recalcular la nota trimestral de un seguimiento específico"""
        seguimiento = self.get_object()
        nota_calculada = seguimiento.calcular_nota_trimestral()
        return Response({
            'message': 'Nota recalculada exitosamente',
            'nota_anterior': seguimiento.nota_trimestral,
            'nota_nueva': nota_calculada
        })

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('estudiante_id', openapi.IN_QUERY, description="ID del estudiante", type=openapi.TYPE_INTEGER, required=True),
        ]
    )
    @action(detail=False, methods=['get'])
    def por_estudiante(self, request):
        """Obtener seguimientos agrupados por estudiante"""
        estudiante_id = request.query_params.get('estudiante_id')
        if not estudiante_id:
            return Response({'error': 'Se requiere estudiante_id'}, status=400)
        
        seguimientos = Seguimiento.objects.filter(estudiante_id=estudiante_id)
        serializer = SeguimientoDetalladoSerializer(seguimientos, many=True)
        return Response(serializer.data)


class AsistenciaViewSet(viewsets.ModelViewSet):
    queryset = Asistencia.objects.all()
    serializer_class = AsistenciaSerializer
    
    @action(detail=False, methods=['post'])
    def registro_masivo(self, request):
        """Registrar asistencia para múltiples estudiantes"""
        data = request.data
        seguimientos_ids = data.get('seguimientos', [])
        fecha = data.get('fecha')
        asistencias = data.get('asistencias', [])  # Lista de booleans
        
        if len(seguimientos_ids) != len(asistencias):
            return Response(
                {'error': 'La cantidad de seguimientos debe coincidir con las asistencias'}, 
                status=400
            )
        
        resultados = []
        for seguimiento_id, presente in zip(seguimientos_ids, asistencias):
            asistencia, created = Asistencia.objects.get_or_create(
                seguimiento_id=seguimiento_id,
                fecha=fecha,
                defaults={'asistencia': presente}
            )
            if not created:
                asistencia.asistencia = presente
                asistencia.save()
            
            resultados.append({
                'seguimiento_id': seguimiento_id,
                'presente': presente,
                'creado': created
            })
        
        return Response({
            'message': f'Asistencia registrada para {len(resultados)} estudiantes',
            'resultados': resultados
        })


class ParticipacionViewSet(viewsets.ModelViewSet):
    queryset = Participacion.objects.all()
    serializer_class = ParticipacionSerializer


class TareaViewSet(viewsets.ModelViewSet):
    queryset = Tarea.objects.all()
    serializer_class = TareaSerializer
    
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('seguimiento_id', openapi.IN_QUERY, description="ID del seguimiento", type=openapi.TYPE_INTEGER, required=True),
        ]
    )
    @action(detail=False, methods=['get'])
    def por_seguimiento(self, request):
        """Obtener tareas de un seguimiento específico"""
        seguimiento_id = request.query_params.get('seguimiento_id')
        if not seguimiento_id:
            return Response({'error': 'Se requiere seguimiento_id'}, status=400)
        
        tareas = Tarea.objects.filter(seguimiento_id=seguimiento_id).order_by('-fecha')
        serializer = TareaSerializer(tareas, many=True)
        return Response(serializer.data)


class ExamenViewSet(viewsets.ModelViewSet):
    queryset = Examen.objects.all()
    serializer_class = ExamenSerializer
    
    @action(detail=False, methods=['get'])
    def proximos(self, request):
        """Obtener exámenes próximos"""
        from datetime import timedelta
        fecha_limite = date.today() + timedelta(days=30)
        
        examenes = Examen.objects.filter(
            fecha__gte=date.today(),
            fecha__lte=fecha_limite
        ).order_by('fecha')
        
        serializer = ExamenSerializer(examenes, many=True)
        return Response(serializer.data)


class TipoExamenViewSet(viewsets.ModelViewSet):
    queryset = TipoExamen.objects.all()
    serializer_class = TipoExamenSerializer


class VerificarMatriculaExamenView(APIView):
    """
    Endpoint para verificar si un estudiante puede rendir exámenes
    """
    def get(self, request, estudiante_id):
        try:
            from usuarios.models import Estudiante
            estudiante = Estudiante.objects.get(id=estudiante_id)
            fecha_hoy = date.today()
            
            puede_rendir, resultado = Matricula.estudiante_puede_rendir_examen(estudiante, fecha_hoy)
            
            response_data = {
                'puede_rendir': puede_rendir,
                'mensaje': resultado if isinstance(resultado, str) else 'Matrícula vigente',
                'estudiante': str(estudiante),
                'fecha_consulta': fecha_hoy
            }
            
            if isinstance(resultado, Matricula):
                response_data['matricula'] = {
                    'id': resultado.id,
                    'tipo_pago': resultado.tipo_pago.get_tipo_display() if resultado.tipo_pago else 'Sin tipo',
                    'fecha_pago': resultado.fecha,
                    'monto': resultado.monto
                }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Error al verificar matrícula: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class ResumenEstudianteView(APIView):
    """Vista para obtener resumen completo de un estudiante"""
    
    def get(self, request, estudiante_id):
        try:
            from usuarios.models import Estudiante
            estudiante = Estudiante.objects.get(id=estudiante_id)
            
            # Obtener todos los seguimientos del estudiante
            seguimientos = Seguimiento.objects.filter(estudiante=estudiante)
            
            resumen = {
                'estudiante': {
                    'id': estudiante.id,
                    'nombre': f"{estudiante.usuario.first_name} {estudiante.usuario.last_name}",
                    'email': estudiante.usuario.email
                },
                'total_materias': seguimientos.count(),
                'promedio_general': 0,
                'materias': []
            }
            
            total_notas = 0
            count_notas = 0
            
            for seguimiento in seguimientos:
                materia_info = {
                    'materia': seguimiento.materia_curso.materia.nombre,
                    'curso': seguimiento.materia_curso.curso.nombre,
                    'trimestre': seguimiento.trimestre.nombre,
                    'nota_trimestral': seguimiento.nota_trimestral,
                    'total_asistencias': seguimiento.asistencias.count(),
                    'total_tareas': seguimiento.tareas.count(),
                    'total_participaciones': seguimiento.participaciones.count(),
                    'total_examenes': seguimiento.examenes.count()
                }
                resumen['materias'].append(materia_info)
                
                if seguimiento.nota_trimestral > 0:
                    total_notas += seguimiento.nota_trimestral
                    count_notas += 1
            
            if count_notas > 0:
                resumen['promedio_general'] = round(total_notas / count_notas, 2)
            
            return Response(resumen)
            
        except Exception as e:
            return Response(
                {'error': f'Error al obtener resumen: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
