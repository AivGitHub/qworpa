from django.contrib.auth.views import LogoutView
from django.urls import path

from authentications.views import (
    ConfirmEmailView,
    ResetPasswordCompleteView,
    ResetPasswordConfirmView,
    ResetPasswordView,
    SignInView,
    SignUpView,
)

urlpatterns = [
    path('sign-in/', SignInView.as_view(), name='sign-in'),
    path('sign-up/', SignUpView.as_view(), name='sign-up'),
    path('passwords/reset/', ResetPasswordView.as_view(), name='reset-password'),
    path(
        'passwords/reset/confirm/<uidb64>/<token>/', ResetPasswordConfirmView.as_view(), name='reset-password-confirm'
    ),
    path(
        'passwords/reset/complete/', ResetPasswordCompleteView.as_view(), name='reset-password-complete'
    ),
    path(
        'emails/confirm/<token>/', ConfirmEmailView.as_view(), name='confirm-email'
    ),
    path('logout/', LogoutView.as_view(template_name='authentications/logout.html'), name='logout'),
]
