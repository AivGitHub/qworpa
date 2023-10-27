# Generated by Django 4.2.1 on 2023-10-27 19:00

import crypto.models
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hex', models.CharField(default=crypto.models.get_message_hex, editable=False, max_length=32, unique=True, verbose_name='Message hex')),
                ('text', models.TextField(editable=False, verbose_name='Message text')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created date')),
            ],
        ),
    ]
