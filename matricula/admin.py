from django.contrib import admin
from .models import Matricula, TipoPago, MetodoPago

# Register your models here.

@admin.register(MetodoPago)
class MetodoPagoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion']
    search_fields = ['nombre']

@admin.register(TipoPago)
class TipoPagoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo']
    list_filter = ['tipo']
    search_fields = ['nombre']

@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display = ['estudiante', 'tipo_pago', 'met_pago', 'fecha', 'monto', 'estado']
    list_filter = ['estado', 'tipo_pago', 'met_pago', 'fecha']
    search_fields = ['estudiante__usuario__first_name', 'estudiante__usuario__last_name']
    date_hierarchy = 'fecha'
