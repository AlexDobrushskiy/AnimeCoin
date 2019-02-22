from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from core.models import User, UserProfile


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    pass


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    pass
