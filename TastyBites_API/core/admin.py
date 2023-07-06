"""
Customized django admin panel
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


class CustomUserAdmin(UserAdmin):
    """Customizes admin panel for user models"""
    ordering = ('id',)
    list_display = ('email', 'name', 'is_active', 'is_staff')


admin.site.register(User, CustomUserAdmin)
