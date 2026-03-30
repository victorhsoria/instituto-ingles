from django.db import migrations, models


def unificar_crash(apps, schema_editor):
    Alumno = apps.get_model("alumnos", "Alumno")
    Alumno.objects.filter(curso="CRASH_2").update(curso="CRASH_1")


class Migration(migrations.Migration):

    dependencies = [
        ("alumnos", "0005_alter_calificacion_calificacion_obtenida"),
    ]

    operations = [
        migrations.RunPython(unificar_crash, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="alumno",
            name="curso",
            field=models.CharField(
                max_length=30,
                choices=[
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
                    ("CRASH_1", "CRASH 1 - 2"),
                    ("CRASH_3_4", "CRASH 3 - 4"),
                ],
            ),
        ),
    ]