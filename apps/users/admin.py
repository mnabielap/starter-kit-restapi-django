from django.contrib import admin
from apps.users.models import User, Token

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'role', 'is_email_verified', 'is_active', 'created_at')
    search_fields = ('email', 'name')
    list_filter = ('role', 'is_email_verified', 'is_active')
    ordering = ('-created_at',)

@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'expires', 'blacklisted', 'created_at')
    search_fields = ('user__email', 'token')
    list_filter = ('type', 'blacklisted')