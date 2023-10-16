# Generated by Django 4.2.4 on 2023-10-16 02:01

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('furfolio', '0046_alter_offer_currency'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='consent_to_adult_content',
            field=models.BooleanField(default=False, help_text='Indicate if you would like to see adult content on this website. If not indicated, you will not see adult content.', verbose_name='Consent to See Adult Content'),
        ),
        migrations.AlterField(
            model_name='offer',
            name='max_price',
            field=models.PositiveIntegerField(default=5, help_text='The maximum price for commissions of this offer.', validators=[django.core.validators.MinValueValidator(1)], verbose_name='Maximum Price'),
        ),
    ]