# Generated by Django 4.2.4 on 2023-09-22 19:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('furfolio', '0010_commission'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='commission',
            name='commissionee',
        ),
    ]
