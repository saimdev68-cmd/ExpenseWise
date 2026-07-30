from django.contrib import admin

from .models import Income


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    """
    Income model admin.
    """
    list_display = ("user", "title", "amount", "category", "date", "created_at")
    list_filter = ("category", "date", "created_at")
    search_fields = ("title", "note", "user__email")
    ordering = ("-date", "-created_at")
    date_hierarchy = "date"
    readonly_fields = ("created_at", "updated_at")
    list_per_page = 25
    fieldsets = (
        ("Income Information", {
            "fields": ("user", "title", "amount", "category", "is_recurring", "date", "note")
        }),
        ("System Information", {
            "fields": ("created_at", "updated_at"),"classes": ("collapse",)
        }),
    )