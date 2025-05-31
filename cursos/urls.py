from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CursoViewSet,
    CursoConMateriasView,
    CursoConEstudiantesViewSet,
    TurnosChoicesView,
    TrimestreViewSet,
)
from cursos.viewsAsignacion import CursoMateriaAsignacionViewSet

# Registramos todos los viewsets
router = DefaultRouter()
router.register(r"cursos", CursoViewSet, basename="cursos")  # Cambiar de "" a "cursos"
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
router.register(
    r"trimestres",
    TrimestreViewSet,
    basename="trimestres",
)

urlpatterns = [
    # Rutas personalizadas que no están en el router
    path("turnos/", TurnosChoicesView.as_view(), name="turnos"),
    path(
        "con-materias/<int:id>",
        CursoConMateriasView.as_view(),
        name="curso-con-materias",
    ),
    # Rutas del router (incluye todas las acciones CRUD)
    path("", include(router.urls)),
]
