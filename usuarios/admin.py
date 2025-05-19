from django.contrib import admin
from .models import Usuario, Estudiante, Docente, PadreTutor, Rol, Permiso

admin.site.register(Usuario)
admin.site.register(Estudiante)
admin.site.register(Docente)
admin.site.register(PadreTutor)
admin.site.register(Rol)
admin.site.register(Permiso)
