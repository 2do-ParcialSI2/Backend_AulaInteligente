from django.urls import path
from materias.views import MateriaListCreateView, MateriaRetrieveUpdateDestroyView

urlpatterns = [
    path("", MateriaListCreateView.as_view(), name="materia-list-create"),
    path(
        "<int:pk>/", MateriaRetrieveUpdateDestroyView.as_view(), name="materia-detail"
    ),
]
