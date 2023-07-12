"""
All the endpoints for the recipe app
"""

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from recipe import serializers
from core.models import Recipe


class RecipeViewSet(viewsets.ModelViewSet):
    """Endpoint for that handles creating, reading and updating recipes for current user"""  # noqa
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return the recipes for the authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Method that returns specific serializer class"""
        if self.action == 'list':
            return serializers.RecipeSerializer

        return self.serializer_class
