# Generated by Django 4.2.4 on 2023-09-25 20:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('furfolio', '0025_alter_offer_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offer',
            name='rating',
            field=models.CharField(choices=[('MAT', 'Mature'), ('GEN', 'General'), ('ADL', 'Adult')], default='GEN', max_length=3),
        ),
    ]
