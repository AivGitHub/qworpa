# Generated by Django 4.2.1 on 2023-07-25 20:31

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20230620_2053'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='subscribers',
            field=models.ManyToManyField(blank=True, related_name='subscriptions', to=settings.AUTH_USER_MODEL),
        ),
    ]
