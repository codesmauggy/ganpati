# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    # Add 'fullName' and 'cid' to the fieldsets
    fieldsets = UserAdmin.fieldsets + (
        ('ERP Role', {'fields': ('role', 'fullName', 'cid')}),
    )
    # Display these columns in the user list
    list_display = ('username', 'fullName', 'email', 'role', 'is_active')
    # Allow searching by fullName and username
    search_fields = ('username', 'fullName', 'email')
    # Optional: order by fullName
    # ordering = ('fullName',)

admin.site.register(User, CustomUserAdmin)