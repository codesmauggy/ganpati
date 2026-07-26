from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('ERP Role', {'fields': ('role', 'full_name')}),
    )
    list_display = ('username', 'email', 'full_name', 'role', 'is_active')
    list_filter = ('role', 'is_active')

admin.site.register(User, CustomUserAdmin)