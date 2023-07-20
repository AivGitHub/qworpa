from django.urls import path

from accounts.views import SettingsView

urlpatterns = [
    path('settings/', SettingsView.as_view(), name='settings'),
]
