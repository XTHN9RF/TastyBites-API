"""
File contains all the views for the user app
"""

from rest_framework import generics

from .serializer import UserSerializer


class UserCreateView(generics.CreateAPIView):
    """ View that helps to create new user """
    serializer_class = UserSerializer
