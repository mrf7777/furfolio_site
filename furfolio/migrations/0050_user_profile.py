# Generated by Django 4.2.4 on 2023-10-23 00:31

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("furfolio", "0049_alter_offer_max_price_alter_offer_min_price"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="profile",
            field=models.TextField(
                blank=True,
                help_text="This will display on you profile page. Use this to describe yourself.",
                max_length=4700,
                verbose_name="Profile Description",
            ),
        ),
    ]