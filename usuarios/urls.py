from django.urls import path
from .views import (
    UsuarioListCreateView, UsuarioDetailView,
    CustomTokenObtainPairView, LogoutView,
    RolListCreateView, RolDetailView,
    PermisoListCreateView, PermisoDetailView,
    EstudianteListCreateView, EstudianteDetailView,
    DocenteListCreateView, DocenteDetailView,
    PadreTutorListCreateView, PadreTutorDetailView
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('usuarios/', UsuarioListCreateView.as_view(), name='usuario-list-create'),
    path('usuarios/<int:pk>/', UsuarioDetailView.as_view(), name='usuario-detail'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('roles/', RolListCreateView.as_view(), name='rol-list-create'),
    path('roles/<int:pk>/', RolDetailView.as_view(), name='rol-detail'),
    path('permisos/', PermisoListCreateView.as_view(), name='permiso-list-create'),
    path('permisos/<int:pk>/', PermisoDetailView.as_view(), name='permiso-detail'),
    path('estudiantes/', EstudianteListCreateView.as_view(), name='estudiante-list-create'),
    path('estudiantes/<int:pk>/', EstudianteDetailView.as_view(), name='estudiante-detail'),
    path('docentes/', DocenteListCreateView.as_view(), name='docente-list-create'),
    path('docentes/<int:pk>/', DocenteDetailView.as_view(), name='docente-detail'),
    path('padres-tutores/', PadreTutorListCreateView.as_view(), name='padretutor-list-create'),
    path('padres-tutores/<int:pk>/', PadreTutorDetailView.as_view(), name='padretutor-detail'),
] 