from django.db import models
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

# Create your models here.

class MetodoPago(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre

class TipoPago(models.Model):
    OPCIONES_PAGO = [
        ('mensual', 'Mensual'),
        ('anual', 'Anual'),
    ]
    
    nombre = models.CharField(max_length=50)
    tipo = models.CharField(max_length=20, choices=OPCIONES_PAGO, default='mensual')

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"

class Matricula(models.Model):
    estudiante = models.ForeignKey('usuarios.Estudiante', on_delete=models.CASCADE)
    tipo_pago = models.ForeignKey('matricula.TipoPago', on_delete=models.SET_NULL, null=True)
    met_pago = models.ForeignKey('matricula.MetodoPago', on_delete=models.SET_NULL, null=True)
    fecha = models.DateField()
    monto = models.FloatField()
    descuento = models.FloatField(default=0)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.estudiante} - {self.fecha}"

    def esta_vigente_para_fecha(self, fecha_examen):
        """
        Verifica si la matrícula está vigente para una fecha de examen específica
        """
        if not self.estado:
            return False
            
        if self.tipo_pago and self.tipo_pago.tipo == 'anual':
            # Si es pago anual, está vigente por todo el año académico
            return True
        elif self.tipo_pago and self.tipo_pago.tipo == 'mensual':
            # Si es pago mensual, verificar si está dentro del mes de pago
            fecha_vencimiento = self.fecha + relativedelta(months=1)
            return fecha_examen <= fecha_vencimiento
        
        return False

    @classmethod
    def estudiante_puede_rendir_examen(cls, estudiante, fecha_examen):
        """
        Método de clase para verificar si un estudiante puede rendir un examen en una fecha específica
        """
        # Buscar la matrícula más reciente del estudiante que esté activa
        matricula_activa = cls.objects.filter(
            estudiante=estudiante,
            estado=True
        ).order_by('-fecha').first()
        
        if not matricula_activa:
            return False, "No tiene matrícula activa"
            
        if matricula_activa.esta_vigente_para_fecha(fecha_examen):
            return True, matricula_activa
        else:
            if matricula_activa.tipo_pago.tipo == 'mensual':
                return False, "Matrícula mensual vencida. Debe renovar el pago."
            else:
                return False, "Matrícula no vigente"
