from rest_framework import generics
from materias.models import Materia
from materias.serializers import MateriaSerializer


class MateriaListCreateView(generics.ListCreateAPIView):
    queryset = Materia.objects.all()
    serializer_class = MateriaSerializer


class MateriaRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Materia.objects.all()
    serializer_class = MateriaSerializer
