from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum, Q, Avg

from django.contrib.auth.decorators import login_required, permission_required
from django.utils import timezone

from .models import Alumno, Pago
from .forms import AlumnoForm, PagoForm
from django.http import HttpResponse  
import json
from django.core.paginator import Paginator
import csv
from .models import Alumno, Pago, Calificacion
from .forms import AlumnoForm, PagoForm, CalificacionForm
from django.contrib import messages
import csv  # asegúrate de tener esto arriba del archivo







@login_required
def home(request):
    hoy = timezone.now().date()
    year = hoy.year
    mes_num = hoy.month  # 1–12

    # Totales básicos
    total_alumnos = Alumno.objects.count()
    total_pagos = Pago.objects.count()

    # Pagos del mes actual (según fecha de pago)
    pagos_mes_qs = Pago.objects.filter(
        fecha_pago__year=year,
        fecha_pago__month=mes_num,
    )
    total_pagos_mes = pagos_mes_qs.count()
    total_monto_mes = pagos_mes_qs.aggregate(total=Sum("monto"))["total"] or 0

    # Alumnos que pagaron este mes
    alumnos_con_pago_mes = (
        Alumno.objects.filter(
            pagos__fecha_pago__year=year,
            pagos__fecha_pago__month=mes_num,
        )
        .distinct()
        .count()
    )

    alumnos_sin_pago_mes = max(total_alumnos - alumnos_con_pago_mes, 0)

    # Últimos pagos registrados
    ultimos_pagos = (
        Pago.objects.select_related("alumno")
        .order_by("-fecha_pago")[:5]
    )

    # Nombre del mes actual usando las choices del modelo
    mes_label = ""
    try:
        mes_label = Pago.MESES_CHOICES[mes_num - 1][1]
    except IndexError:
        mes_label = ""

    context = {
        "total_alumnos": total_alumnos,
        "total_pagos": total_pagos,
        "total_pagos_mes": total_pagos_mes,
        "total_monto_mes": total_monto_mes,
        "alumnos_sin_pago_mes": alumnos_sin_pago_mes,
        "alumnos_con_pago_mes": alumnos_con_pago_mes,
        "ultimos_pagos": ultimos_pagos,
        "mes_actual_label": mes_label,
        "hoy": hoy,
    }
    return render(request, "home.html", context)



# ---------- ALUMNOS ----------

@login_required
@permission_required("alumnos.view_alumno", raise_exception=True)
def lista_alumnos(request):
    curso = request.GET.get("curso", "")
    q = request.GET.get("q", "")

    # Query base
    alumnos_qs = Alumno.objects.all()

    if curso:
        alumnos_qs = alumnos_qs.filter(curso=curso)

    if q:
        alumnos_qs = alumnos_qs.filter(
            Q(nombre__icontains=q)
            | Q(apellido__icontains=q)
            | Q(dni__icontains=q)
        )

    # Orden (opcional pero recomendable)
    alumnos_qs = alumnos_qs.order_by("apellido", "nombre")

    # ---- PAGINACIÓN ----
    paginator = Paginator(alumnos_qs, 20)  # 20 alumnos por página
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Armamos el querystring sin el parámetro "page" para conservar filtros
    params = request.GET.copy()
    if "page" in params:
        params.pop("page")
    querystring = params.urlencode()

    cursos = Alumno.CURSOS_CHOICES

    context = {
        "alumnos": page_obj.object_list,   # lista de esa página
        "cursos": cursos,
        "curso_seleccionado": curso,
        "q": q,
        "page_obj": page_obj,
        "querystring": querystring,
    }
    return render(request, "alumnos/lista_alumnos.html", context)


@login_required
@permission_required("alumnos.add_alumno", raise_exception=True)
def crear_alumno(request):
    if request.method == "POST":
        form = AlumnoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Alumno creado correctamente.")

            return redirect("lista_alumnos")
    else:
        form = AlumnoForm()
    return render(
        request,
        "alumnos/form_alumno.html",
        {"form": form, "titulo": "Nuevo alumno"},
    )


@login_required
@permission_required("alumnos.change_alumno", raise_exception=True)
def editar_alumno(request, pk):
    alumno = get_object_or_404(Alumno, pk=pk)
    if request.method == "POST":
        form = AlumnoForm(request.POST, instance=alumno)
        if form.is_valid():
            form.save()
            messages.success(request, "Alumno creado correctamente.")

            return redirect("lista_alumnos")
    else:
        form = AlumnoForm(instance=alumno)
    return render(
        request,
        "alumnos/form_alumno.html",
        {"form": form, "titulo": "Editar alumno"},
    )


