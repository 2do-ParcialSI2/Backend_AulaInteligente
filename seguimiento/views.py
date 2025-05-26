from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Seguimiento, Asistencia, Participacion, Tarea, Examen, TipoExamen
from .serializers import (
    SeguimientoSerializer, AsistenciaSerializer, ParticipacionSerializer,
    TareaSerializer, ExamenSerializer, TipoExamenSerializer
)
from matricula.models import Matricula
from datetime import date

# Create your views here.

class SeguimientoViewSet(viewsets.ModelViewSet):
    queryset = Seguimiento.objects.all()
    serializer_class = SeguimientoSerializer

class AsistenciaViewSet(viewsets.ModelViewSet):
    queryset = Asistencia.objects.all()
    serializer_class = AsistenciaSerializer

class ParticipacionViewSet(viewsets.ModelViewSet):
    queryset = Participacion.objects.all()
    serializer_class = ParticipacionSerializer

class TareaViewSet(viewsets.ModelViewSet):
    queryset = Tarea.objects.all()
    serializer_class = TareaSerializer

class ExamenViewSet(viewsets.ModelViewSet):
    queryset = Examen.objects.all()
    serializer_class = ExamenSerializer

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
