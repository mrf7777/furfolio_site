# Generated by Django 4.2.4 on 2023-09-29 00:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('furfolio', '0031_alter_commissionmessage_commission'),
    ]

    operations = [
        migrations.AddField(
            model_name='commissionmessage',
            name='id',
            field=models.BigAutoField(auto_created=True, default=1, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='commissionmessage',
            name='commission',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='furfolio.commission'),
        ),
    ]
