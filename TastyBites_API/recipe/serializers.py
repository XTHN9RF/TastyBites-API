"""
Serializers for recipe API app
"""

from rest_framework import serializers

from core.models import Recipe


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer that represents a recipe object"""

    class Meta:
        model = Recipe
        fields = ('id', 'title', 'ingredients', 'time_minutes', 'price', 'link')
        read_only_fields = ('id',)
