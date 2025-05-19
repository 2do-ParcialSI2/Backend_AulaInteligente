from django.shortcuts import render
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Usuario, Estudiante, Docente, PadreTutor, Rol, Permiso
from .serializers import UsuarioSerializer, CustomTokenObtainPairSerializer, RolSerializer, PermisoSerializer, EstudianteSerializer, DocenteSerializer, PadreTutorSerializer

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

class EstudianteListCreateView(generics.ListCreateAPIView):
    queryset = Estudiante.objects.all()
    serializer_class = EstudianteSerializer
    permission_classes = [permissions.IsAuthenticated]

class EstudianteDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Estudiante.objects.all()
    serializer_class = EstudianteSerializer
    permission_classes = [permissions.IsAuthenticated]

class DocenteListCreateView(generics.ListCreateAPIView):
    queryset = Docente.objects.all()
    serializer_class = DocenteSerializer
    permission_classes = [permissions.IsAuthenticated]

class DocenteDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Docente.objects.all()
    serializer_class = DocenteSerializer
    permission_classes = [permissions.IsAuthenticated]

class PadreTutorListCreateView(generics.ListCreateAPIView):
    queryset = PadreTutor.objects.all()
    serializer_class = PadreTutorSerializer
    permission_classes = [permissions.IsAuthenticated]

class PadreTutorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PadreTutor.objects.all()
    serializer_class = PadreTutorSerializer
    permission_classes = [permissions.IsAuthenticated]
