# Generated by Django 4.2.4 on 2023-10-01 20:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('furfolio', '0036_alter_user_options_user_user_username_index'),
    ]

    operations = [
        migrations.RenameField(
            model_name='offer',
            old_name='max_active_commissions',
            new_name='slots',
        ),
    ]