from django.contrib import admin

from .models import Budget


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    """
    Budget model admin.
    """
    list_display = ("user","category","amount","month","year","created_at")
    list_filter = ("category","month","year","created_at")
    search_fields = ("user__email","category")
    ordering = ("-year","-month","category")
    readonly_fields = (
        "created_at",
        "updated_at",
        "spent_display",
        "remaining_display",
        "percentage_display",
        "status_display",
        "warning_display"
    )
    list_per_page = 25
    fieldsets = (
        ("Budget Information",{
            "fields": ("user","category","amount","month","year")
        }),
        ("Budget Summary",{
            "fields": ("spent_display","remaining_display","percentage_display","status_display","warning_display")
        }),
        ("System Information",{
            "fields": ("created_at","updated_at"),"classes": ("collapse",)
        }),
    )

    @admin.display(description="Spent")
    def spent_display(self, obj):
        return f"Rs{obj.spent:.2f}"

    @admin.display(description="Remaining")
    def remaining_display(self, obj):
        return f"Rs{obj.remaining:.2f}"

    @admin.display(description="Used")
    def percentage_display(self, obj):
        return f"{obj.percentage_used}%"

    @admin.display(description="Status")
    def status_display(self, obj):
        return obj.status

    @admin.display(description="Warning")
    def warning_display(self, obj):
        return obj.warning_message if obj.warning_message else "-"