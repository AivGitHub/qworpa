from django.urls import path

from accounts.views import SettingsView, SubscriptionsView

urlpatterns = [
    path('settings/', SettingsView.as_view(), name='settings'),
    path('subscriptions/', SubscriptionsView.as_view(), name='subscriptions'),
]
