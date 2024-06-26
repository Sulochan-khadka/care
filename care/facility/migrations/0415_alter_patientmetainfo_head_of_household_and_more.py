# Generated by Django 4.2.10 on 2024-02-20 13:26

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("facility", "0414_remove_bed_old_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="patientmetainfo",
            name="head_of_household",
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="patientmetainfo",
            name="occupation",
            field=models.IntegerField(
                blank=True,
                choices=[
                    (1, "STUDENT"),
                    (2, "BUSINESSMAN"),
                    (3, "HEALTH_CARE_WORKER"),
                    (4, "HEALTH_CARE_LAB_WORKER"),
                    (5, "ANIMAL_HANDLER"),
                    (6, "OTHERS"),
                ],
                null=True,
            ),
        ),
    ]
