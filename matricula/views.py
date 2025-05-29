from django.shortcuts import render
from rest_framework import viewsets
from .models import Matricula, TipoPago
from .serializers import MatriculaSerializer, TipoPagoSerializer

# Create your views here.

class MatriculaViewSet(viewsets.ModelViewSet):
    queryset = Matricula.objects.all()
    serializer_class = MatriculaSerializer

class TipoPagoViewSet(viewsets.ModelViewSet):
    queryset = TipoPago.objects.all()
    serializer_class = TipoPagoSerializer
