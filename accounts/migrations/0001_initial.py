# Generated by Django 4.2.1 on 2023-05-12 19:48

from django.db import migrations, models
import django.utils.timezone

import accounts.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID'
                    )
                ),
                (
                    'title',
                    models.CharField(
                        max_length=128,
                        verbose_name='Title'
                    )
                ),
                (
                    'description',
                    models.TextField(
                        verbose_name='Description'
                    )
                ),
                (
                    'slug',
                    models.SlugField()
                ),
                (
                    'weight',
                    models.PositiveSmallIntegerField(
                        default=0,
                        verbose_name='Weight'
                    )
                ),
            ],
            options={
                'verbose_name_plural': 'Categories',
            }
        ),
        migrations.CreateModel(
            name='FeedbackMessage',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID'
                    )
                ),
                (
                    'email',
                    models.EmailField(
                        help_text='Your e-mail',
                        max_length=254,
                        verbose_name='Email address'
                    )
                ),
                (
                    'name',
                    models.CharField(
                        help_text='Your name',
                        max_length=200,
                        verbose_name='Name'
                    )
                ),
                (
                    'subject',
                    models.CharField(
                        max_length=100,
                        verbose_name='Subject'
                    )
                ),
                (
                    'body',
                    models.TextField(
                        verbose_name='Body'
                    )
                ),
                (
                    'approved',
                    models.BooleanField(
                        default=False,
                        verbose_name='Approved'
                    )
                ),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID'
                    )
                ),
                (
                    'password',
                    models.CharField(
                        max_length=128,
                        verbose_name='password'
                    )
                ),
                (
                    'last_login',
                    models.DateTimeField(
                        blank=True,
                        null=True,
                        verbose_name='last login'
                    )
                ),
                (
                    'is_superuser',
                    models.BooleanField(
                        default=False,
                        help_text='Designates that this user has all permissions without explicitly assigning them.',
                        verbose_name='superuser status'
                    )
                ),
                (
                    'username',
                    models.CharField(
                        error_messages={
                            'unique': 'A user with that username already exists.',
                        },
                        help_text='150 characters or fewer. Letters and digits only.',
                        max_length=64,
                        unique=True,
                        verbose_name='username'
                    )
                ),
                (
                    'first_name',
                    models.CharField(
                        max_length=150,
                        verbose_name='First name'
                    )
                ),
                (
                    'last_name',
                    models.CharField(
                        max_length=50,
                        verbose_name='Last name'
                    )
                ),
                (
                    'email',
                    models.EmailField(
                        default=None,
                        error_messages={
                            'unique': 'A user with that email already exists.',
                        },
                        max_length=254,
                        unique=True,
                        verbose_name='Email address'
                    )
                ),
                (
                    'is_staff',
                    models.BooleanField(
                        default=False,
                        help_text='Designates whether the user can log into this admin site.',
                        verbose_name='Staff status'
                    )
                ),
                (
                    'is_active',
                    models.BooleanField(
                        default=True,
                        help_text='Designates whether this user should be treated as active. '
                                  'Unselect this instead of deleting accounts.',
                        verbose_name='Active'
                    )
                ),
                (
                    'date_joined',
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        verbose_name='Date joined'
                    )
                ),
                (
                    'is_confirmed',
                    models.BooleanField(
                        default=False,
                        help_text='Designates whether this user confirmed an email or other authenticated method.',
                        verbose_name='Is confirmed'
                    )
                ),
                (
                    'birth_date',
                    models.DateField(
                        default=django.utils.timezone.now,
                        help_text='Birth date'
                    ),
                ),
                (
                    'categories',
                    models.ManyToManyField(
                        blank=True,
                        related_query_name='users',
                        to='accounts.category'
                    )
                ),
                (
                    'groups',
                    models.ManyToManyField(
                        blank=True,
                        help_text='The groups this user belongs to. '
                                  'A user will get all permissions granted to each of their groups.',
                        related_name='user_set',
                        related_query_name='user',
                        to='auth.group',
                        verbose_name='groups'
                    )
                ),
                (
                    'user_permissions',
                    models.ManyToManyField(
                        blank=True,
                        help_text='Specific permissions for this user.',
                        related_name='user_set',
                        related_query_name='user',
                        to='auth.permission',
                        verbose_name='user permissions'
                    )
                ),
            ],
            options={
                'verbose_name': 'User',
                'verbose_name_plural': 'Users',
            },
            managers=[
                (
                    'objects',
                    accounts.managers.UserManager()
                ),
            ]
        ),
    ]
