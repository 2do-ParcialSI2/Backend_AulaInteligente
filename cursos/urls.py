from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CursoViewSet,
    CursoConMateriasView,
    CursoConEstudiantesViewSet,
    TurnosChoicesView,
)
from cursos.viewsAsignacion import CursoMateriaAsignacionViewSet

# Registramos todos los viewsets
router = DefaultRouter()
router.register(r"", CursoViewSet, basename="cursos")  # Expone todas las acciones CRUD
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

urlpatterns = [
    # Rutas personalizadas que no están en el router
    path("turnos/", TurnosChoicesView.as_view(), name="turnos"),
    path(
        "con-materias/<int:id>",
        CursoConMateriasView.as_view(),
        name="curso-con-materias",
    ),
    # Rutas del router (incluye todas las acciones CRUD para cursos)
    path("", include(router.urls)),
]
