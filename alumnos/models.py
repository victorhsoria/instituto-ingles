from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator



class Alumno(models.Model):
    CURSOS_CHOICES = [
        ("PLAY_SCHOOL", "PLAY SCHOOL"),
        ("CHILDREN", "CHILDREN"),
        ("KIDS_1", "KIDS 1"),
        ("KIDS_2", "KIDS 2"),
        ("KIDS_3", "KIDS 3"),
        ("JUNIORS_1", "JUNIORS 1"),
        ("JUNIORS_2", "JUNIORS 2"),
        ("JUNIORS_3", "JUNIORS 3"),
        ("JUNIORS_4", "JUNIORS 4"),
        ("1ST_INTENSIVE", "1st INTENSIVE"),
        ("3RD_INTENSIVE", "3rd INTENSIVE"),
        ("5TH_INTENSIVE", "5th INTENSIVE"),
        ("6TH_INTENSIVE", "6th INTENSIVE"),
        ("7TH_INTENSIVE", "7th INTENSIVE"),
        ("CRASH_1", "CRASH 1"),
        ("CRASH_2", "CRASH 2"),
    ]

    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    dni = models.CharField(max_length=20, unique=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    padre_o_tutor = models.CharField(max_length=100, blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    direccion = models.CharField(max_length=100)
    curso = models.CharField(max_length=30, choices=CURSOS_CHOICES)

    # 🔹 nuevos campos
    correo_electronico = models.EmailField(null=True, blank=True)
    fecha_inscripcion = models.DateField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.apellido}, {self.nombre}"

    @property
    def nombre_completo(self):
        return f"{self.apellido}, {self.nombre}"

class Pago(models.Model):
    MESES_CHOICES = [
        ('ENE', 'Enero'),
        ('FEB', 'Febrero'),
        ('MAR', 'Marzo'),
        ('ABR', 'Abril'),
        ('MAY', 'Mayo'),
        ('JUN', 'Junio'),
        ('JUL', 'Julio'),
        ('AGO', 'Agosto'),
        ('SEP', 'Septiembre'),
        ('OCT', 'Octubre'),
        ('NOV', 'Noviembre'),
        ('DIC', 'Diciembre'),
    ]

    CONCEPTO_PAGO_CHOICES = [
        ('Mensualidad', 'Mensualidad'),
        ('Materiales', 'Materiales'),
        ('Examen', 'Examen'),
        ('Inscripción', 'Inscripción'),
    ]

    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE, related_name='pagos')
    mes = models.CharField(max_length=3, choices=MESES_CHOICES)
    fecha_pago = models.DateField()
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    observaciones = models.TextField(blank=True, null=True)

    # 🔹 nuevos campos
    concepto_pago = models.CharField(
        max_length=20,
        choices=CONCEPTO_PAGO_CHOICES,
        default='Mensualidad',
    )
    mes_correspondiente = models.CharField(
        max_length=30,
        blank=True,
        help_text="Ej: 'Noviembre 2025'. Opcional.",
    )

    def __str__(self):
        return f"{self.alumno} - {self.get_mes_display()} - {self.monto}"




class Calificacion(models.Model):
    alumno = models.ForeignKey(
        Alumno,
        on_delete=models.CASCADE,
        related_name="calificaciones",
    )
    materia_examen = models.CharField(max_length=150)
    fecha_examen = models.DateField()
    calificacion_obtenida = models.DecimalField(
        max_digits=4,          # ej: 10.00, 7.50, 9.75
        decimal_places=2,
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )

    def __str__(self):
        return f"{self.alumno} - {self.materia_examen} ({self.calificacion_obtenida})"