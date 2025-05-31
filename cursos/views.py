from rest_framework import viewsets
from rest_framework.generics import RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from cursos.models import Curso, Trimestre
from cursos.serializers import (
    CursoSerializer,
    CursoConEstudiantesSerializer,
    TrimestreSerializer,
    TrimestreCreateSerializer,
)
from cursos.serializersMaterias import CursoConMateriasSerializer
from materias.models import MateriaCurso
from materias.serializers import MateriaSerializer


class CursoViewSet(viewsets.ModelViewSet):
    queryset = Curso.objects.all()
    serializer_class = CursoSerializer

    @action(detail=True, methods=['delete'], url_path='eliminar-materia/(?P<materia_id>[^/.]+)')
    def eliminar_materia(self, request, pk=None, materia_id=None):
        """Eliminar una asignación específica de materia-docente del curso"""
        try:
            curso = self.get_object()
            asignacion = MateriaCurso.objects.get(curso=curso, materia_id=materia_id)
            materia_nombre = asignacion.materia.nombre
            asignacion.delete()
            return Response(
                {"message": f"Materia '{materia_nombre}' eliminada del curso {curso.nombre}"},
                status=status.HTTP_200_OK
            )
        except MateriaCurso.DoesNotExist:
            return Response(
                {"error": "La materia no está asignada a este curso"},
                status=status.HTTP_404_NOT_FOUND
            )


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


class TrimestreViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar trimestres con CRUD completo"""
    queryset = Trimestre.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TrimestreCreateSerializer
        return TrimestreSerializer
    
    def create(self, request, *args, **kwargs):
        """Crear un nuevo trimestre"""
        create_serializer = TrimestreCreateSerializer(data=request.data)
        create_serializer.is_valid(raise_exception=True)
        trimestre_creado = create_serializer.save()
        
        # Usar el serializer de lectura para la respuesta
        response_serializer = TrimestreSerializer(trimestre_creado)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    def get_queryset(self):
        """Ordenar trimestres por fecha de inicio"""
        return Trimestre.objects.all().order_by('fecha_inicio')
