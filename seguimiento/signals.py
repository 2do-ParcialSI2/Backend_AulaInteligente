# seguimiento/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Tarea, Participacion, Asistencia, Examen, Seguimiento

def actualizar_nota(seguimiento):
    if seguimiento:
        seguimiento.calcular_nota_trimestral()

@receiver(post_save, sender=Tarea)
@receiver(post_delete, sender=Tarea)
@receiver(post_save, sender=Participacion)
@receiver(post_delete, sender=Participacion)
@receiver(post_save, sender=Asistencia)
@receiver(post_delete, sender=Asistencia)
@receiver(post_save, sender=Examen)
@receiver(post_delete, sender=Examen)
def recalcular_nota(sender, instance, **kwargs):
    actualizar_nota(instance.seguimiento)
