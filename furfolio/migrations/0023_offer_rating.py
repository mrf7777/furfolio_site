# Generated by Django 4.2.4 on 2023-09-25 20:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('furfolio', '0022_alter_offer_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='offer',
            name='rating',
            field=models.CharField(default='GEN', max_length=3),
        ),
    ]
