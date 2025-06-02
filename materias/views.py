from rest_framework import generics
from materias.models import Materia
from materias.serializers import MateriaSerializer


class MateriaListCreateView(generics.ListCreateAPIView):
    queryset = Materia.objects.all()
    serializer_class = MateriaSerializer


class MateriaRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Materia.objects.all()  # No filtramos por activo para mantener historial
    serializer_class = MateriaSerializer

    def perform_destroy(self, instance):
        instance.activo = False
        instance.save()
