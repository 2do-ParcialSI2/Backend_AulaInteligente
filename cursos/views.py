from rest_framework import viewsets
from rest_framework.generics import RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from cursos.models import Curso
from cursos.serializers import (
    CursoSerializer,
    CursoConEstudiantesSerializer,
)
from cursos.serializersMaterias import CursoConMateriasSerializer
from materias.serializers import MateriaSerializer


class CursoViewSet(viewsets.ModelViewSet):
    queryset = Curso.objects.all()
    serializer_class = CursoSerializer


class CursoConEstudiantesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Curso.objects.all()
    serializer_class = CursoConEstudiantesSerializer


class CursoConMateriasView(RetrieveAPIView):
    queryset = Curso.objects.all()
    lookup_field = "id"
    serializer_class = CursoConMateriasSerializer


class TurnosChoicesView(APIView):
    def get(self, request):
        turnos = [
            {"value": turno[0], "label": turno[1]} for turno in Curso.TURNO_CHOICES
        ]
        return Response(turnos)