@login_required
@permission_required("alumnos.delete_alumno", raise_exception=True)
def eliminar_alumno(request, pk):
    alumno = get_object_or_404(Alumno, pk=pk)
    if request.method == "POST":
        nombre = f"{alumno.apellido}, {alumno.nombre}"
        alumno.delete()
        messages.success(request, f"Alumno “{nombre}” eliminado correctamente.")
        return redirect("lista_alumnos")

    return render(request, "alumnos/confirmar_eliminar_alumno.html", {"alumno": alumno})



@login_required
@permission_required("alumnos.view_alumno", raise_exception=True)
def detalle_alumno(request, pk):
    alumno = get_object_or_404(Alumno, pk=pk)

    # Todos los pagos del alumno (para el historial)
    pagos = alumno.pagos.order_by("-fecha_pago")

    # Año actual
    year_actual = timezone.now().year

    # Pagos del año actual para este alumno
    pagos_year = alumno.pagos.filter(fecha_pago__year=year_actual)

    # Meses que ya tienen pago en el año actual (códigos: ENE, FEB, etc.)
    meses_pagados = set(pagos_year.values_list("mes", flat=True))

    # Orden de los meses (1 a 12) para saber qué meses ya vencieron
    mes_orden = {
        codigo: idx
        for idx, (codigo, nombre) in enumerate(Pago.MESES_CHOICES, start=1)
    }

    # Lista con el estado de cada mes del año
    estado_meses = []
    for codigo, nombre in Pago.MESES_CHOICES:
        estado_meses.append(
            {
                "codigo": codigo,
                "nombre": nombre,
                "pagado": codigo in meses_pagados,
            }
        )

    # Mes actual (numérico, 1-12)
    mes_actual_num = timezone.now().month

    # Meses vencidos (hasta el mes actual) que NO tienen pago
    meses_vencidos_sin_pago = [
        m
        for m in estado_meses
        if mes_orden[m["codigo"]] <= mes_actual_num and not m["pagado"]
    ]
    cantidad_meses_adeudados = len(meses_vencidos_sin_pago)

    # Total pagado en el año actual
    total_pagado_year = pagos_year.aggregate(total=Sum("monto"))["total"] or 0

    # Calificaciones del alumno
    calificaciones = Calificacion.objects.filter(alumno=alumno).order_by(
        "-fecha_examen", "-id"
    )

    # Promedio de calificaciones (None si no hay)
    promedio_calificaciones = calificaciones.aggregate(
        prom=Avg("calificacion_obtenida")
    )["prom"]

    context = {
        "alumno": alumno,
        "pagos": pagos,
        "year_actual": year_actual,
        "estado_meses": estado_meses,
        "cantidad_meses_adeudados": cantidad_meses_adeudados,
        "total_pagado_year": total_pagado_year,
        "meses_vencidos_sin_pago": meses_vencidos_sin_pago,
        "calificaciones": calificaciones,
        "promedio_calificaciones": promedio_calificaciones,  # 👈 nuevo
    }
    return render(request, "alumnos/detalle_alumno.html", context)




# ---------- PAGOS ----------

@login_required
@permission_required("alumnos.view_pago", raise_exception=True)
def lista_pagos(request):
    mes = request.GET.get("mes", "")
    q = request.GET.get("q", "")
    desde = request.GET.get("desde", "")
    hasta = request.GET.get("hasta", "")

    pagos_qs = Pago.objects.select_related("alumno").all()

    if mes:
        pagos_qs = pagos_qs.filter(mes=mes)

    if q:
        pagos_qs = pagos_qs.filter(
            Q(alumno__nombre__icontains=q)
            | Q(alumno__apellido__icontains=q)
            | Q(alumno__dni__icontains=q)
        )

    if desde:
        pagos_qs = pagos_qs.filter(fecha_pago__gte=desde)

    if hasta:
        pagos_qs = pagos_qs.filter(fecha_pago__lte=hasta)

    pagos_qs = pagos_qs.order_by("-fecha_pago")
    meses = Pago.MESES_CHOICES

    # 🔹 Paginación
    paginator = Paginator(pagos_qs, 20)  # 20 pagos por página (cambiá el número si querés)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "pagos": page_obj,          # para el for
        "page_obj": page_obj,       # para los links de paginación
        "meses": meses,
        "mes_seleccionado": mes,
        "q": q,
        "desde": desde,
        "hasta": hasta,
    }
    return render(request, "pagos/lista_pagos.html", context)




