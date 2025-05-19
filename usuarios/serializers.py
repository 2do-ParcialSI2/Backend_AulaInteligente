from rest_framework import serializers
from .models import Usuario, Estudiante, Docente, PadreTutor, Rol, Permiso
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UsuarioSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    class Meta:
        model = Usuario
        fields = ['id', 'correo', 'name', 'genero', 'activo', 'roles', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = Usuario(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

class EstudianteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estudiante
        fields = '__all__'

class DocenteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Docente
        fields = '__all__'

class PadreTutorSerializer(serializers.ModelSerializer):
    class Meta:
        model = PadreTutor
        fields = '__all__'

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['correo'] = user.correo
        token['roles'] = [rol.nombre for rol in user.roles.all()]
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Solo devolver el access token y los datos del usuario
        user_data = UsuarioSerializer(self.user).data
        data = {
            'token': data['access'],
            'user': user_data
        }
        return data

class PermisoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permiso
        fields = '__all__'

class RolSerializer(serializers.ModelSerializer):
    permisos = PermisoSerializer(many=True, read_only=True)
    class Meta:
        model = Rol
        fields = ['id', 'nombre', 'permisos']

class CrearAdminSerializer(serializers.Serializer):
    correo = serializers.EmailField()
    name = serializers.CharField()
    password = serializers.CharField(write_only=True) 