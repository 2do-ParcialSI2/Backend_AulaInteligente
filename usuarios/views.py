from django.shortcuts import render
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Usuario, Estudiante, Docente, PadreTutor, Rol, Permiso
from .serializers import UsuarioSerializer, CustomTokenObtainPairSerializer, RolSerializer, PermisoSerializer, EstudianteSerializer, DocenteSerializer, PadreTutorSerializer, CrearAdminSerializer
from rest_framework import serializers
from drf_yasg.utils import swagger_auto_schema

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
        rol_docente = Rol.objects.get(nombre='DOCENTE')
        return Usuario.objects.filter(roles=rol_docente, activo=True)

class DocenteDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DocenteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        rol_docente = Rol.objects.get(nombre='DOCENTE')
        return Usuario.objects.get(pk=self.kwargs['pk'], roles=rol_docente, activo=True)

class EstudianteListCreateView(generics.ListCreateAPIView):
    serializer_class = EstudianteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        rol_estudiante = Rol.objects.get(nombre='ESTUDIANTE')
        return Usuario.objects.filter(roles=rol_estudiante, activo=True)

class EstudianteDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EstudianteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        rol_estudiante = Rol.objects.get(nombre='ESTUDIANTE')
        return Usuario.objects.get(pk=self.kwargs['pk'], roles=rol_estudiante, activo=True)

class PadreTutorListCreateView(generics.ListCreateAPIView):
    serializer_class = PadreTutorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        rol_padre = Rol.objects.get(nombre='PADRE_TUTOR')
        return Usuario.objects.filter(roles=rol_padre, activo=True)

class PadreTutorDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PadreTutorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        rol_padre = Rol.objects.get(nombre='PADRE_TUTOR')
        return Usuario.objects.get(pk=self.kwargs['pk'], roles=rol_padre, activo=True)

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
