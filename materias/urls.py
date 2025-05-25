from django.urls import path
from cursos.views import CursoConMateriasView
from materias.views import MateriaListCreateView, MateriaRetrieveUpdateDestroyView

urlpatterns = [
    path("", MateriaListCreateView.as_view(), name="materia-list-create"),
    path(
        "<int:pk>/", MateriaRetrieveUpdateDestroyView.as_view(), name="materia-detail"
    ),
    path("curso/<int:id>/", CursoConMateriasView.as_view(), name="curso-con-materias"),
]
