from django.contrib import admin

from blogs.models import Post, PostComment, PostCommentLike, PostLike


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    pass


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    pass


@admin.register(PostComment)
class PostCommentAdmin(admin.ModelAdmin):
    pass


@admin.register(PostCommentLike)
class PostCommentLikeAdmin(admin.ModelAdmin):
    pass
