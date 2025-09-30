from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'theme', 'default_privacy', 'created_at']
    list_filter = ['theme', 'default_privacy', 'is_staff', 'is_active']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Thing Journal Settings', {
            'fields': ('thing_face', 'theme', 'background_music', 'music_volume', 'default_privacy')
        }),
    )
