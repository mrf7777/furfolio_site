# Generated by Django 4.2.4 on 2023-09-08 00:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('furfolio', '0004_alter_offer_cutoff_date'),
    ]

    operations = [
        migrations.RenameField(
            model_name='offer',
            old_name='created date',
            new_name='created_date',
        ),
        migrations.RenameField(
            model_name='offer',
            old_name='updated date',
            new_name='updated_date',
        ),
    ]
