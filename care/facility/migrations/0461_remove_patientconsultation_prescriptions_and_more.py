# Generated by Django 4.2.10 on 2024-08-29 16:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("facility", "0460_alter_dailyround_bp_alter_dailyround_feeds_and_more"),
    ]

    def forward_investigations_dict_to_array(apps, schema_editor):
        PatientConsultation = apps.get_model("facility", "PatientConsultation")
        PatientConsultation.objects.filter(investigation={}).update(investigation=[])

    operations = [
        migrations.RemoveField(
            model_name="patientconsultation",
            name="prescriptions",
        ),
        migrations.RemoveField(
            model_name="dailyround",
            name="medication_given",
        ),
        migrations.AlterField(
            model_name="patientconsultation",
            name="investigation",
            field=models.JSONField(default=list),
        ),
        migrations.RunPython(
            forward_investigations_dict_to_array,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
