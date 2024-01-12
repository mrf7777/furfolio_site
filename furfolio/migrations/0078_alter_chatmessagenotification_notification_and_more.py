# Generated by Django 4.2.7 on 2024-01-09 20:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("furfolio", "0077_userfollowednotification"),
    ]

    operations = [
        migrations.AlterField(
            model_name="chatmessagenotification",
            name="notification",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                parent_link=True,
                to="furfolio.notification",
            ),
        ),
        migrations.AlterField(
            model_name="commissioncreatednotification",
            name="notification",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                parent_link=True,
                to="furfolio.notification",
            ),
        ),
        migrations.AlterField(
            model_name="commissionstatenotification",
            name="notification",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                parent_link=True,
                to="furfolio.notification",
            ),
        ),
        migrations.AlterField(
            model_name="offerpostednotification",
            name="notification",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                parent_link=True,
                to="furfolio.notification",
            ),
        ),
        migrations.AlterField(
            model_name="userfollowednotification",
            name="notification",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                parent_link=True,
                to="furfolio.notification",
            ),
        ),
    ]