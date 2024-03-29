# Generated by Django 4.2.4 on 2023-11-06 23:34

from django.db import migrations, models
import furfolio.validators


class Migration(migrations.Migration):
    dependencies = [
        ("furfolio", "0058_alter_tag_description"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tag",
            name="name",
            field=models.CharField(
                max_length=38,
                unique=True,
                validators=[furfolio.validators.validate_tag_name],
                verbose_name="Name",
            ),
        ),
    ]
