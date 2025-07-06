from django.db import migrations


def populate_reference_numbers(apps, schema_editor):
    Student = apps.get_model("students", "Student")
    seq = 0
    for s in Student.objects.order_by("id"):
        seq += 1
        s.reference_number_int = seq
        s.reference_number = f"{seq:05d}"  # 00001 … 99999
        s.save(update_fields=["reference_number_int", "reference_number"])


class Migration(migrations.Migration):

    dependencies = [
        ("students", "0016_student_reference_number_int_and_more"),  # ← اسم 0016 بالضبط
    ]

    operations = [
        migrations.RunPython(
            populate_reference_numbers,
            migrations.RunPython.noop,
        ),
    ]
