from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from accounts.views import UserPermissionsMixin
from blogs.forms import PostCreateForm, PostEditForm
from blogs.models import Post


class PostListView(ListView):
    template_name = 'blogs/post_list.html'
    paginate_by = 5

    def get_queryset(self, *args, **kwargs):
        return Post.objects.exclude(is_draft=True).order_by('-created_at')


class PostDetailsView(DetailView):
    model = Post
    template_name = 'blogs/post_details.html'
    slug_field = 'url_hex'
    slug_url_kwarg = 'url_hex'

    def get_object(self, queryset=None):
        post = super(PostDetailsView, self).get_object(queryset=queryset)
        post.check_access(self.request.user)
        return post


class MyPostListView(LoginRequiredMixin, ListView):
    login_url = reverse_lazy('sign-in')
    template_name = 'blogs/post_list.html'
    paginate_by = 5

    def get_queryset(self, *args, **kwargs):
        return Post.objects.filter(author=self.request.user).order_by('-created_at')


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'blogs/post_edit.html'
    form_class = PostCreateForm
    extra_context = {
        'submit_button_text': _('Create post'),
    }

    def get_success_url(self):
        messages.success(
            self.request,
            _(
                '<p>Congratulations! You created the post <a href="%(post_url)s">%(title)s</a>.</p>'
            ) % ({
                'post_url': reverse_lazy('post-details', kwargs={'url_hex': self.object.url_hex}),
                'title': self.object.title,
            })
        )
        return reverse_lazy('my-post-list')

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.author = self.request.user
        obj.save()
        return super().form_valid(form)


class PostEditView(LoginRequiredMixin, UserPermissionsMixin, UpdateView):
    model = Post
    form_class = PostEditForm
    slug_field = 'url_hex'
    slug_url_kwarg = 'url_hex'
    template_name = 'blogs/post_edit.html'
    extra_context = {
        'page_title': _('Edit post'),
        'submit_button_text': _('Edit post'),
    }

    def get_success_url(self):
        return reverse_lazy('post-details', kwargs={'url_hex': self.object.url_hex})


class FavoritesListView(LoginRequiredMixin, ListView):
    login_url = reverse_lazy('sign-in')
    template_name = 'blogs/post_list.html'
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
        # TODO: Sure can be optimized.
        return Post.objects.filter(id__in=self.request.user.post_likes.values_list('post_id'), is_draft=False)
