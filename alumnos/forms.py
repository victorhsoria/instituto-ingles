from django import forms
from .models import Alumno, Pago, Calificacion


class AlumnoForm(forms.ModelForm):
    class Meta:
        model = Alumno
        fields = [
            "nombre",
            "apellido",
            "dni",
            "fecha_nacimiento",
            "padre_o_tutor",
            "telefono",
            "direccion",
            "curso",
        ]
        labels = {
            "nombre": "Nombre",
            "apellido": "Apellido",
            "dni": "DNI",
            "fecha_nacimiento": "Fecha de nacimiento",
            "padre_o_tutor": "Padre / Tutor",
            "telefono": "Teléfono",
            "direccion": "Dirección",
            "curso": "Curso",
        }
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "apellido": forms.TextInput(attrs={"class": "form-control"}),
            "dni": forms.TextInput(attrs={"class": "form-control"}),
            "fecha_nacimiento": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "padre_o_tutor": forms.TextInput(attrs={"class": "form-control"}),
            "telefono": forms.TextInput(attrs={"class": "form-control"}),
            "direccion": forms.TextInput(attrs={"class": "form-control"}),
            "curso": forms.Select(attrs={"class": "form-select"}),
        }

    def clean_dni(self):
        dni = self.cleaned_data.get("dni")
        if not dni:
            return dni

        # Sacamos puntos/espacios para validación básica
        dni_normalizado = "".join(c for c in dni if c.isdigit())
        if len(dni_normalizado) < 7:
            raise forms.ValidationError(
                "El DNI parece demasiado corto, revisalo por favor."
            )

        # Verificar que no esté repetido (excepto el propio alumno si estamos editando)
        qs = Alumno.objects.filter(dni=dni)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Ya existe un alumno con ese DNI.")

        return dni


class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ["alumno", "mes", "fecha_pago", "monto", "observaciones"]
        labels = {
            "alumno": "Alumno",
            "mes": "Mes",
            "fecha_pago": "Fecha de pago",
            "monto": "Monto",
            "observaciones": "Observaciones",
        }
        widgets = {
            "alumno": forms.Select(attrs={"class": "form-select"}),
            "mes": forms.Select(attrs={"class": "form-select"}),
            "fecha_pago": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "monto": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0"}
            ),
            "observaciones": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
        }

    def clean_monto(self):
        monto = self.cleaned_data.get("monto")
        if monto is not None and monto <= 0:
            raise forms.ValidationError("El monto debe ser mayor a 0.")
        return monto

    def clean(self):
        cleaned_data = super().clean()
        alumno = cleaned_data.get("alumno")
        mes = cleaned_data.get("mes")
        fecha_pago = cleaned_data.get("fecha_pago")

        if alumno and mes and fecha_pago:
            pagos_iguales = Pago.objects.filter(
                alumno=alumno,
                mes=mes,
                fecha_pago__year=fecha_pago.year,
            )

            # Si es edición, excluir el propio registro
            if self.instance.pk:
                pagos_iguales = pagos_iguales.exclude(pk=self.instance.pk)

            if pagos_iguales.exists():
                nombre_mes = dict(Pago.MESES_CHOICES).get(mes, mes)
                self.add_error(
                    "mes",
                    f"Ya cargaste un pago para {alumno} en {nombre_mes} {fecha_pago.year}.",
                )

        return cleaned_data


class CalificacionForm(forms.ModelForm):
    class Meta:
        model = Calificacion
        fields = ["alumno", "materia_examen", "fecha_examen", "calificacion_obtenida"]
        labels = {
            "alumno": "Alumno",
            "materia_examen": "Materia / examen",
            "fecha_examen": "Fecha del examen",
            "calificacion_obtenida": "Calificación (0 a 100)",
        }
        widgets = {
            "alumno": forms.Select(attrs={"class": "form-select"}),
            "materia_examen": forms.TextInput(attrs={"class": "form-control"}),
            "fecha_examen": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "calificacion_obtenida": forms.NumberInput(
                attrs={"class": "form-control", "min": 0, "max": 100}
            ),
        }

    def clean_calificacion_obtenida(self):
        nota = self.cleaned_data.get("calificacion_obtenida")
        if nota is None:
            return nota
        if nota < 0 or nota > 100:
            raise forms.ValidationError("La calificación debe estar entre 0 y 100.")
        return nota

class CalificacionForm(forms.ModelForm):
    class Meta:
        model = Calificacion
        fields = ["alumno", "materia_examen", "fecha_examen", "calificacion_obtenida"]
        labels = {
            "alumno": "Alumno",
            "materia_examen": "Materia / examen",
            "fecha_examen": "Fecha del examen",
            "calificacion_obtenida": "Calificación (1 a 10)",
        }
        widgets = {
            "alumno": forms.Select(attrs={"class": "form-select"}),
            "materia_examen": forms.TextInput(attrs={"class": "form-control"}),
            "fecha_examen": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "calificacion_obtenida": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                    "max": 10,
                    "step": "0.1",   # 👈 permite 7.5, 8.3, etc.
                }
            ),
        }

    def clean_calificacion_obtenida(self):
        nota = self.cleaned_data.get("calificacion_obtenida")
        if nota is None:
            return nota
        # Por si acaso, validamos igual acá:
        if nota < 1 or nota > 10:
            raise forms.ValidationError("La calificación debe estar entre 1 y 10.")
        return nota
