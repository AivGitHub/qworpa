from django import template

register = template.Library()


@register.simple_tag
def user_has_liked_post(post, user):
    return post.has_liked(user)
