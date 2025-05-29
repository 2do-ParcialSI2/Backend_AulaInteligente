from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CursoViewSet,
    CursoConMateriasView,
    CursoConEstudiantesViewSet,
    TurnosChoicesView,
)
from cursos.viewsAsignacion import CursoMateriaAsignacionViewSet

# Registramos solo los viewsets adicionales
router = DefaultRouter()
router.register(
    r"cursos-con-estudiantes",
    CursoConEstudiantesViewSet,
    basename="cursos-con-estudiantes",
)
router.register(
    r"asignar-materias",
    CursoMateriaAsignacionViewSet,
    basename="asignar-materias",
)

# Acciones manuales de CursoViewSet
curso_list = CursoViewSet.as_view({"get": "list"})
curso_detail = CursoViewSet.as_view({"get": "retrieve"})

urlpatterns = [
    # Rutas personalizadas
    path("", curso_list, name="curso-lista"),
    path("<int:pk>/", curso_detail, name="curso-detalle"),
    path("turnos/", TurnosChoicesView.as_view(), name="turnos"),
    path(
        "con-materias/<int:id>",
        CursoConMateriasView.as_view(),
        name="curso-con-materias",
    ),
    # Rutas adicionales con include(router.urls)
    path(
        "", include(router.urls)
    ),  # Mantiene las otras rutas de los viewsets registrados
]
