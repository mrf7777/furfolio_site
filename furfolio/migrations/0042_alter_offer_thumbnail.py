# Generated by Django 4.2.4 on 2023-10-04 17:58

from django.db import migrations, models
import furfolio.validators


class Migration(migrations.Migration):

    dependencies = [
        ('furfolio', '0041_alter_user_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offer',
            name='thumbnail',
            field=models.ImageField(blank=True, null=True, upload_to='', validators=[furfolio.validators.validate_offer_thumbnail_aspect_ratio]),
        ),
    ]