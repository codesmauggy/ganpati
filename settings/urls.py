from django.urls import path
from .views import SettingsView

urlpatterns = [
    # Remove 'api/' prefix – we will include this under 'api/' in the main urls
    path('settings/', SettingsView.as_view(), name='settings'),
]