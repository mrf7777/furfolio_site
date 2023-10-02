# Generated by Django 4.2.4 on 2023-10-02 00:48

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('furfolio', '0037_rename_max_active_commissions_offer_slots'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commission',
            name='state',
            field=models.CharField(choices=[('REVIEW', 'Review'), ('ACCEPTED', 'Accepted'), ('IN_PROGRESS', 'In Progress'), ('CLOSED', 'Finished')], default='REVIEW', max_length=11),
        ),
        migrations.AlterField(
            model_name='offer',
            name='slots',
            field=models.PositiveIntegerField(default=3, help_text='The maximum number of commissions you are willing to work on for this offer.<br>This is not a hard limit; it is used to communicate how many commissions you are willing to work.', validators=[django.core.validators.MinValueValidator(1)], verbose_name='Slots'),
        ),
    ]