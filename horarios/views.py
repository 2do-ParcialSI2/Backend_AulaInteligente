from rest_framework import viewsets
from horarios.models import Horario
from materias.models import MateriaCurso
from horarios.serializers import HorarioSerializer
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from unidecode import unidecode


class HorarioViewSet(viewsets.ModelViewSet):
    queryset = Horario.objects.all()
    serializer_class = HorarioSerializer


# unidecode(dia) quita acentos ("Miércoles" → "Miercoles").
# .capitalize() convierte "miercoles" → "Miercoles" (si así lo guardaste en tu base de datos).
# __iexact en el filtro ignora mayúsculas/minúsculas.


class DiasSemanaChoicesView(APIView):
    def get(self, request):
        dias = [{"value": dia[0], "label": dia[1]} for dia in Horario.DIAS_SEMANA]
        return Response(dias)


class HorariosPorDiaView(APIView):
    def get(self, request, dia):
        dia = unidecode(dia).capitalize()
        # bloques = Horario.objects.filter(dia_semana=dia).order_by("hora_inicio")
        bloques = Horario.objects.filter(dia_semana__iexact=dia).order_by("hora_inicio")
        response = []

        for bloque in bloques:
            mc = bloque.materia_curso
            response.append(
                {
                    "hora_inicio": bloque.hora_inicio.strftime("%H:%M"),
                    "hora_fin": bloque.hora_fin.strftime("%H:%M"),
                    "curso": mc.curso.nombre,
                    "materia": mc.materia.nombre,
                }
            )

        return Response(response)


class HorariosPorMateriaView(APIView):
    def get(self, request, materia_id):
        relaciones = MateriaCurso.objects.filter(materia_id=materia_id)

        response = []

        for relacion in relaciones:
            horarios = Horario.objects.filter(materia_curso=relacion).order_by(
                "dia_semana", "hora_inicio"
            )
            for horario in horarios:
                response.append(
                    {
                        "curso": relacion.curso.nombre,
                        "dia": horario.dia_semana,
                        "hora_inicio": horario.hora_inicio.strftime("%H:%M"),
                        "hora_fin": horario.hora_fin.strftime("%H:%M"),
                    }
                )

        return Response(response)
