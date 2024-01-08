# Generated by Django 4.2.7 on 2024-01-02 02:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("furfolio", "0068_delete_commissionmessage"),
    ]

    operations = [
        migrations.AlterField(
            model_name="commission",
            name="chat",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="furfolio.chat",
            ),
        ),
    ]