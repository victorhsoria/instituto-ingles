from django.contrib import admin
from .models import Alumno, Pago


@admin.register(Alumno)
class AlumnoAdmin(admin.ModelAdmin):
    list_display = ("apellido", "nombre", "dni", "curso", "telefono")
    search_fields = ("nombre", "apellido", "dni", "padre_o_tutor", "telefono")
    list_filter = ("curso",)


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ("alumno", "mes", "fecha_pago", "monto")
    list_filter = ("mes", "fecha_pago", "alumno")
    search_fields = ("alumno__nombre", "alumno__apellido", "alumno__dni")
