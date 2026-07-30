from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Notification model admin.
    """
    list_display = ("user","title","notification_type","is_read","created_at")
    list_filter = ("is_read","notification_type")
    search_fields = ("title","user__email")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)
    list_per_page = 25
    fieldsets = (
        ("Notification Information", {
            "fields": ("user", "title", "message", "notification_type", "url", "is_read")
        }),
        ("System Information", {
            "fields": ("created_at", "updated_at"),"classes": ("collapse",)
        }),
    )