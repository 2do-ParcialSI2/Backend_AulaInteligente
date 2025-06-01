from django.shortcuts import render
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Usuario, Estudiante, Docente, PadreTutor, Rol, Permiso
from .serializers import UsuarioSerializer, CustomTokenObtainPairSerializer, RolSerializer, PermisoSerializer, EstudianteSerializer, EstudianteCreateSerializer, EstudianteUpdateSerializer, DocenteSerializer, PadreTutorSerializer, CrearAdminSerializer
from rest_framework import serializers
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from horarios.models import Horario
from materias.models import MateriaCurso

# Create your views here.

class UsuarioListCreateView(generics.ListCreateAPIView):
    queryset = Usuario.objects.filter(activo=True)
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]

class UsuarioDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Usuario.objects.filter(activo=True)
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_destroy(self, instance):
        instance.activo = False
        instance.save()

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class RolListCreateView(generics.ListCreateAPIView):
    queryset = Rol.objects.all()
    serializer_class = RolSerializer
    permission_classes = [permissions.IsAuthenticated]

class RolDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Rol.objects.all()
    serializer_class = RolSerializer
    permission_classes = [permissions.IsAuthenticated]

class PermisoListCreateView(generics.ListCreateAPIView):
    queryset = Permiso.objects.all()
    serializer_class = PermisoSerializer
    permission_classes = [permissions.IsAuthenticated]

class PermisoDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Permiso.objects.all()
    serializer_class = PermisoSerializer
    permission_classes = [permissions.IsAuthenticated]

class DocenteListCreateView(generics.ListCreateAPIView):
    serializer_class = DocenteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Docente.objects.filter(usuario__activo=True)

class DocenteDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DocenteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Docente.objects.filter(usuario__activo=True)

    def perform_destroy(self, instance):
        # Realizar eliminación lógica del usuario asociado
        instance.usuario.activo = False
        instance.usuario.save()
        # No eliminamos el docente físicamente

class EstudianteListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Estudiante.objects.filter(usuario__activo=True)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return EstudianteCreateSerializer
        return EstudianteSerializer
    
    def create(self, request, *args, **kwargs):
        # Usar el serializer de creación para validar y crear
        create_serializer = EstudianteCreateSerializer(data=request.data)
        create_serializer.is_valid(raise_exception=True)
        estudiante_creado = create_serializer.save()
        
        # Usar el serializer de lectura para devolver la respuesta completa
        response_serializer = EstudianteSerializer(estudiante_creado)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

class EstudianteDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Estudiante.objects.filter(usuario__activo=True)

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return EstudianteUpdateSerializer
        return EstudianteSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Usar el serializer de actualización para validar y guardar
        update_serializer = EstudianteUpdateSerializer(instance, data=request.data, partial=partial)
        update_serializer.is_valid(raise_exception=True)
        updated_instance = update_serializer.save()
        
        # Usar el serializer de lectura para devolver la respuesta completa
        response_serializer = EstudianteSerializer(updated_instance)
        return Response(response_serializer.data)

    def perform_destroy(self, instance):
        # Realizar eliminación lógica del usuario asociado
        instance.usuario.activo = False
        instance.usuario.save()
        # No eliminamos el estudiante físicamente

class PadreTutorListCreateView(generics.ListCreateAPIView):
    serializer_class = PadreTutorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PadreTutor.objects.filter(usuario__activo=True)

class PadreTutorDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PadreTutorSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PadreTutor.objects.filter(usuario__activo=True)

    def perform_destroy(self, instance):
        # Realizar eliminación lógica del usuario asociado
        instance.usuario.activo = False
        instance.usuario.save()
        # No eliminamos el padre/tutor físicamente

class CrearAdminView(APIView):
    permission_classes = []  # Sin autenticación
    serializer_class = CrearAdminSerializer

    @swagger_auto_schema(request_body=CrearAdminSerializer)
    def post(self, request):
        admin_role, created = Rol.objects.get_or_create(nombre='ADMINISTRADOR')
        if Usuario.objects.filter(roles=admin_role).exists():
            return Response({'error': 'Ya existe un usuario administrador.'}, status=400)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = Usuario(
            email=data['email'],
            first_name='Admin',
            last_name='Sistema',
            activo=True
        )
        user.set_password(data['password'])
        user.save()
        user.roles.add(admin_role)
        return Response({'mensaje': 'Usuario administrador creado correctamente.'}, status=201)

class DocenteHorariosView(APIView):
    """Vista para obtener todos los horarios asignados a un docente"""
    
    def get(self, request, pk):
        try:
            docente = Docente.objects.get(pk=pk)
            
            # Obtener todos los horarios del docente
            horarios = Horario.objects.filter(
                materia_cursos__docente=docente
            ).distinct().order_by('dia_semana', 'hora_inicio')
            
            horarios_data = []
            for horario in horarios:
                # Obtener la información de materia y curso para este horario
                materia_curso = MateriaCurso.objects.filter(
                    docente=docente,
                    horarios=horario
                ).first()
                
                if materia_curso:
                    horarios_data.append({
                        'horario_id': horario.id,
                        'nombre': horario.nombre,
                        'dia_semana': horario.dia_semana,
                        'hora_inicio': horario.hora_inicio,
                        'hora_fin': horario.hora_fin,
                        'materia': materia_curso.materia.nombre,
                        'curso': f"{materia_curso.curso.nombre} - {materia_curso.curso.turno}"
                    })
            
            return Response({
                'docente': f"{docente.usuario.first_name} {docente.usuario.last_name}",
                'total_horarios': len(horarios_data),
                'horarios': horarios_data
            })
            
        except Docente.DoesNotExist:
            return Response(
                {'error': 'Docente no encontrado'},
                status=404
            )
        except Exception as e:
            return Response(
                {'error': f'Error al obtener horarios: {str(e)}'},
                status=400
            )
