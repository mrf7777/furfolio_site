# Generated by Django 4.2.4 on 2023-09-29 00:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('furfolio', '0030_commissionmessage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commissionmessage',
            name='commission',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='furfolio.commission'),
        ),
    ]