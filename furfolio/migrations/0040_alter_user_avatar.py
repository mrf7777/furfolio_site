# Generated by Django 4.2.4 on 2023-10-04 15:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('furfolio', '0039_alter_commission_state'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.ImageField(blank=True, help_text='Avatars are optional. Your avatar must be 64 by 64 pixels.', upload_to=''),
        ),
    ]
