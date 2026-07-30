from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, PendingEmail


class PendingEmailInline(admin.StackedInline):
    model = PendingEmail
    extra = 0
    can_delete = True
    max_num = 1


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("-date_joined",)

    list_display = ("email","is_active","is_staff","is_superuser")
    list_filter = ("is_active","is_staff","is_superuser","date_joined")
    search_fields = ("email","name")
    readonly_fields = ("last_login","date_joined","updated_at")
    inlines = [PendingEmailInline]
    fieldsets = (
        ("User Information",{
            "fields": ("email","name","password")
        }),
        ("Permissions",{
            "fields": ("is_active","is_staff","is_superuser","groups","user_permissions",)
        }),
        ("Important Dates",{
            "fields": ("last_login","date_joined","updated_at")
        })
    )

    add_fieldsets = (
        (None,{
            "classes": ("wide",),
            "fields": ("email","name","password1","password2","is_active","is_staff","is_superuser"),
        }),
    )