# Generated by Django 4.2.4 on 2023-09-03 02:02

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('furfolio', '0002_offer'),
    ]

    operations = [
        migrations.AddField(
            model_name='offer',
            name='cutoff date',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]