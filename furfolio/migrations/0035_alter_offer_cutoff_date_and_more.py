# Generated by Django 4.2.4 on 2023-10-01 00:25

import django.contrib.postgres.indexes
from django.contrib.postgres.operations import BtreeGinExtension
import django.core.validators
from django.db import migrations, models
import furfolio.models
import furfolio.validators


class Migration(migrations.Migration):

    dependencies = [
        ('furfolio', '0034_offer_max_active_commissions_and_more'),
    ]

    operations = [
        BtreeGinExtension(),
        migrations.AlterField(
            model_name='offer',
            name='cutoff_date',
            field=models.DateTimeField(default=furfolio.models.seven_days_from_now, validators=[furfolio.validators.validate_datetime_not_in_past]),
        ),
        migrations.AlterField(
            model_name='offer',
            name='max_active_commissions',
            field=models.PositiveIntegerField(default=3, help_text='The maximum number of commissions you are willing to work on for this offer.<br>This includes commissions that you accept, are in progress, or closed. Commissions in the review state do not count.', validators=[django.core.validators.MinValueValidator(1)], verbose_name='Max Active Commissions'),
        ),
        migrations.AlterField(
            model_name='offer',
            name='max_review_commissions',
            field=models.PositiveIntegerField(default=5, help_text='The maximum number of commissions allowed to be in the review state.<br>Use this to prevent being overloaded with too many commission requests at a time.', validators=[django.core.validators.MinValueValidator(1)], verbose_name='Max Commissions in Review'),
        ),
        migrations.AddIndex(
            model_name='offer',
            index=django.contrib.postgres.indexes.GinIndex(fastupdate=False, fields=['name', 'description'], name='offer_name_description_index'),
        ),
    ]