@login_required
@permission_required("alumnos.add_pago", raise_exception=True)
def crear_pago(request):
    alumno_id = request.GET.get("alumno")
    alumno = None
    initial = {}

    # Si viene desde detalle_alumno, preseleccionamos y guardamos el alumno
    if alumno_id:
        alumno = get_object_or_404(Alumno, pk=alumno_id)
        initial["alumno"] = alumno

    if request.method == "POST":
        form = PagoForm(request.POST)
        if form.is_valid():
            pago = form.save()
            messages.success(request, "Pago registrado correctamente.")
            return redirect("detalle_alumno", pk=pago.alumno.pk)
    else:
        form = PagoForm(initial=initial)

    return render(
        request,
        "pagos/form_pago.html",
        {
            "form": form,
            "titulo": "Nuevo pago",
            "alumno": alumno,  # 👈 para saber a dónde volver en el template
        },
    )




@login_required
@permission_required("alumnos.change_pago", raise_exception=True)
def editar_pago(request, pk):
    pago = get_object_or_404(Pago, pk=pk)
    alumno = pago.alumno  # 👈 siempre hay alumno

    if request.method == "POST":
        form = PagoForm(request.POST, instance=pago)
        if form.is_valid():
            pago = form.save()
            messages.success(request, "Pago actualizado correctamente.")
            return redirect("detalle_alumno", pk=pago.alumno.pk)
    else:
        form = PagoForm(instance=pago)

    return render(
        request,
        "pagos/form_pago.html",
        {
            "form": form,
            "titulo": "Editar pago",
            "alumno": alumno,  # 👈 lo mandamos al template
        },
    )




@login_required
@permission_required("alumnos.delete_pago", raise_exception=True)
def eliminar_pago(request, pk):
    pago = get_object_or_404(Pago, pk=pk)
    alumno_pk = pago.alumno.pk

    if request.method == "POST":
        pago.delete()
        messages.success(request, "Pago eliminado correctamente.")
        return redirect("detalle_alumno", pk=alumno_pk)

    return render(
        request,
        "pagos/confirmar_eliminar_pago.html",
        {"pago": pago},
    )



# ...

@login_required
@permission_required("alumnos.view_pago", raise_exception=True)
def reporte_pagos(request):
    pagos = Pago.objects.select_related("alumno").all()

    # Total por mes
    resumen_por_mes = (
        pagos.values("mes")
        .annotate(total=Sum("monto"))
        .order_by("mes")
    )
    meses_labels = dict(Pago.MESES_CHOICES)
    for fila in resumen_por_mes:
        fila["mes_label"] = meses_labels.get(fila["mes"], fila["mes"])

    # Total por curso
    resumen_por_curso = (
        pagos.values("alumno__curso")
        .annotate(total=Sum("monto"))
        .order_by("alumno__curso")
    )
    cursos_labels = dict(Alumno.CURSOS_CHOICES)
    for fila in resumen_por_curso:
        fila["curso_label"] = cursos_labels.get(
            fila["alumno__curso"], fila["alumno__curso"]
        )

    @login_required
    @permission_required("alumnos.add_pago", raise_exception=True)
    def crear_pago(request):
        alumno_id = request.GET.get("alumno")
        initial = {}

        if alumno_id:
            initial["alumno"] = get_object_or_404(Alumno, pk=alumno_id)

        if request.method == "POST":
            form = PagoForm(request.POST)
            if form.is_valid():
                pago = form.save()
                messages.success(request, "Pago registrado correctamente.")
                return redirect("detalle_alumno", pk=pago.alumno.pk)
        else:
            form = PagoForm(initial=initial)

        return render(
            request,
            "pagos/form_pago.html",
            {"form": form, "titulo": "Nuevo pago"},
        )


    # Total general
    total_general = pagos.aggregate(total=Sum("monto"))["total"] or 0

    # ------ Datos para las gráficas (en JSON) ------
    labels_mes = json.dumps([fila["mes_label"] for fila in resumen_por_mes])
    valores_mes = json.dumps([float(fila["total"]) for fila in resumen_por_mes])

    labels_curso = json.dumps([fila["curso_label"] for fila in resumen_por_curso])
    valores_curso = json.dumps([float(fila["total"]) for fila in resumen_por_curso])

    context = {
        "resumen_por_mes": resumen_por_mes,
        "resumen_por_curso": resumen_por_curso,
        "total_general": total_general,
        "labels_mes": labels_mes,
        "valores_mes": valores_mes,
        "labels_curso": labels_curso,
        "valores_curso": valores_curso,
    }
    return render(request, "reportes/pagos_por_curso_mes.html", context)



from django.db.models import Q  # ya lo tenés importado arriba con Sum

