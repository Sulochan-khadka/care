# Generated by Django 2.2.11 on 2023-02-22 14:42

import care.utils.models.validators
import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("hcx", "0003_auto_20230217_1901"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="claim",
            name="procedures",
        ),
        migrations.AddField(
            model_name="claim",
            name="items",
            field=django.contrib.postgres.fields.jsonb.JSONField(
                default=list,
                validators=[
                    care.utils.models.validators.JSONFieldSchemaValidator(
                        {
                            "$schema": "http://json-schema.org/draft-07/schema#",
                            "items": [
                                {
                                    "additionalProperties": False,
                                    "category": "string",
                                    "properties": {
                                        "id": {"type": "string"},
                                        "name": {"type": "string"},
                                        "price": {"type": "number"},
                                    },
                                    "required": ["id", "name", "price"],
                                    "type": "object",
                                }
                            ],
                            "type": "array",
                        }
                    )
                ],
            ),
        ),
    ]