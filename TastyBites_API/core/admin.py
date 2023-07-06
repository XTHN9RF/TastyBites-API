"""
Customized django admin panel
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy

from .models import User


class CustomUserAdmin(UserAdmin):
    """Customizes admin panel for user models"""
    ordering = ('id',)
    list_display = ('email', 'name', 'is_active', 'is_staff')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (
            gettext_lazy('Permissions'),
            {'fields': ('is_active', 'is_staff', 'is_superuser')}
        ),
        (gettext_lazy('Important dates'),
         {'fields': ('last_login',)})
    )
    readonly_fields = ('last_login',)


admin.site.register(User, CustomUserAdmin)
