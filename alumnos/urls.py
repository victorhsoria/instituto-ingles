from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),

    # ALUMNOS
    path("alumnos/", views.lista_alumnos, name="lista_alumnos"),
    path("alumnos/nuevo/", views.crear_alumno, name="crear_alumno"),
    path("alumnos/<int:pk>/", views.detalle_alumno, name="detalle_alumno"),
    path("alumnos/<int:pk>/editar/", views.editar_alumno, name="editar_alumno"),
    path("alumnos/<int:pk>/eliminar/", views.eliminar_alumno, name="eliminar_alumno"),

    # PAGOS
    path("pagos/", views.lista_pagos, name="lista_pagos"),
    path("pagos/nuevo/", views.crear_pago, name="crear_pago"),
    path("pagos/<int:pk>/editar/", views.editar_pago, name="editar_pago"),
    path("pagos/<int:pk>/eliminar/", views.eliminar_pago, name="eliminar_pago"),

    # REPORTES
    path("reportes/pagos/", views.reporte_pagos, name="reporte_pagos"),
    path(
        "reportes/pagos/csv/",
        views.exportar_reporte_pagos_csv,
        name="exportar_reporte_pagos_csv",
    ),

    path(
        "reportes/alumnos-sin-pago/",
        views.reporte_alumnos_sin_pago,
        name="reporte_alumnos_sin_pago",
    ),
    path(
        "reportes/alumnos-sin-pago/csv/",
        views.exportar_alumnos_sin_pago_csv,
        name="exportar_alumnos_sin_pago_csv",
    ),

    # opcional: índice general de reportes
    # path("reportes/", views.reportes, name="reportes"),

        # CALIFICACIONES
    path("calificaciones/", views.lista_calificaciones, name="lista_calificaciones"),
    path("calificaciones/nueva/", views.crear_calificacion, name="crear_calificacion"),
    path(
        "calificaciones/<int:pk>/editar/",
        views.editar_calificacion,
        name="editar_calificacion",
    ),
    path(
        "calificaciones/<int:pk>/eliminar/",
        views.eliminar_calificacion,
        name="eliminar_calificacion",
    ),

]
