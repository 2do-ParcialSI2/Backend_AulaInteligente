from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MatriculaViewSet, TipoPagoViewSet

router = DefaultRouter()
router.register(r'matriculas', MatriculaViewSet)
router.register(r'tipopago', TipoPagoViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 