@login_required
@permission_required("alumnos.view_pago", raise_exception=True)
def reporte_alumnos_sin_pago(request):
    mes = request.GET.get("mes", "")
    year = request.GET.get("year", "")
    q = request.GET.get("q", "").strip()  # 🔍 nuevo filtro de búsqueda

    meses = Pago.MESES_CHOICES

    # Año por defecto: actual
    if not year:
        year = str(timezone.now().year)

    alumnos_sin_pago = None  # None = todavía no se filtró

    if mes:
        # Pagos registrados en ese mes y año
        pagos_periodo = Pago.objects.filter(mes=mes, fecha_pago__year=year)

        # IDs de alumnos que sí pagaron
        alumnos_con_pago = pagos_periodo.values_list("alumno_id", flat=True).distinct()

        # Alumnos que NO están en esa lista
        alumnos_sin_pago = (
            Alumno.objects
            .exclude(id__in=alumnos_con_pago)
            .order_by("apellido", "nombre")
        )

        # Si hay texto de búsqueda, filtramos por apellido, nombre o DNI
        if q:
            alumnos_sin_pago = alumnos_sin_pago.filter(
                Q(apellido__icontains=q)
                | Q(nombre__icontains=q)
                | Q(dni__icontains=q)
            )

    context = {
        "alumnos": alumnos_sin_pago,
        "meses": meses,
        "mes_seleccionado": mes,
        "year": year,
        "q": q,  # para que el input recuerde lo buscado
    }
    return render(request, "reportes/alumnos_sin_pago.html", context)


@login_required
@permission_required("alumnos.view_pago", raise_exception=True)
def exportar_reporte_pagos_csv(request):
    pagos = Pago.objects.select_related("alumno").all()

    # --- Totales por mes ---
    resumen_por_mes = (
        pagos.values("mes")
        .annotate(total=Sum("monto"))
        .order_by("mes")
    )
    meses_labels = dict(Pago.MESES_CHOICES)

    # --- Totales por curso ---
    resumen_por_curso = (
        pagos.values("alumno__curso")
        .annotate(total=Sum("monto"))
        .order_by("alumno__curso")
    )
    cursos_labels = dict(Alumno.CURSOS_CHOICES)

    # Total general
    total_general = pagos.aggregate(total=Sum("monto"))["total"] or 0

    # Respuesta CSV
    response = HttpResponse(
        content_type="text/csv; charset=utf-8"
    )
    response["Content-Disposition"] = 'attachment; filename="reporte_pagos_resumen.csv"'

    # BOM para que Excel lo abra bien en Windows
    response.write("\ufeff")

    writer = csv.writer(response, delimiter=";")

    # Sección 1: por mes
    writer.writerow(["Reporte de pagos por MES"])
    writer.writerow(["Mes", "Total"])
    for fila in resumen_por_mes:
        mes_label = meses_labels.get(fila["mes"], fila["mes"])
        writer.writerow([mes_label, f"{fila['total']:.2f}"])

    writer.writerow([])

    # Sección 2: por curso
    writer.writerow(["Reporte de pagos por CURSO"])
    writer.writerow(["Curso", "Total"])
    for fila in resumen_por_curso:
        curso_label = cursos_labels.get(fila["alumno__curso"], fila["alumno__curso"])
        writer.writerow([curso_label, f"{fila['total']:.2f}"])

    writer.writerow([])
    writer.writerow(["Total general", f"{total_general:.2f}"])

    return response


@login_required
@permission_required("alumnos.view_alumno", raise_exception=True)
def exportar_alumnos_sin_pago_csv(request):
    mes = request.GET.get("mes", "")
    year = request.GET.get("year", "")

    if not year:
        year = str(timezone.now().year)

    alumnos_sin_pago = []

    if mes:
        pagos_periodo = Pago.objects.filter(mes=mes, fecha_pago__year=year)
        alumnos_con_pago = pagos_periodo.values_list("alumno_id", flat=True).distinct()

        alumnos_sin_pago = (
            Alumno.objects
            .exclude(id__in=alumnos_con_pago)
            .order_by("apellido", "nombre")
        )

    response = HttpResponse(content_type="text/csv")
    filename = f"alumnos_sin_pago_{mes or 'SIN_MES'}_{year}.csv"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    writer = csv.writer(response, delimiter=";")
    writer.writerow([
        "Apellido",
        "Nombre",
        "DNI",
        "Curso",
        "Padre/Tutor",
        "Teléfono",
        "Dirección",
    ])

    for a in alumnos_sin_pago:
        writer.writerow([
            a.apellido,
            a.nombre,
            a.dni,
            a.get_curso_display(),
            a.padre_o_tutor,
            a.telefono,
            a.direccion,
        ])

    return response




