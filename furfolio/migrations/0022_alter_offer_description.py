# Generated by Django 4.2.4 on 2023-09-25 00:36

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('furfolio', '0021_offer_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offer',
            name='description',
            field=models.TextField(default='', help_text='Describes the details of the offer.', max_length=4700, validators=[django.core.validators.MinLengthValidator(18)]),
        ),
    ]