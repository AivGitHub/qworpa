from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from accounts.models import FeedbackMessage


class ErrorFormMixin:
    def set_error_class_for_field(self, name, class_name='is-invalid'):
        try:
            self.fields[name]
        except KeyError:
            return
        try:
            self.fields[name].widget.attrs['class'] += ' %s' % class_name
        except KeyError:
            return

    def is_valid(self) -> bool:
        for name, field in self.errors.items():
            self.set_error_class_for_field(name)

        return super().is_valid()


class FeedbackMessageForm(ErrorFormMixin, forms.ModelForm):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'autofocus': True,
            }
        ),
        max_length=254,
        required=True
    )
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
            }
        ),
        max_length=200,
        required=True
    )
    subject = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
            }
        ),
        max_length=100,
        required=True
    )
    body = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': '4',
                'resize': 'none',
            }
        ),
        help_text=_('Here you can tell me what you want!'),
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
        model = FeedbackMessage
        fields = "__all__"
        exclude = (
            'approved',
        )

    def clean_body(self):
        body = self.cleaned_data['body']
        limit = 1024
        if len(body) >= limit:
            raise ValidationError(_('Please limit your message with %s chars') % limit)
        return body
