from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MatriculaViewSet, TipoPagoViewSet, MetodoPagoViewSet

router = DefaultRouter()
router.register(r'matriculas', MatriculaViewSet)
router.register(r'tipopago', TipoPagoViewSet)
router.register(r'metodpago', MetodoPagoViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 