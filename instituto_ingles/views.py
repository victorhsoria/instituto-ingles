# instituto_ingles/views.py
from django.shortcuts import render

def error_403(request, exception=None):
    # Podés personalizar el texto según tu sistema
    context = {
        "titulo": "Acceso denegado",
        "mensaje": "No tenés permiso para ver esta sección.",
        "detalle": "Si pensás que es un error, hablá con el administrador del sistema."
    }
    return render(request, "403.html", context, status=403)