@login_required
@permission_required("alumnos.view_calificacion", raise_exception=True)
def lista_calificaciones(request):
    q = request.GET.get("q", "").strip()

    calificaciones = Calificacion.objects.select_related("alumno")

    if q:
        calificaciones = calificaciones.filter(
            Q(alumno__nombre__icontains=q)
            | Q(alumno__apellido__icontains=q)
            | Q(alumno__dni__icontains=q)
            | Q(materia_examen__icontains=q)
        )

    calificaciones = calificaciones.order_by("-fecha_examen", "-id")

    paginator = Paginator(calificaciones, 25)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "q": q,
    }
    return render(request, "calificaciones/lista_calificaciones.html", context)

@login_required
@permission_required("alumnos.change_calificacion", raise_exception=True)
def editar_calificacion(request, pk):
    calificacion = get_object_or_404(Calificacion, pk=pk)

    if request.method == "POST":
        form = CalificacionForm(request.POST, instance=calificacion)
        if form.is_valid():
            calificacion = form.save()
            return redirect("detalle_alumno", pk=calificacion.alumno.pk)
    else:
        form = CalificacionForm(instance=calificacion)

    return render(
        request,
        "calificaciones/form_calificacion.html",
        {"form": form, "titulo": "Editar calificación"},
    )

@login_required
@permission_required("alumnos.delete_calificacion", raise_exception=True)
def eliminar_calificacion(request, pk):
    calificacion = get_object_or_404(Calificacion, pk=pk)
    alumno_pk = calificacion.alumno.pk

    if request.method == "POST":
        calificacion.delete()
        return redirect("detalle_alumno", pk=alumno_pk)

    return render(
        request,
        "calificaciones/confirmar_eliminar_calificacion.html",
        {"calificacion": calificacion},
    )

# ---------- CALIFICACIONES ----------

@login_required
@permission_required("alumnos.view_calificacion", raise_exception=True)
def lista_calificaciones(request):
    q = request.GET.get("q", "").strip()

    calificaciones_qs = Calificacion.objects.select_related("alumno").all()

    if q:
        calificaciones_qs = calificaciones_qs.filter(
            Q(alumno__nombre__icontains=q)
            | Q(alumno__apellido__icontains=q)
            | Q(alumno__dni__icontains=q)
            | Q(materia_examen__icontains=q)
        )

    calificaciones_qs = calificaciones_qs.order_by("-fecha_examen", "-id")

    paginator = Paginator(calificaciones_qs, 25)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "q": q,
    }
    return render(request, "calificaciones/lista_calificaciones.html", context)


@login_required
@permission_required("alumnos.add_calificacion", raise_exception=True)
def crear_calificacion(request):
    alumno_id = request.GET.get("alumno")
    alumno = None
    initial = {}

    if alumno_id:
        alumno = get_object_or_404(Alumno, pk=alumno_id)
        initial["alumno"] = alumno

    if request.method == "POST":
        form = CalificacionForm(request.POST)
        if form.is_valid():
            calificacion = form.save()
            messages.success(request, "Calificación registrada correctamente.")
            return redirect("detalle_alumno", pk=calificacion.alumno.pk)
    else:
        form = CalificacionForm(initial=initial)

    return render(
        request,
        "calificaciones/form_calificacion.html",
        {
            "form": form,
            "titulo": "Nueva calificación",
            "alumno": alumno,
        },
    )




@login_required
@permission_required("alumnos.change_calificacion", raise_exception=True)
def editar_calificacion(request, pk):
    calificacion = get_object_or_404(Calificacion, pk=pk)
    alumno = calificacion.alumno

    if request.method == "POST":
        form = CalificacionForm(request.POST, instance=calificacion)
        if form.is_valid():
            calificacion = form.save()
            messages.success(request, "Calificación actualizada correctamente.")
            return redirect("detalle_alumno", pk=calificacion.alumno.pk)
    else:
        form = CalificacionForm(instance=calificacion)

    return render(
        request,
        "calificaciones/form_calificacion.html",
        {
            "form": form,
            "titulo": "Editar calificación",
            "alumno": alumno,
        },
    )




@login_required
@permission_required("alumnos.delete_calificacion", raise_exception=True)
def eliminar_calificacion(request, pk):
    calificacion = get_object_or_404(Calificacion, pk=pk)
    alumno_pk = calificacion.alumno.pk

    if request.method == "POST":
        calificacion.delete()
        messages.success(request, "Calificación eliminada correctamente.")
        return redirect("detalle_alumno", pk=alumno_pk)

    return render(
        request,
        "calificaciones/confirmar_eliminar_calificacion.html",
        {"calificacion": calificacion},
    )


