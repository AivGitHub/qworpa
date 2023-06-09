# Generated by Django 4.2.1 on 2023-06-20 20:53

from django.db import migrations


def load_initial_categories(apps, schema_editor):
    from django.core.management import call_command
    call_command('loaddata', 'accounts/fixtures/initial_categories.json')


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_initial_categories),
    ]
