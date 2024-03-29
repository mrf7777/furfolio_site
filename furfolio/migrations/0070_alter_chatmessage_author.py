# Generated by Django 4.2.7 on 2024-01-02 02:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("furfolio", "0069_alter_commission_chat"),
    ]

    operations = [
        migrations.AlterField(
            model_name="chatmessage",
            name="author",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
