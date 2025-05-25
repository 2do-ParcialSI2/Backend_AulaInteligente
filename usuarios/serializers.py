from rest_framework import serializers
from .models import Usuario, Estudiante, Docente, PadreTutor, Rol, Permiso
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from cursos.serializers import CursoSerializer


class UsuarioSerializer(serializers.ModelSerializer):
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


class EstudianteSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True, required=False)
    first_name = serializers.CharField(write_only=True, required=False)
    last_name = serializers.CharField(write_only=True, required=False)
    genero = serializers.CharField(write_only=True, required=False)
    activo = serializers.BooleanField(write_only=True, required=False)
    roles = serializers.SerializerMethodField(read_only=True)
    password = serializers.CharField(write_only=True, required=True)
    direccion = serializers.CharField(required=True)
    fecha_nacimiento = serializers.DateField(required=True)
    padre_tutor_id = serializers.IntegerField(write_only=True, required=False)
    curso = CursoSerializer(read_only=True)

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
            "password",
            "direccion",
            "fecha_nacimiento",
            "padre_tutor_id",
            "curso",
        ]
        read_only_fields = ["id", "roles"]

    def get_roles(self, obj):
        return [rol.nombre for rol in obj.usuario.roles.all()]

    def create(self, validated_data):
        direccion = validated_data.pop("direccion")
        fecha_nacimiento = validated_data.pop("fecha_nacimiento")
        padre_tutor_id = validated_data.pop("padre_tutor_id", None)
        password = validated_data.pop("password")

        user = Usuario(**validated_data)
        user.set_password(password)
        user.save()

        rol_estudiante = Rol.objects.get(nombre="ESTUDIANTE")
        user.roles.add(rol_estudiante)

        estudiante = Estudiante.objects.create(
            usuario=user, direccion=direccion, fecha_nacimiento=fecha_nacimiento
        )

        if padre_tutor_id:
            try:
                padre_tutor = PadreTutor.objects.get(id=padre_tutor_id)
                estudiante.padre_tutor = padre_tutor
                estudiante.save()
            except PadreTutor.DoesNotExist:
                pass

        return user

    def to_representation(self, instance):
        if isinstance(instance, Usuario):
            try:
                estudiante = Estudiante.objects.get(usuario=instance)
            except Estudiante.DoesNotExist:
                return super().to_representation(instance)
        else:
            estudiante = instance
        data = super().to_representation(estudiante)
        data["email"] = estudiante.usuario.email
        data["first_name"] = estudiante.usuario.first_name
        data["last_name"] = estudiante.usuario.last_name
        data["genero"] = estudiante.usuario.genero
        data["activo"] = estudiante.usuario.activo
        data["roles"] = [rol.nombre for rol in estudiante.usuario.roles.all()]
        data["direccion"] = estudiante.direccion
        data["fecha_nacimiento"] = estudiante.fecha_nacimiento
        if estudiante.padre_tutor:
            data["padre_tutor"] = {
                "id": estudiante.padre_tutor.id,
                "nombre": f"{estudiante.padre_tutor.usuario.first_name} {estudiante.padre_tutor.usuario.last_name}",
                "parentesco": estudiante.padre_tutor.parentesco,
            }
        else:
            data["padre_tutor"] = None

        if estudiante.curso:
            data["curso"] = CursoSerializer(estudiante.curso).data
        else:
            data["curso"] = None
        return data


# para no anidar toda la estructura del usuario y consultar que estudiantes estan asociados a un curso
class EstudianteSimpleSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="usuario.first_name")
    last_name = serializers.CharField(source="usuario.last_name")
    genero = serializers.CharField(source="usuario.genero")

    class Meta:
        model = Estudiante
        fields = ["id", "first_name", "last_name", "genero", "fecha_nacimiento"]


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
        return [est.id for est in obj.estudiantes.all()]

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
