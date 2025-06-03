from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Matricula, TipoPago, MetodoPago
from .serializers import MatriculaSerializer, TipoPagoSerializer, MetodoPagoSerializer
import logging

logger = logging.getLogger(__name__)

# Create your views here.

class MatriculaViewSet(viewsets.ModelViewSet):
    queryset = Matricula.objects.all()
    serializer_class = MatriculaSerializer
    
    def update(self, request, *args, **kwargs):
        """Override del update para debugging"""
        try:
            logger.info(f"Actualizando matrícula {kwargs.get('pk')} con datos: {request.data}")
            
            instance = self.get_object()
            logger.info(f"Matrícula antes de actualizar: {instance.__dict__}")
            
            # Verificar si met_pago está en los datos
            if 'met_pago' in request.data:
                met_pago_id = request.data.get('met_pago')
                if met_pago_id:
                    try:
                        metodo_pago = MetodoPago.objects.get(id=met_pago_id)
                        logger.info(f"Método de pago encontrado: {metodo_pago}")
                    except MetodoPago.DoesNotExist:
                        logger.error(f"Método de pago con ID {met_pago_id} no existe")
                        return Response({
                            'error': f'Método de pago con ID {met_pago_id} no existe'
                        }, status=status.HTTP_400_BAD_REQUEST)
            
            # Usar PATCH por defecto para actualización parcial
            partial = kwargs.pop('partial', True)
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            
            if serializer.is_valid():
                self.perform_update(serializer)
                logger.info(f"Matrícula actualizada exitosamente: {serializer.instance.__dict__}")
                return Response(serializer.data)
            else:
                logger.error(f"Errores de validación: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error al actualizar matrícula: {str(e)}")
            return Response({
                'error': f'Error interno: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def partial_update(self, request, *args, **kwargs):
        """Override del partial_update para asegurar que sea parcial"""
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

class TipoPagoViewSet(viewsets.ModelViewSet):
    queryset = TipoPago.objects.all()
    serializer_class = TipoPagoSerializer

class MetodoPagoViewSet(viewsets.ModelViewSet):
    queryset = MetodoPago.objects.all()
    serializer_class = MetodoPagoSerializer
