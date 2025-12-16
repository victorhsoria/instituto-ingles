# Instituto de Inglés – Sistema de gestión

Aplicación web en **Django** para administrar un instituto de inglés:  
gestión de alumnos, control de pagos, calificaciones y reportes, usando **SQLite** como base de datos.

---

## 🚀 Funcionalidades principales

- 🧑‍🎓 **Alumnos**
  - Alta, edición, baja y listado de alumnos.
  - Datos básicos: nombre, DNI, curso, teléfono, dirección, correo, fecha de inscripción, padre/tutor.
  - Filtros por curso y búsqueda por nombre/apellido/DNI.
  - Paginación y diseño responsive con Bootstrap.

- 💸 **Pagos**
  - Registro de pagos por alumno.
  - Conceptos de pago con opciones fijas: **Mensualidad, Materiales, Examen, Inscripción**.
  - Mes / período correspondiente (ej: “Noviembre 2025”).
  - Listado de pagos con filtros por:
    - Alumno
    - Mes
    - Rango de fechas
  - Edición y eliminación de pagos.
  - Reporte general de pagos por mes y por curso, con gráficos (Chart.js).

- 📊 **Reportes**
  - **Alumnos sin pago** por mes y año, con:
    - Filtro por nombre / apellido / DNI
    - Botón rápido para registrar pago
    - Exportación a **CSV**
  - **Reporte de pagos**:
    - Total general cobrado
    - Totales por mes
    - Totales por curso
    - Exportación a **CSV**

- 📝 **Calificaciones**
  - Registro de calificaciones por alumno.
  - Campo “materia/examen” (ej: *Midterm Speaking B1*).
  - Fecha de examen.
  - Nota en escala **1 a 10** (con decimales).
  - Edición y eliminación de calificaciones.
  - En el detalle del alumno:
    - Lista de todas las calificaciones.
    - **Promedio general** con código de colores:
      - Verde: nota ≥ 8  
      - Amarillo: 6–7.9  
      - Rojo: < 6  

- 🏠 **Dashboard de inicio**
  - Número de alumnos registrados.
  - Resumen de pagos del mes.
  - Estado general de pagos (alumnos con/sin pago).
  - Últimos pagos registrados.

- 🔐 **Autenticación y permisos**
  - Login / logout con usuarios de Django.
  - Restricción de acceso a las vistas (decoradores `login_required` y `permission_required`).
  - Sin uso de Django Admin para la gestión diaria (toda la UI es personalizada).

---

## 🛠️ Tecnologías usadas

- **Python** (3.x)
- **Django**
- **SQLite** (base de datos por defecto)
- **Bootstrap 5** (interfaz)
- **Bootstrap Icons**
- **Chart.js** (gráficos en reportes)
- Sistema de mensajes de Django (feedback al usuario al crear/editar/borrar).

---

## 📂 Estructura principal del proyecto

```text
instituto_ingles/
├── alumnos/                # App principal: modelos, vistas, formularios, URLs
├── instituto_ingles/       # Configuración del proyecto Django
├── templates/              # Templates base (home, login, 403, etc.)
├── manage.py
└── db.sqlite3 (ignorado en Git)
