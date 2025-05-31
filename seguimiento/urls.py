from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SeguimientoViewSet, AsistenciaViewSet, ParticipacionViewSet,
    TareaViewSet, ExamenViewSet, TipoExamenViewSet, VerificarMatriculaExamenView,
    ResumenEstudianteView
)

router = DefaultRouter()
router.register(r'seguimientos', SeguimientoViewSet)
router.register(r'asistencias', AsistenciaViewSet)
router.register(r'participaciones', ParticipacionViewSet)
router.register(r'tareas', TareaViewSet)
router.register(r'examenes', ExamenViewSet)
router.register(r'tipoexamen', TipoExamenViewSet)

urlpatterns = [
    path('verificar-matricula/<int:estudiante_id>/', VerificarMatriculaExamenView.as_view(), name='verificar-matricula'),
    path('resumen-estudiante/<int:estudiante_id>/', ResumenEstudianteView.as_view(), name='resumen-estudiante'),
    path('', include(router.urls)),
] 