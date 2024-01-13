# Generated by Django 4.2.7 on 2024-01-13 02:35

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("furfolio", "0082_remove_chat_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="SupportTicket",
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
                            ("OPEN", "Open"),
                            ("INVESTIGATING", "Investigating"),
                            ("CLOSED", "Closed"),
                        ],
                        default="OPEN",
                        max_length=13,
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        help_text="Summarize your issue with a few words. Must be between 5 and 100 characters.",
                        max_length=100,
                        validators=[django.core.validators.MinLengthValidator(5)],
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        help_text="\n            Please describe your issue in detail.\n            <br>\n            If possible, please answer the following questions:\n            <ul>\n                <li>\n                    What is the issue?\n                </li>\n                <li>\n                    Where can we see this issue? (commission chat, published offers, etc.)\n                </li>\n                <li>\n                    When did the issue happen or start?\n                </li>\n                <li>\n                    Who is involved? (You, another user, a group of users, etc.)\n                </li>\n            </ul>\n            ",
                        max_length=23500,
                        validators=[django.core.validators.MinLengthValidator(47)],
                    ),
                ),
                ("created_date", models.DateTimeField(auto_now_add=True)),
                ("updated_date", models.DateTimeField(auto_now=True)),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
