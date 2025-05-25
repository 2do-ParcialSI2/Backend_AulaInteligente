from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DiasSemanaChoicesView,
    HorarioViewSet,
    HorariosPorDiaView,
    HorariosPorMateriaView,
)

router = DefaultRouter()
router.register(r"", HorarioViewSet)

urlpatterns = [
    path("dias-semana/", DiasSemanaChoicesView.as_view(), name="dias-semana"),
    # path("horarios-dia/<str:dia>/", HorariosPorDiaView.as_view()),
    path("por-dia/<str:dia>/", HorariosPorDiaView.as_view(), name="horarios-por-dia"),
    path(
        "por-materia/<int:materia_id>/",
        HorariosPorMateriaView.as_view(),
        name="horarios-por-materia",
    ),
    path("", include(router.urls)),
]
