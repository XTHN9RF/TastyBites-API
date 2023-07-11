"""
URL configuration for user app
"""

from django.urls import path

from .views import *

app_name = 'user'

urlpatterns = [
    path('create/', RegistrationApiView.as_view(), name='create_user'),
    path('login/', LoginApiView.as_view(), name='login_user'),
    path('refresh/', RefreshApiView.as_view(), name='refresh_token'),
]
