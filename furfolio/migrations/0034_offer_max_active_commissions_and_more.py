# Generated by Django 4.2.4 on 2023-09-30 22:00

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('furfolio', '0033_alter_commissionmessage_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='offer',
            name='max_active_commissions',
            field=models.PositiveIntegerField(default=3, help_text='The maximum number of commissions you are willing to work on for this offer. Commissions in the review state do not count.', validators=[django.core.validators.MinValueValidator(1)], verbose_name='Max Active Commissions'),
        ),
        migrations.AddField(
            model_name='offer',
            name='max_review_commissions',
            field=models.PositiveIntegerField(default=5, help_text='The maximum number of commissions allowed to be in the review state. Use this to prevent being overloaded with too many commission requests at a time.', validators=[django.core.validators.MinValueValidator(1)], verbose_name='Max Commissions in Review'),
        ),
    ]
