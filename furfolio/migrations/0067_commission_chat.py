# Generated by Django 4.2.7 on 2024-01-02 01:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("furfolio", "0066_chat_alter_offer_cutoff_date_chatparticipant_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="commission",
            name="chat",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="furfolio.chat",
            ),
        ),
    ]
