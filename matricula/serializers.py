from rest_framework import serializers
from .models import Matricula, TipoPago, MetodoPago

class MatriculaSerializer(serializers.ModelSerializer):
    # Campos opcionales para mostrar información adicional
    estudiante_nombre = serializers.CharField(source='estudiante.usuario.get_full_name', read_only=True)
    tipo_pago_nombre = serializers.CharField(source='tipo_pago.nombre', read_only=True)
    metodo_pago_nombre = serializers.CharField(source='met_pago.nombre', read_only=True)
    
    class Meta:
        model = Matricula
        fields = '__all__'
        extra_kwargs = {
            'estudiante': {'required': False},  # No requerido en actualizaciones
            'fecha': {'required': False},       # No requerido en actualizaciones
            'monto': {'required': False},       # No requerido en actualizaciones
        }
    
    def validate_met_pago(self, value):
        """Validar que el método de pago existe"""
        if value and not MetodoPago.objects.filter(id=value.id if hasattr(value, 'id') else value).exists():
            raise serializers.ValidationError("El método de pago especificado no existe")
        return value
    
    def validate_tipo_pago(self, value):
        """Validar que el tipo de pago existe"""
        if value and not TipoPago.objects.filter(id=value.id if hasattr(value, 'id') else value).exists():
            raise serializers.ValidationError("El tipo de pago especificado no existe")
        return value
    
    def update(self, instance, validated_data):
        """Override del update para logging y control"""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"Actualizando matrícula ID {instance.id}")
        logger.info(f"Datos validados: {validated_data}")
        
        # Actualizar solo los campos que vienen en validated_data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        logger.info(f"Matrícula {instance.id} actualizada exitosamente")
        return instance

class TipoPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoPago
        fields = '__all__'

class MetodoPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetodoPago
        fields = '__all__'