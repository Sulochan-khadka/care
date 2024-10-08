# Generated by Django 4.2.10 on 2024-09-19 12:58

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("facility", "0457_patientmetainfo_domestic_healthcare_support_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="FacilityFlag",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "external_id",
                    models.UUIDField(db_index=True, default=uuid.uuid4, unique=True),
                ),
                (
                    "created_date",
                    models.DateTimeField(auto_now_add=True, db_index=True, null=True),
                ),
                (
                    "modified_date",
                    models.DateTimeField(auto_now=True, db_index=True, null=True),
                ),
                ("deleted", models.BooleanField(db_index=True, default=False)),
                ("flag", models.CharField(max_length=1024)),
                (
                    "facility",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="facility.facility",
                    ),
                ),
            ],
            options={
                "verbose_name": "Facility Flag",
            },
        ),
        migrations.AddConstraint(
            model_name="facilityflag",
            constraint=models.UniqueConstraint(
                condition=models.Q(("deleted", False)),
                fields=("facility", "flag"),
                name="unique_facility_flag",
            ),
        ),
    ]
