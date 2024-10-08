# Generated by Django 2.2.11 on 2020-04-05 05:52

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("facility", "0074_auto_20200404_2352"),
    ]

    operations = [
        migrations.AlterField(
            model_name="dailyround",
            name="additional_symptoms",
            field=models.CharField(
                blank=True,
                choices=[
                    (1, "ASYMPTOMATIC"),
                    (2, "FEVER"),
                    (3, "SORE THROAT"),
                    (4, "COUGH"),
                    (5, "BREATHLESSNESS"),
                    (6, "MYALGIA"),
                    (7, "ABDOMINAL DISCOMFORT"),
                    (8, "VOMITING/DIARRHOEA"),
                    (9, "OTHERS"),
                    (10, "SARI"),
                ],
                default=1,
                max_length=20,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="patientconsultation",
            name="symptoms",
            field=models.CharField(
                blank=True,
                choices=[
                    (1, "ASYMPTOMATIC"),
                    (2, "FEVER"),
                    (3, "SORE THROAT"),
                    (4, "COUGH"),
                    (5, "BREATHLESSNESS"),
                    (6, "MYALGIA"),
                    (7, "ABDOMINAL DISCOMFORT"),
                    (8, "VOMITING/DIARRHOEA"),
                    (9, "OTHERS"),
                    (10, "SARI"),
                ],
                default=1,
                max_length=20,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="patientteleconsultation",
            name="symptoms",
            field=models.CharField(
                choices=[
                    (1, "ASYMPTOMATIC"),
                    (2, "FEVER"),
                    (3, "SORE THROAT"),
                    (4, "COUGH"),
                    (5, "BREATHLESSNESS"),
                    (6, "MYALGIA"),
                    (7, "ABDOMINAL DISCOMFORT"),
                    (8, "VOMITING/DIARRHOEA"),
                    (9, "OTHERS"),
                    (10, "SARI"),
                ],
                max_length=20,
            ),
        ),
    ]
