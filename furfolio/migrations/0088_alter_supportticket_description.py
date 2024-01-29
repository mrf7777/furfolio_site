# Generated by Django 4.2.7 on 2024-01-29 01:36

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("furfolio", "0087_auto_20240129_0030"),
    ]

    operations = [
        migrations.AlterField(
            model_name="supportticket",
            name="description",
            field=models.TextField(
                help_text="\n            Please describe your issue in detail.\n            <br>\n            If possible, please answer as many of the following questions as possible:\n            <ul>\n                <li>\n                    What is the issue?\n                </li>\n                <li>\n                    Where can we see this issue? Add a URL or a link. (commission chat, published offers, etc.)\n                </li>\n                <li>\n                    When did the issue happen or start?\n                </li>\n                <li>\n                    Who is involved? (You, another user, a group of users, etc.)\n                </li>\n                <li>\n                    How did the issue happen?\n                </li>\n            </ul>\n            ",
                max_length=23500,
                validators=[django.core.validators.MinLengthValidator(47)],
            ),
        ),
    ]
