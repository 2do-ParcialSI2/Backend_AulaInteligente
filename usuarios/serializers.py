from rest_framework import serializers
from .models import Usuario, Estudiante, Docente, PadreTutor, Rol, Permiso
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from cursos.serializers import CursoSerializer


class UsuarioSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "genero",
            "activo",
            "roles",
            "password",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        roles = validated_data.pop("roles", [])
        password = validated_data.pop("password", None)
        user = Usuario(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        if roles:
            user.roles.set(roles)
        return user

    def get_roles(self, obj):
        return [
            {
                "id": rol.id,
                "nombre": rol.nombre,
                "permisos": [permiso.nombre for permiso in rol.permisos.all()]
            }
            for rol in obj.roles.all()
        ]

class EstudianteCreateSerializer(serializers.ModelSerializer):
    """Serializer para CREAR estudiantes - solo campos necesarios"""
    email = serializers.EmailField(write_only=True, required=False)
    first_name = serializers.CharField(write_only=True, required=False)
    last_name = serializers.CharField(write_only=True, required=False)
    genero = serializers.CharField(write_only=True, required=False)
    activo = serializers.BooleanField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, required=True)
    direccion = serializers.CharField(required=True)
    fecha_nacimiento = serializers.DateField(required=True)
    padre_tutor_id = serializers.IntegerField(write_only=True, required=False)
    curso_id = serializers.IntegerField(
        write_only=True, 
        required=False,
        allow_null=True,
        help_text="ID del curso al que asignar el estudiante"
    )

    class Meta:
        model = Estudiante
        fields = [
            "email",
            "first_name",
            "last_name",
            "genero",
            "activo",
            "password",
            "direccion",
            "fecha_nacimiento",
            "padre_tutor_id",
            "curso_id",
        ]

    def create(self, validated_data):
        direccion = validated_data.pop("direccion")
        fecha_nacimiento = validated_data.pop("fecha_nacimiento")
        padre_tutor_id = validated_data.pop("padre_tutor_id", None)
        curso_id = validated_data.pop("curso_id", None)
        password = validated_data.pop("password")

        user = Usuario(**validated_data)
        user.set_password(password)
        user.save()

        rol_estudiante = Rol.objects.get(nombre="ESTUDIANTE")
        user.roles.add(rol_estudiante)

        estudiante = Estudiante.objects.create(
            usuario=user, direccion=direccion, fecha_nacimiento=fecha_nacimiento
        )

        # Asignar curso si se proporcionó
        if curso_id:
            from cursos.models import Curso
            try:
                curso = Curso.objects.get(id=curso_id)
                estudiante.curso = curso
                estudiante.save()
            except Curso.DoesNotExist:
                raise serializers.ValidationError(f"El curso con ID {curso_id} no existe")

        # Asignar padre/tutor si se proporcionó
        if padre_tutor_id:
            try:
                padre_tutor = PadreTutor.objects.get(id=padre_tutor_id)
                estudiante.padre_tutor = padre_tutor
                estudiante.save()
            except PadreTutor.DoesNotExist:
                pass

        return estudiante


class EstudianteUpdateSerializer(serializers.ModelSerializer):
    """Serializer para ACTUALIZAR estudiantes - campos permitidos para editar"""
    padre_tutor_id = serializers.IntegerField(
        write_only=True, 
        required=False, 
        allow_null=True,
        help_text="ID del padre/tutor a asignar"
    )
    curso_id = serializers.IntegerField(
        write_only=True, 
        required=False, 
        allow_null=True,
        help_text="ID del curso al que asignar el estudiante"
    )

    class Meta:
        model = Estudiante
        fields = [
            "direccion",
            "fecha_nacimiento", 
            "padre_tutor_id",
            "curso_id"
        ]

    def update(self, instance, validated_data):
        # Actualizar campos directos del estudiante
        instance.direccion = validated_data.get('direccion', instance.direccion)
        instance.fecha_nacimiento = validated_data.get('fecha_nacimiento', instance.fecha_nacimiento)
        
        # Manejar padre_tutor_id
        padre_tutor_id = validated_data.get('padre_tutor_id')
        if padre_tutor_id is not None:
            if padre_tutor_id == 0 or padre_tutor_id == '':
                instance.padre_tutor = None
            else:
                try:
                    padre_tutor = PadreTutor.objects.get(id=padre_tutor_id)
                    instance.padre_tutor = padre_tutor
                except PadreTutor.DoesNotExist:
                    raise serializers.ValidationError(f"El padre/tutor con ID {padre_tutor_id} no existe")
        
        # Manejar curso_id
        curso_id = validated_data.get('curso_id')
        if curso_id is not None:
            if curso_id == 0 or curso_id == '':
                instance.curso = None
            else:
                from cursos.models import Curso
                try:
                    curso = Curso.objects.get(id=curso_id)
                    instance.curso = curso
                except Curso.DoesNotExist:
                    raise serializers.ValidationError(f"El curso con ID {curso_id} no existe")
        
        instance.save()
        return instance


class EstudianteSerializer(serializers.ModelSerializer):
    """Serializer para LEER estudiantes - incluye todos los datos"""
    email = serializers.EmailField(source='usuario.email', read_only=True)
    first_name = serializers.CharField(source='usuario.first_name', read_only=True)
    last_name = serializers.CharField(source='usuario.last_name', read_only=True)
    genero = serializers.CharField(source='usuario.genero', read_only=True)
    activo = serializers.BooleanField(source='usuario.activo', read_only=True)
    roles = serializers.SerializerMethodField(read_only=True)
    curso = CursoSerializer(read_only=True)
    padre_tutor = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Estudiante
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "genero",
            "activo",
            "roles",
            "direccion",
            "fecha_nacimiento",
            "padre_tutor",
            "curso",
        ]
        read_only_fields = ["id"]

    def get_roles(self, obj):
        return [rol.nombre for rol in obj.usuario.roles.all()]

    def get_padre_tutor(self, obj):
        if obj.padre_tutor:
            return {
                "id": obj.padre_tutor.id,
                "nombre": f"{obj.padre_tutor.usuario.first_name} {obj.padre_tutor.usuario.last_name}",
                "parentesco": obj.padre_tutor.parentesco,
            }
        return None


