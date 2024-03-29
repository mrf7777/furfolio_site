# Generated by Django 4.2.4 on 2023-09-22 19:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('furfolio', '0009_alter_user_avatar'),
    ]

    operations = [
        migrations.CreateModel(
            name='Commission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('initial_request_text', models.CharField(default='', max_length=3760)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('commissionee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='commission_set_as_commissionee', to=settings.AUTH_USER_MODEL)),
                ('commissioner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='commission_set_as_commissioner', to=settings.AUTH_USER_MODEL)),
                ('offer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='furfolio.offer')),
            ],
        ),
    ]
