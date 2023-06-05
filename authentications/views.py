from smtplib import SMTPException

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.views import LoginView, PasswordResetCompleteView, PasswordResetConfirmView, PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.core.mail import BadHeaderError, send_mail
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, TemplateView

from accounts.models import User
from authentications.forms import AuthPasswordResetForm, PasswordSetForm, SignInForm, SignUpForm
from authentications.models import (
    decode_jwt_signature,
    FatalSignatureError,
    generate_jwt_signature,
    SignatureExpiredError,
)


class AuthViewMixin:
    def dispatch(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('/')
        return super().dispatch(*args, **kwargs)


class SignInView(AuthViewMixin, LoginView):
    form_class = SignInForm
    template_name = 'authentications/sign_in.html'

    def get_success_url(self):
        return reverse_lazy('feed')

    def form_invalid(self, form: SignInForm):
        # Maybe here we need to use ``form.errors`` in templates, but for now ``django.contrib.messages`` are used.
        if form.user_cache is not None and not form.user_cache.is_confirmed:
            messages.error(
                self.request,
                _(
                    "<p>%(user_name)s, looks like you haven't activated an account.</p>"
                    "<p>If you haven't received an email try to <a href='%(reset_url)s'>reset the password</a>.</p>"
                ) % ({
                    'user_name': form.user_cache.username,
                    'reset_url': reverse_lazy('reset-password'),
                })
            )
        else:
            messages.error(self.request, _('Invalid username or password!'))
        return self.render_to_response(self.get_context_data(form=form))


class SignUpView(AuthViewMixin, FormView):
    redirect_authenticated_user = True
    template_name = 'authentications/sign_up.html'
    form_class = SignUpForm
    success_url = '.'

    def get_context_data(self, **kwargs):
        context = super(SignUpView, self).get_context_data(**kwargs)
        return context

    def form_valid(self, form: SignUpForm):
        sign_up_form = form.save()
        signature = generate_jwt_signature(
            {
                'username': sign_up_form.username,
            }
        )
        html_message = render_to_string(
            'authentications/emails/confirm.html',
            context={
                'user': sign_up_form,
                'sign_in_url': '%s%s' % (
                    settings.PROJECT_URL,
                    reverse_lazy('confirm-email', kwargs={'token': signature})
                ),
            }
        )
        original_message = strip_tags(html_message)
        try:
            send_mail(
                _('Subject'),
                original_message,
                settings.DEFAULT_FROM_EMAIL,
                [sign_up_form.email],
                html_message=html_message
            )
        except (BadHeaderError, SMTPException):
            messages.error(
                self.request,
                _(
                    '<p>%(user_name)s, thank you for registration.</p>'
                    '<p>You should have received an e-mail on %(user_email)s, but something went wrong.</p>'
                    '<p>You can <a href="%(reset_password_url)s">request access here</a>.</p>'
                ) % ({
                    'user_name': sign_up_form.username,
                    'user_email': sign_up_form.email,
                    'reset_password_url': reverse_lazy('reset-password'),
                })
            )
        else:
            messages.success(
                self.request,
                _(
                    '<p>%(user_name)s, thank you for registration.</p>'
                    '<p>You will receive an e-mail on %(user_email)s, please follow instructions in the letter.</p>'
                    '<p>You can <a href="%(sign_in_url)s">Sign In</a> now.</p>'
                ) % ({
                    'user_name': sign_up_form.first_name,
                    'user_email': sign_up_form.email,
                    'sign_in_url': reverse_lazy('sign-in'),
                })
            )
        return super(SignUpView, self).form_valid(form)


class ConfirmEmailView(AuthViewMixin, TemplateView):
    template_name = 'authentications/confirm_email.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        try:
            token = context['token']
        except KeyError:
            raise PermissionDenied()
        try:
            payload = decode_jwt_signature(token)
        except FatalSignatureError:
            raise PermissionDenied()
        except SignatureExpiredError:
            messages.error(
                request,
                _(
                    '<p>Looks like this link has expired.</p>'
                    'You can request a new password to activate your account <a href="%(reset_password_url)s">Here</a>.'
                ) % (
                    {
                        'reset_password_url': reverse_lazy('reset-password'),
                    }
                )
            )
            return self.render_to_response(context)
        try:
            username = payload['username']
        except KeyError:
            raise PermissionDenied()

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise PermissionDenied()

        if user.is_confirmed:
            return redirect(reverse_lazy('sign-in'))
        user.is_confirmed = True
        user.save(update_fields=['is_confirmed'])

        messages.success(
            request,
            _(
                '<p>%(username)s, you successfully activated your account.</p>'
                '<p>You may go ahead and <a href="%(sign_in_url)s">Sign In!</a></p>'
            ) % (
                {
                    'username': user.username,
                    'sign_in_url': reverse_lazy('sign-in'),
                }
            )
        )
        return self.render_to_response(context)


class ResetPasswordView(AuthViewMixin, SuccessMessageMixin, PasswordResetView):
    form_class = AuthPasswordResetForm
    template_name = 'authentications/reset_password.html'
    email_template_name = 'authentications/emails/reset_password.html'
    html_email_template_name = 'authentications/emails/reset_password.html'
    from_email = settings.DEFAULT_FROM_EMAIL
    success_message = _(
        "We've emailed you instructions for setting your password, "
        "if an account exists with the email you entered. You should receive them shortly. "
        "If you don't receive an email, "
        "please make sure you've entered the address you registered with, and check your spam folder."
    )
    success_url = reverse_lazy('reset-password')
    extra_email_context = {
        'project_url': settings.PROJECT_URL,
    }


class ResetPasswordConfirmView(AuthViewMixin, PasswordResetConfirmView):
    template_name = 'authentications/reset_password_confirm.html'
    form_class = PasswordSetForm
    success_url = reverse_lazy('reset-password-complete')


class ResetPasswordCompleteView(AuthViewMixin, PasswordResetCompleteView):
    template_name = 'authentications/reset_password_complete.html'
