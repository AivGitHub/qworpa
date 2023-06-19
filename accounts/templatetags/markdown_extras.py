import bleach
from django import template
from django.template.defaultfilters import stringfilter
import markdown as mark_down

register = template.Library()


markdown_tags = [
    "h1", "h2", "h3", "h4", "h5", "h6",
    "b", "i", "strong", "em", "tt",
    "p", "br",
    "span", "div", "blockquote", "code", "hr",
    "ul", "ol", "li", "dd", "dt",
    "img",
    "a",
    "sub", "sup",
]

markdown_attrs = {
    "*": ["id"],
    "img": ["src", "alt", "title"],
    "a": ["href", "alt", "title"],
}


@register.filter()
@stringfilter
def markdown(value):
    return bleach.clean(
        mark_down.markdown(value, extensions=['markdown.extensions.fenced_code']),
        markdown_tags,
        markdown_attrs
    )


@register.filter(name='nbsp2space', is_safe=True)
@stringfilter
def nbsp2space(value):
    return ' '.join(value.replace('&nbsp;', '').split())
