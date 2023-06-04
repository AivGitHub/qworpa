from django import template
from django.contrib.messages import constants as message_constants

from core import settings

AVAILABLE_SETTINGS = [
    'PROJECT_NAME',
    'TINYMCE_API_KEY',
]


register = template.Library()


@register.simple_tag
def get_setting(value: str):
    setting_name: str = value.upper()
    if setting_name not in AVAILABLE_SETTINGS:
        raise RuntimeError('Setting %s is not available' % value)

    try:
        return settings.__getattribute__(setting_name)
    except AttributeError:
        raise RuntimeError('Setting %s not found' % setting_name)


@register.simple_tag
def has_success_message(messages):
    for message in messages:
        if message.level == message_constants.SUCCESS:
            return True
    return False


@register.simple_tag
def define_value(value=None):
    return value
