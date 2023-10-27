# Generated by Django 4.2.4 on 2023-10-27 22:07

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("furfolio", "0051_offer_max_commissions_per_user"),
    ]

    operations = [
        migrations.AlterField(
            model_name="offer",
            name="max_review_commissions",
            field=models.PositiveIntegerField(
                default=5,
                help_text="The maximum number of commissions allowed to be in the review state.<br>Use this to prevent being overloaded with too many commission requests at a time for this offer.",
                validators=[django.core.validators.MinValueValidator(1)],
                verbose_name="Maximum Commissions in Review",
            ),
        ),
    ]
