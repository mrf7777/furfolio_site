# Generated by Django 4.2.7 on 2024-01-08 02:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("furfolio", "0071_notification_chatmessagenotification"),
    ]

    operations = [
        migrations.AddField(
            model_name="notification",
            name="seen",
            field=models.BooleanField(default=False),
        ),
    ]