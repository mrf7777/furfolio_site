# Generated by Django 4.2.7 on 2024-01-08 23:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("furfolio", "0073_offerpostednotification"),
    ]

    operations = [
        migrations.CreateModel(
            name="CommissionStateNotification",
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
                    "state",
                    models.CharField(
                        choices=[
                            ("REVIEW", "Review"),
                            ("ACCEPTED", "Accepted"),
                            ("IN_PROGRESS", "In Progress"),
                            ("CLOSED", "Finished"),
                            ("REJECTED", "Rejected"),
                        ],
                        max_length=11,
                    ),
                ),
                (
                    "commission",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="furfolio.commission",
                    ),
                ),
                (
                    "notification",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="furfolio.notification",
                    ),
                ),
            ],
        ),
    ]
