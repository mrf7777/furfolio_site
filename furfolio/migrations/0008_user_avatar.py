# Generated by Django 4.2.4 on 2023-09-15 19:49

from django.db import migrations, models
import furfolio.validators


class Migration(migrations.Migration):

    dependencies = [
        ('furfolio', '0007_offer_thumbnail_alter_offer_cutoff_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='avatar',
            field=models.ImageField(blank=True, help_text='Your avatar must be of small size.', upload_to='', validators=[furfolio.validators.validate_profile_image_is_right_size]),
        ),
    ]
