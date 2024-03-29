"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from accounts.views import AboutView, ContactView, FeedView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('', FeedView.as_view(), name='feed'),
    path('blogs/', include('blogs.urls'), name='blogs'),
    path('about/', AboutView.as_view(), name='about'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('authentications/', include('authentications.urls')),
    path('api/', include('api.urls')),
    path('accounts/', include('accounts.urls'), name='accounts'),
    path(
        'robots.txt',
        TemplateView.as_view(
            template_name='accounts/robots.txt',
            content_type='text/plain'
        ),
        name='robots'
    ),
]


handler404 = 'accounts.views.not_found'
handler500 = 'accounts.views.bad_request'
