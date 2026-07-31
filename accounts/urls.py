# accounts/urls.py
from django.urls import path
from .views import LoginView, RefreshView, ProfileView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('refresh/', RefreshView.as_view(), name='refresh'),
    path('me/', ProfileView.as_view(), name='profile'),
]