# para no anidar toda la estructura del usuario y consultar que estudiantes estan asociados a un curso
class EstudianteSimpleSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="usuario.first_name")
    last_name = serializers.CharField(source="usuario.last_name")
    genero = serializers.CharField(source="usuario.genero")
    curso = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Estudiante
        fields = ["id", "first_name", "last_name", "genero", "fecha_nacimiento", "curso"]

    def get_curso(self, obj):
        if obj.curso:
            return {
                "id": obj.curso.id,
                "nombre": obj.curso.nombre,
                "turno": obj.curso.turno
            }
        return None


class DocenteSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True, required=False)
    first_name = serializers.CharField(write_only=True, required=False)
    last_name = serializers.CharField(write_only=True, required=False)
    genero = serializers.CharField(write_only=True, required=False)
    activo = serializers.BooleanField(write_only=True, required=False)
    roles = serializers.SerializerMethodField(read_only=True)
    password = serializers.CharField(write_only=True, required=True)
    especialidad = serializers.CharField(required=True)

    class Meta:
        model = Docente
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "genero",
            "activo",
            "roles",
            "password",
            "especialidad",
        ]
        read_only_fields = ["id", "roles"]

    def get_roles(self, obj):
        return [rol.nombre for rol in obj.usuario.roles.all()]

    def create(self, validated_data):
        especialidad = validated_data.pop("especialidad")
        password = validated_data.pop("password")

        user = Usuario(**validated_data)
        user.set_password(password)
        user.save()

        rol_docente = Rol.objects.get(nombre="DOCENTE")
        user.roles.add(rol_docente)

        docente = Docente.objects.create(usuario=user, especialidad=especialidad)

        return docente

    def to_representation(self, instance):
        if isinstance(instance, Usuario):
            try:
                docente = Docente.objects.get(usuario=instance)
            except Docente.DoesNotExist:
                return super().to_representation(instance)
        else:
            docente = instance
        data = super().to_representation(docente)
        data["email"] = docente.usuario.email
        data["first_name"] = docente.usuario.first_name
        data["last_name"] = docente.usuario.last_name
        data["genero"] = docente.usuario.genero
        data["activo"] = docente.usuario.activo
        data["roles"] = [rol.nombre for rol in docente.usuario.roles.all()]
        data["especialidad"] = docente.especialidad
        return data


class PadreTutorSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True, required=False)
    first_name = serializers.CharField(write_only=True, required=False)
    last_name = serializers.CharField(write_only=True, required=False)
    genero = serializers.CharField(write_only=True, required=False)
    activo = serializers.BooleanField(write_only=True, required=False)
    roles = serializers.SerializerMethodField(read_only=True)
    estudiantes = serializers.SerializerMethodField(read_only=True)
    password = serializers.CharField(write_only=True, required=True)
    parentesco = serializers.CharField(required=True)
    telefono = serializers.CharField(required=True)

    class Meta:
        model = PadreTutor
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "genero",
            "activo",
            "roles",
            "parentesco",
            "telefono",
            "estudiantes",
            "password",
        ]
        read_only_fields = ["id", "roles", "estudiantes"]

    def get_roles(self, obj):
        return [rol.nombre for rol in obj.usuario.roles.all()]

    def get_estudiantes(self, obj):
        estudiantes = obj.estudiantes.all()
        return EstudianteSimpleSerializer(estudiantes, many=True).data

    def create(self, validated_data):
        parentesco = validated_data.pop("parentesco")
        telefono = validated_data.pop("telefono")
        password = validated_data.pop("password")

        user = Usuario(**validated_data)
        user.set_password(password)
        user.save()

        rol_padre = Rol.objects.get(nombre="PADRE_TUTOR")
        user.roles.add(rol_padre)

        padre_tutor = PadreTutor.objects.create(
            usuario=user, parentesco=parentesco, telefono=telefono
        )

        return padre_tutor

    def to_representation(self, instance):
        if isinstance(instance, Usuario):
            try:
                padre_tutor = PadreTutor.objects.get(usuario=instance)
            except PadreTutor.DoesNotExist:
                return super().to_representation(instance)
        else:
            padre_tutor = instance
        data = super().to_representation(padre_tutor)
        data["email"] = padre_tutor.usuario.email
        data["first_name"] = padre_tutor.usuario.first_name
        data["last_name"] = padre_tutor.usuario.last_name
        data["genero"] = padre_tutor.usuario.genero
        data["activo"] = padre_tutor.usuario.activo
        data["roles"] = [rol.nombre for rol in padre_tutor.usuario.roles.all()]
        data["parentesco"] = padre_tutor.parentesco
        data["telefono"] = padre_tutor.telefono
        return data


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["roles"] = [rol.nombre for rol in user.roles.all()]
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Solo devolver el access token y los datos del usuario
        user_data = UsuarioSerializer(self.user).data
        data = {"token": data["access"], "user": user_data}
        return data


class PermisoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permiso
        fields = "__all__"


class RolSerializer(serializers.ModelSerializer):
    permisos = PermisoSerializer(many=True, read_only=True)

    class Meta:
        model = Rol
        fields = ["id", "nombre", "permisos"]


class CrearAdminSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
