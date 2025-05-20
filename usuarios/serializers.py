from rest_framework import serializers
from .models import Usuario, Estudiante, Docente, PadreTutor, Rol, Permiso
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'email', 'first_name', 'last_name', 'genero', 'activo', 'roles', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        roles = validated_data.pop('roles', [])
        password = validated_data.pop('password', None)
        user = Usuario(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        if roles:
            user.roles.set(roles)
        return user

class EstudianteSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = Usuario
        fields = ['id', 'email', 'first_name', 'last_name', 'genero', 'activo', 'roles', 'password']
        read_only_fields = ['id', 'roles']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = Usuario(**validated_data)
        user.set_password(password)
        user.save()
        
        rol_estudiante = Rol.objects.get(nombre='ESTUDIANTE')
        user.roles.add(rol_estudiante)
        
        return user

class DocenteSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    especialidad = serializers.CharField(required=True)
    
    class Meta:
        model = Usuario
        fields = ['id', 'email', 'first_name', 'last_name', 'genero', 'activo', 'roles', 'password', 'especialidad']
        read_only_fields = ['id', 'roles']

    def create(self, validated_data):
        especialidad = validated_data.pop('especialidad')
        password = validated_data.pop('password')
        user = Usuario(**validated_data)
        user.set_password(password)
        user.save()
        
        rol_docente = Rol.objects.get(nombre='DOCENTE')
        user.roles.add(rol_docente)
        
        docente = Docente.objects.create(
            usuario=user,
            especialidad=especialidad
        )
        
        return user

    def to_representation(self, instance):
        data = super().to_representation(instance)
        try:
            docente = Docente.objects.get(usuario=instance)
            data['especialidad'] = docente.especialidad
        except Docente.DoesNotExist:
            data['especialidad'] = None
        return data

class PadreTutorSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = Usuario
        fields = ['id', 'email', 'first_name', 'last_name', 'genero', 'activo', 'roles', 'password']
        read_only_fields = ['id', 'roles']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = Usuario(**validated_data)
        user.set_password(password)
        user.save()
        
        rol_padre = Rol.objects.get(nombre='PADRE_TUTOR')
        user.roles.add(rol_padre)
        
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
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
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True) 