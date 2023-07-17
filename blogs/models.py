from uuid import uuid4

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.models import Category, User


class UUID4HEXNotGenerated(Exception):
    """UUID4 hex is not generated."""


def get_url_hex(tries=5):
    """Generates UUID4 hex.

    Args:
        tries (int, optional): Number of attempts to generate unique hex for given ``field``.

    Returns:
        str: UUID4 hex.

    Raises:
        blogs.models.UUID4HEXNotGenerated: If hex is not generated.
    """
    for _ in range(tries):
        uuid4_hex = uuid4().hex
        try:
            Post.objects.get(url_hex=uuid4_hex)
        except Post.DoesNotExist:
            return uuid4_hex
    else:
        raise UUID4HEXNotGenerated()


class Post(models.Model):
    title = models.CharField(
        _('Title'),
        max_length=200,
        blank=False,
        null=False
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        blank=False,
        null=False
    )
    content = models.TextField(
        _('Content')
    )
    created_at = models.DateTimeField(
        _('Created on'),
        auto_now_add=True,
        blank=False,
        null=False
    )
    url_hex = models.CharField(
        _('URL hex'),
        max_length=32,
        default=get_url_hex,
        editable=False,
        null=False,
        blank=False,
        unique=True
    )
    # I decided to use float instead of decimal.
    # If you have arguments please let me know.
    weight = models.FloatField(
        _('Weight'),
        default=0,
        null=False,
        blank=False
    )
    tags = models.TextField(
        _('Tags'),
        max_length=512,
        default='',
        null=True,
        blank=True
    )
    is_draft = models.BooleanField(
        _('Draft'),
        default=False,
        help_text=_('Designates whether this post should be treated as draft.')
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='posts',
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def check_access(self, user):
        if self.is_draft and user != self.author:
            raise PermissionDenied()

    def has_liked(self, user):
        if user.is_anonymous:
            return False
        try:
            self.likes.get(user=user)
        except PostLike.DoesNotExist:
            return False
        return True


class PostLike(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='post_likes'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='likes',
    )
    created_at = models.DateTimeField(
        _('Created at'),
        auto_now_add=True
    )

    def clean(self):
        cleaned_data = super().clean()
        try:
            self.post.likes.get(user=self.user)
        except PostLike.DoesNotExist:
            return cleaned_data
        raise ValidationError(_('You already liked this post.'))


class PostComment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='post_comments'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='nested_comments'
    )
    content = models.TextField()
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    def has_liked(self, user):
        if user.is_anonymous:
            return False
        try:
            self.likes.get(user=user)
        except PostCommentLike.DoesNotExist:
            return False
        return True

    def clean(self):
        cleaned_data = super().clean()
        if self.parent is not None and self == self.parent:
            raise ValidationError(_("Post can't be a parent to itself."))
        if self.parent is not None and self.parent.parent is not None:
            raise ValidationError(_('Only one nesting level is allowed'))
        return cleaned_data

    def has_delete_permission(self, user: User):
        if user.is_anonymous:
            return False
        return self.author == user or self.post.author == user

    class Meta:
        ordering = ('created_at',)


class PostCommentLike(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comment_likes'
    )
    comment = models.ForeignKey(
        PostComment,
        on_delete=models.CASCADE,
        related_name='likes',
    )
    created_at = models.DateTimeField(
        _('Created at'),
        auto_now_add=True
    )

    def clean(self):
        cleaned_data = super().clean()
        try:
            self.comment.likes.get(user=self.user)
        except PostCommentLike.DoesNotExist:
            return cleaned_data
        raise ValidationError(_('You already liked this comment.'))
