from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
)
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from accounts.managers import UserManager


class Category(models.Model):
    title = models.CharField(
        _('Title'),
        max_length=128,
        null=False,
        blank=False
    )
    description = models.TextField(
        _('Description'),
        null=False,
        blank=False
    )
    slug = models.SlugField()
    weight = models.PositiveSmallIntegerField(
        _('Weight'),
        default=0,
        null=False,
        blank=False
    )

    class Meta:
        verbose_name_plural = _('Categories')

    def __str__(self):
        return self.title


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        _('username'),
        max_length=64,
        help_text=_('150 characters or fewer. Letters and digits only.'),
        error_messages={
            'unique': _('A user with that username already exists.'),
        },
        null=False,
        blank=False,
        unique=True
    )
    first_name = models.CharField(
        _('First name'),
        max_length=150,
        null=False,
        blank=False
    )
    last_name = models.CharField(
        _('Last name'),
        max_length=50,
        null=False,
        blank=False
    )
    email = models.EmailField(
        _('Email address'),
        max_length=254,
        error_messages={
            'unique': _('A user with that email already exists.'),
        },
        default=None,
        null=False,
        blank=False,
        unique=True
    )
    is_staff = models.BooleanField(
        _('Staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.')
    )
    is_active = models.BooleanField(
        _('Active'),
        default=True,
        help_text=_('Designates whether this user should be treated as active. '
                    'Unselect this instead of deleting accounts.')
    )
    date_joined = models.DateTimeField(
        _('Date joined'),
        default=timezone.now
    )
    is_confirmed = models.BooleanField(
        _('Is confirmed'),
        default=False,
        help_text=_('Designates whether this user confirmed an email or '
                    'other authenticated method.')
    )
    birth_date = models.DateField(
        help_text=_('Birth date'),
        default=timezone.now
    )
    categories = models.ManyToManyField(
        Category,
        related_query_name='users',
        blank=True
    )

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self) -> str:
        return self.username

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def clean(self) -> None:
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self) -> str:
        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name}'

        if self.first_name:
            return self.first_name

        if self.last_name:
            return self.last_name

        return self.username

    def get_safe_full_name(self) -> str:
        full_name = self.get_full_name()
        full_name_split = full_name.split()
        if len(full_name_split) == 1:
            return full_name
        # We need it in case user has a second name
        first_name = full_name_split.pop(0)
        return '%s %s' % (first_name, ' '.join(['%s.' % a[0] for a in full_name_split]))

    def email_user(self, subject, message, from_email=None, **kwargs) -> None:
        send_mail(subject, message, from_email, [self.email], **kwargs)


class FeedbackMessage(models.Model):
    email = models.EmailField(
        _('Email address'),
        help_text=_('Your e-mail'),
        max_length=254,
        null=False,
        blank=False
    )
    name = models.CharField(
        _('Name'),
        help_text=_('Your name'),
        max_length=200,
        null=False,
        blank=False
    )
    subject = models.CharField(
        _('Subject'),
        max_length=100,
        null=False,
        blank=False
    )
    body = models.TextField(
        _('Body'),
        null=False,
        blank=False
    )
    approved = models.BooleanField(
        _('Approved'),
        default=False
    )
