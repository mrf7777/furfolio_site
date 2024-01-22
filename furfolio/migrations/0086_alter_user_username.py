# Generated by Django 4.2.7 on 2024-01-22 19:10

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("furfolio", "0085_alter_user_username"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="username",
            field=models.CharField(
                help_text="\n            This is how you will be refered to on this website.\n            <ul>\n                <li>The maximum length is 42 characters</li>\n                <li>Usernames may contain alphanumeric, _, @, +, . and - characters.</li>\n            </ul>\n            ",
                max_length=42,
                unique=True,
            ),
        ),
    ]
