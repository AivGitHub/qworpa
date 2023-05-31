from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from accounts.models import Category
from blogs.models import Post


class PostCreateForm(forms.ModelForm):
    title = forms.CharField(
        label=_('Title'),
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'autofocus': True,
            }
        ),
        help_text=_("You can't change the title after you create a post.")
    )
    content = forms.CharField(
        label=_('Content'),
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': '16',
                'resize': 'none',
            }
        ),
        help_text=_('Text supports default markdown.'),
        required=True
    )
    category = forms.ModelChoiceField(
        label=_('Category'),
        error_messages={
            'invalid_choice': _('Select valid category.'),
        },
        widget=forms.Select(
            attrs={
                'class': 'form-control',
            }
        ),
        queryset=Category.objects.all(),
        help_text=_("You can't change the category after you create a post.")
    )
    is_draft = forms.BooleanField(
        label=_('Draft'),
        widget=forms.CheckboxInput(
            attrs={
                'class': 'form-check-input',
            }
        ),
        help_text=_('Only you can see your draft posts.'),
        required=False,
        initial=False
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
        model = Post
        fields = ('title', 'is_draft', 'category', 'content', 'captcha',)


class PostEditForm(PostCreateForm):
    title = forms.CharField(
        label=_('Title'),
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
            }
        ),
        disabled=True
    )
    category = forms.ModelChoiceField(
        label=_('Category'),
        error_messages={
            'invalid_choice': _('Select valid category.'),
        },
        widget=forms.Select(
            attrs={
                'class': 'form-control',
            }
        ),
        queryset=Category.objects.all(),
        disabled=True
    )
    captcha = None

    class Meta:
        model = Post
        fields = ('title', 'is_draft', 'category', 'content',)

    def clean_category(self):
        if self.cleaned_data['category'].id == self.initial['category']:
            return self.cleaned_data['category']
        raise ValidationError(_("You can't change the category."))

    def clean_title(self):
        if self.cleaned_data['title'] == self.initial['title']:
            return self.cleaned_data['title']
        raise ValidationError(_("You can't change the title."))
