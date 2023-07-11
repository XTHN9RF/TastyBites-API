"""
File contains all the views for the user app
"""

from rest_framework.response import Response
from rest_framework import (status,
                            generics)
from rest_framework.views import APIView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model

from . import serializers
from . import authentication


class RegistrationApiView(APIView):
    """Handle creating user accounts"""
    serializer_class = serializers.UserSerializer

    def post(self, request):
        """Handle creating user accounts by checking if the data is valid and returning an access and refresh token"""  # noqa
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()

            user = get_user_model().objects.get(email=request.data['email'])

            response = Response()

            access_token = authentication.create_access_token(user.id)
            refresh_token = authentication.create_refresh_token(user.id)

            response.set_cookie(key="refresh_token",
                                value=refresh_token, httponly=True)

            response.data = {
                'token': access_token,
                'message': 'User created successfully'
            }
            response.status_code = status.HTTP_201_CREATED
            return response

        return Response({"errorMessage": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)


class LoginApiView(APIView):
    """Handle logging in user accounts"""

    def post(self, request):
        """Login a user by checking email and password and returning an access and refresh token"""  # noqa
        user = get_user_model().objects.get(email=request.data['email'])

        if not user:
            return Response({'errorMessage': 'User with such email not found'},
                            status=status.HTTP_403_FORBIDDEN)

        if not user.check_password(request.data['password']):
            return Response({'errorMessage': 'Wrong password'},
                            status=status.HTTP_403_FORBIDDEN)

        access_token = authentication.create_access_token(user.id)
        refresh_token = authentication.create_refresh_token(user.id)

        response = Response()
        response.set_cookie(key="refresh_token",
                            value=refresh_token, httponly=True)

        response.data = {
            'token': access_token,
            'message': 'User logged in successfully'
        }
        response.status_code = status.HTTP_200_OK
        return response


class RefreshApiView(APIView):
    """Handle refreshing access token"""

    def get(self, request):
        """Refresh access token by checking validity of refresh token and user data, then returns a new access token"""  # noqa
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({'errorMessage': 'No refresh token'},
                            status=status.HTTP_403_FORBIDDEN)

        user_id = authentication.decode_refresh_token(refresh_token)
        if not user_id:
            return Response({'errorMessage': 'Invalid refresh token'},
                            status=status.HTTP_403_FORBIDDEN)

        user = get_user_model().objects.get(id=user_id)
        if not user:
            return Response({'errorMessage': 'User not found'},
                            status=status.HTTP_403_FORBIDDEN)

        access_token = authentication.create_access_token(user.id)
        response = Response()
        response.data = {
            'token': access_token,
            'message': 'Access token refreshed successfully'
        }
        response.status_code = status.HTTP_200_OK
        return response


class ManageUserApiView(generics.RetrieveUpdateAPIView, LoginRequiredMixin):
    """Handle updating and retrieving user profile"""
    serializer_class = serializers.UserSerializer

    def get_object(self):
        """Retrieves and returns authenticated user object"""
        return self.request.user
