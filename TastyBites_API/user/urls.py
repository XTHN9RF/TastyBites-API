"""
URL configuration for user app
"""

from django.urls import path

from . import views

app_name = 'user'

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create_user'),
    path('token/', views.CreateTokenView.as_view(), name='login_user'),
    path('manage/', views.ManageUserView.as_view(), name='manage_user'),
]
