# Generated by Django 2.2.11 on 2020-04-04 18:22

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("facility", "0073_auto_20200404_2303"),
    ]

    operations = [
        migrations.AddField(
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
                ],
                default=1,
                max_length=17,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="dailyround",
            name="current_health",
            field=models.IntegerField(
                blank=True,
                choices=[
                    (0, "NO DATA"),
                    (1, "REQUIRES VENTILATOR"),
                    (2, "WORSE"),
                    (3, "STATUS QUO"),
                    (4, "BETTER"),
                ],
                default=0,
            ),
        ),
        migrations.AddField(
            model_name="dailyround",
            name="other_symptoms",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="dailyround",
            name="patient_category",
            field=models.CharField(
                blank=True,
                choices=[
                    ("Mild", "Category-A"),
                    ("Moderate", "Category-B"),
                    ("Severe", "Category-C"),
                    (None, "UNCLASSIFIED"),
                ],
                default=None,
                max_length=8,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="dailyround",
            name="recommend_discharge",
            field=models.BooleanField(
                default=False, verbose_name="Recommend Discharging Patient"
            ),
        ),
    ]
