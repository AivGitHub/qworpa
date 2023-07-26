from django import template

register = template.Library()


@register.simple_tag
def user_has_liked_post(post, user):
    return post.has_liked(user)


@register.simple_tag
def user_has_liked_comment(comment, user):
    return comment.has_liked(user)


@register.simple_tag
def user_has_subscribed(user, author):
    if user.is_anonymous:
        return False
    return author.subscribers.contains(user)
