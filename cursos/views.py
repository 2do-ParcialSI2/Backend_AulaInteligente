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
from cursos.serializersMaterias import (
    CursoConMateriasSerializer,
    AsignarMateriasSerializer,
    AsignarDocenteSerializer,
    AsignarHorariosSerializer,
)
from materias.models import MateriaCurso
from materias.serializers import MateriaSerializer


class CursoViewSet(viewsets.ModelViewSet):
    serializer_class = CursoSerializer

    def get_queryset(self):
        return Curso.objects.filter(activo=True)

    def perform_destroy(self, instance):
        instance.activo = False
        instance.save()

    @action(detail=True, methods=['post'], url_path='asignar-materias')
    def asignar_materias(self, request, pk=None):
        """Asignar una o más materias al curso"""
        curso = self.get_object()
        serializer = AsignarMateriasSerializer(data=request.data, context={'curso': curso})
        serializer.is_valid(raise_exception=True)
        asignaciones = serializer.save()
        
        return Response({
            "message": f"Se asignaron {len(asignaciones)} materias al curso {curso.nombre}",
            "asignaciones": [
                {
                    "materia": asignacion.materia.nombre,
                    "curso": asignacion.curso.nombre
                }
                for asignacion in asignaciones
            ]
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='asignar-docente/(?P<materia_id>[^/.]+)')
    def asignar_docente(self, request, pk=None, materia_id=None):
        """Asignar un docente a una materia específica del curso"""
        try:
            curso = self.get_object()
            materia_curso = MateriaCurso.objects.get(curso=curso, materia_id=materia_id)
            
            serializer = AsignarDocenteSerializer(materia_curso, data=request.data)
            serializer.is_valid(raise_exception=True)
            asignacion = serializer.save()
            
            return Response({
                "message": f"Docente asignado a {asignacion.materia.nombre} en {curso.nombre}",
                "docente": asignacion.docente.usuario.get_full_name()
            })
        except MateriaCurso.DoesNotExist:
            return Response(
                {"error": "La materia no está asignada a este curso"},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'], url_path='asignar-horarios/(?P<materia_id>[^/.]+)')
    def asignar_horarios(self, request, pk=None, materia_id=None):
        """Asignar horarios a una materia específica del curso"""
        try:
            curso = self.get_object()
            materia_curso = MateriaCurso.objects.get(curso=curso, materia_id=materia_id)
            
            serializer = AsignarHorariosSerializer(materia_curso, data=request.data)
            serializer.is_valid(raise_exception=True)
            asignacion = serializer.save()
            
            return Response({
                "message": f"Horarios asignados a {asignacion.materia.nombre} en {curso.nombre}",
                "horarios": [
                    str(horario) for horario in asignacion.horarios.all()
                ]
            })
        except MateriaCurso.DoesNotExist:
            return Response(
                {"error": "La materia no está asignada a este curso"},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['delete'], url_path='eliminar-materia/(?P<materia_id>[^/.]+)')
    def eliminar_materia(self, request, pk=None, materia_id=None):
        """Eliminar lógicamente una asignación específica de materia del curso"""
        try:
            curso = self.get_object()
            asignacion = MateriaCurso.objects.get(curso=curso, materia_id=materia_id)
            materia_nombre = asignacion.materia.nombre
            
            # Eliminación lógica
            asignacion.activo = False
            asignacion.save()
            
            return Response(
                {"message": f"Materia '{materia_nombre}' desactivada en el curso {curso.nombre}"},
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
    # queryset = Curso.objects.all()
    # lookup_field = "id"
    serializer_class = CursoConMateriasSerializer
    lookup_field = "id"

    def get_queryset(self):
        return Curso.objects.filter(activo=True).prefetch_related(
            'materias',
            'materias__materiacurso_set'
        )

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
