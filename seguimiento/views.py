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
import requests

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
    
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('estudiante_id', openapi.IN_PATH, description="ID del estudiante", type=openapi.TYPE_INTEGER, required=True),
            openapi.Parameter('materia_curso_id', openapi.IN_PATH, description="ID de la materia-curso", type=openapi.TYPE_INTEGER, required=True),
        ],
        responses={
            200: openapi.Response(
                description="Predicción exitosa",
                examples={
                    "application/json": {
                        "success": True,
                        "estudiante_id": 123,
                        "materia_curso_id": 456,
                        "prediccion": {
                            "nota_estimada": 84.7,
                            "clasificacion": "medio",
                            "nivel_confianza": "alto",
                            "confianza_valor": 3.2,
                            "mensaje": "Buen rendimiento. Se estima una nota de 84.7 (rendimiento medio) con alta confianza."
                        },
                        "datos_utilizados": {
                            "prom_tareas_t1": 85.0,
                            "prom_examenes_t1": 78.0,
                            "prom_part_t1": 92.0,
                            "asistencia_t1": 95.0,
                            "prom_tareas_t2": 87.0,
                            "prom_examenes_t2": 82.0,
                            "prom_part_t2": 88.0,
                            "asistencia_t2": 93.0
                        },
                        "trimestres_utilizados": ["1er Trimestre", "2do Trimestre"]
                    }
                }
            ),
            400: openapi.Response(description="Error en los datos de entrada"),
            404: openapi.Response(description="Estudiante o materia-curso no encontrado"),
            503: openapi.Response(description="Error al conectar con el microservicio de predicción")
        }
    )
    @action(detail=False, methods=['post'], url_path='predecir-nota/(?P<estudiante_id>[^/.]+)/(?P<materia_curso_id>[^/.]+)')
    def predecir_nota(self, request, estudiante_id=None, materia_curso_id=None):
        """
        Predecir la nota del tercer trimestre usando Machine Learning
        
        Este endpoint:
        1. Obtiene los datos de seguimiento del estudiante para los trimestres 1 y 2
        2. Calcula los promedios necesarios para el modelo ML
        3. Llama al microservicio de predicción
        4. Retorna la predicción formateada
        """
        try:
            # Validar que existan los IDs
            if not estudiante_id or not materia_curso_id:
                return Response({
                    'success': False,
                    'error': 'Se requieren estudiante_id y materia_curso_id'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Obtener y validar datos para predicción
            datos_prediccion = self._obtener_datos_para_prediccion(estudiante_id, materia_curso_id)
            
            if 'error' in datos_prediccion:
                return Response({
                    'success': False,
                    'error': datos_prediccion['error']
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Llamar al microservicio de predicción
            try:
                ml_response = requests.post(
                    'http://localhost:8000/api/v1/predecir/',
                    json=datos_prediccion['datos_ml'],
                    timeout=10
                )
                
                if ml_response.status_code == 200:
                    prediccion = ml_response.json()
                    
                    return Response({
                        'success': True,
                        'estudiante_id': int(estudiante_id),
                        'materia_curso_id': int(materia_curso_id),
                        'prediccion': prediccion,
                        'datos_utilizados': datos_prediccion['datos_ml'],
                        'trimestres_utilizados': datos_prediccion['trimestres_nombres']
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        'success': False,
                        'error': f'Error del microservicio ML: {ml_response.text}'
                    }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                    
            except requests.exceptions.ConnectionError:
                return Response({
                    'success': False,
                    'error': 'No se puede conectar al microservicio de predicción. Verifique que esté ejecutándose en http://localhost:8000'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            except requests.exceptions.Timeout:
                return Response({
                    'success': False,
                    'error': 'Timeout al conectar con el microservicio de predicción'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            except Exception as e:
                return Response({
                    'success': False,
                    'error': f'Error inesperado al llamar al microservicio: {str(e)}'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Error interno del servidor: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _obtener_datos_para_prediccion(self, estudiante_id, materia_curso_id):
        """
        Método auxiliar para obtener y formatear datos de seguimiento para el modelo ML
        """
        try:
            from usuarios.models import Estudiante
            from materias.models import MateriaCurso
            from cursos.models import Trimestre
            
            # Validar que existen el estudiante y materia_curso
            try:
                estudiante = Estudiante.objects.get(id=estudiante_id)
                materia_curso = MateriaCurso.objects.get(id=materia_curso_id)
            except Estudiante.DoesNotExist:
                return {'error': f'No se encontró el estudiante con ID {estudiante_id}'}
            except MateriaCurso.DoesNotExist:
                return {'error': f'No se encontró la materia-curso con ID {materia_curso_id}'}
            
            # Obtener trimestres ordenados por fecha de inicio
            trimestres = Trimestre.objects.all().order_by('fecha_inicio')
            
            if trimestres.count() < 2:
                return {'error': 'Se necesitan al menos 2 trimestres registrados para hacer predicciones'}
            
            trimestre_1 = trimestres[0]  # Primer trimestre
            trimestre_2 = trimestres[1]  # Segundo trimestre
            
            # Obtener seguimientos para ambos trimestres
            try:
                seguimiento_t1 = Seguimiento.objects.get(
                    estudiante=estudiante,
                    materia_curso=materia_curso,
                    trimestre=trimestre_1
                )
            except Seguimiento.DoesNotExist:
                return {'error': f'No se encontró seguimiento del estudiante en {trimestre_1.nombre}'}
            
            try:
                seguimiento_t2 = Seguimiento.objects.get(
                    estudiante=estudiante,
                    materia_curso=materia_curso,
                    trimestre=trimestre_2
                )
            except Seguimiento.DoesNotExist:
                return {'error': f'No se encontró seguimiento del estudiante en {trimestre_2.nombre}'}
            
            # Calcular promedios para trimestre 1
            datos_t1 = self._calcular_promedios_seguimiento(seguimiento_t1)
            
            # Calcular promedios para trimestre 2
            datos_t2 = self._calcular_promedios_seguimiento(seguimiento_t2)
            
            # Formatear datos para el modelo ML
            datos_ml = {
                'prom_tareas_t1': datos_t1['prom_tareas'],
                'prom_examenes_t1': datos_t1['prom_examenes'],
                'prom_part_t1': datos_t1['prom_participaciones'],
                'asistencia_t1': datos_t1['porcentaje_asistencia'],
                'prom_tareas_t2': datos_t2['prom_tareas'],
                'prom_examenes_t2': datos_t2['prom_examenes'],
                'prom_part_t2': datos_t2['prom_participaciones'],
                'asistencia_t2': datos_t2['porcentaje_asistencia']
            }
            
            return {
                'datos_ml': datos_ml,
                'trimestres_nombres': [trimestre_1.nombre, trimestre_2.nombre]
            }
            
        except Exception as e:
            return {'error': f'Error al procesar datos: {str(e)}'}
    
    def _calcular_promedios_seguimiento(self, seguimiento):
        """
        Calcular promedios específicos de un seguimiento (similar al método del modelo pero retornando datos separados)
        """
        # Promedio de tareas
        tareas = seguimiento.tareas.all()
        prom_tareas = sum(t.nota_tarea for t in tareas) / len(tareas) if tareas else 0

        # Promedio de participaciones
        participaciones = seguimiento.participaciones.all()
        prom_participaciones = sum(p.nota_participacion for p in participaciones) / len(participaciones) if participaciones else 0

        # Promedio de exámenes
        examenes = seguimiento.examenes.all()
        prom_examenes = sum(e.nota_examen for e in examenes) / len(examenes) if examenes else 0

        # Porcentaje de asistencia
        asistencias = seguimiento.asistencias.all()
        porcentaje_asistencia = (
            sum(1 for a in asistencias if a.asistencia) / len(asistencias) * 100
            if asistencias else 0
        )
        
        return {
            'prom_tareas': round(prom_tareas, 2),
            'prom_participaciones': round(prom_participaciones, 2),
            'prom_examenes': round(prom_examenes, 2),
            'porcentaje_asistencia': round(porcentaje_asistencia, 2)
        }


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
