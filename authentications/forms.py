from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from dateutil.relativedelta import relativedelta
from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import (
    _unicode_ci_compare,  # noqa
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
    UserCreationForm,
    UsernameField,
)
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from accounts.forms import ErrorFormMixin
from accounts.models import User


class SignInForm(AuthenticationForm):
    username = UsernameField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'autofocus': True,
            }
        )
    )
    password = forms.CharField(
        label=_('Password'),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'autocomplete': 'current-password',
            }
        ),
    )
    next = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )

    error_messages = {
        'invalid_login': _(
            'Please enter a correct %(username)s and password. Note that both '
            'fields may be case-sensitive.'
        ),
        'inactive': _('This account is inactive.'),
        'not_confirmed': _(
                    "%(user_name)s, looks like you haven't activated an account. "
                    "If you haven't received an email try to reset the password."
                ),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['next'] = self.request.GET.get("next", "")

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )
        if not user.is_confirmed:
            raise ValidationError(
                self.error_messages['not_confirmed'] % ({
                    'user_name': user.username,
                }),
                code='not_confirmed',
            )


class SignUpForm(ErrorFormMixin, UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'autofocus': True,
            }
        ),
        min_length=5,
        max_length=64,
        required=True
    )
    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
            }
        ),
        max_length=64,
        required=True
    )
    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
            }
        ),
        max_length=64,
        required=True
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
            }
        ),
        max_length=254,
        required=True
    )
    birth_date = forms.DateTimeField(
        input_formats=['%d/%m/%Y %H:%M'],
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'date',
        })
    )
    password1 = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
            }
        ),
        max_length=254,
        required=True
    )
    password2 = forms.CharField(
        label=_('Confirm password'),
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
            }
        ),
        max_length=254,
        required=True
    )
    captcha = ReCaptchaField(
        label='',
        error_messages={
            'required': _('Please confirm you are not a robot!'),
        },
        widget=ReCaptchaV2Checkbox(
            attrs={
                'class': 'form-control',
            }
        )
    )

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'birth_date',
            'password1',
            'password2',
            'captcha',
        )

    def clean_birth_date(self):
        birth_date = self.cleaned_data['birth_date']
        min_age = 7
        max_age = 150
        full_age = relativedelta(timezone.now(), birth_date).years
        if min_age > full_age:
            raise ValidationError(
                _('You are too young for this resource. Minimum age is %s.') % min_age
            )
        if full_age > max_age:
            raise ValidationError(
                _('You are too old for this resource. Maximum age is %s.') % max_age
            )
        return birth_date


class AuthPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label=_('Email'),
        max_length=254,
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'autofocus': True,
                'autocomplete': 'email',
            }
        ),
    )
    captcha = ReCaptchaField(
        label='',
        error_messages={
            'required': _('Please confirm you are not a robot!'),
        },
        widget=ReCaptchaV2Checkbox(
            attrs={
                'class': 'form-control',
            }
        )
    )

    def get_users(self, email):
        email_field_name = User.get_email_field_name()
        active_users = User._default_manager.filter(  # noqa
            **{
                '%s__iexact' % email_field_name: email,
                'is_active': True,
            }
        )
        return (
            u
            for u in active_users
            if u.has_usable_password()
            and _unicode_ci_compare(email, getattr(u, email_field_name))
        )


class PasswordSetForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label=_('New password'),
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'autofocus': True,
                'autocomplete': 'new-password',
            }
        ),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label=_('New password confirmation'),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'autocomplete': 'new-password',
            }
        ),
    )
    captcha = ReCaptchaField(
        label='',
        error_messages={
            'required': _('Please confirm you are not a robot!'),
        },
        widget=ReCaptchaV2Checkbox(
            attrs={
                'class': 'form-control',
            }
        )
    )

    def save(self, commit=True):
        password = self.cleaned_data['new_password1']
        self.user.set_password(password)
        self.user.is_confirmed = True
        if commit:
            self.user.save()
        return self.user


class ChangePasswordForm(PasswordChangeForm):
    old_password = forms.CharField(
        label=_('Old password'),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'autocomplete': 'current-password',
                'placeholder': _('Old password'),
            }
        ),
    )
    new_password1 = forms.CharField(
        label=_('New password'),
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'autocomplete': 'new-password',
                'placeholder': _('New password'),
            }
        ),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label=_('New password confirmation'),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'autocomplete': 'new-password',
                'placeholder': _('New password confirmation'),
            }
        ),
    )
