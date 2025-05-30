from rest_framework import viewsets, mixins
from cursos.models import Curso
from cursos.serializersAsignacionMaterias import CursoMateriaAsignacionSerializer


class CursoMateriaAsignacionViewSet(
    viewsets.GenericViewSet, 
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin
):
    queryset = Curso.objects.all()
    serializer_class = CursoMateriaAsignacionSerializer
