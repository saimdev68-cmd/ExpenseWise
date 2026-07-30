from django.contrib import admin

from .models import RecurringTransaction


@admin.register(RecurringTransaction)
class RecurringTransactionAdmin(admin.ModelAdmin):
    """
    Recurring transaction model admin.
    """
    list_display = ("user","title","transaction_type","amount","frequency","next_run","status","is_active","created_at")
    list_filter = ("transaction_type","frequency","is_active","created_at")
    search_fields = ("title","note","user__email")
    ordering = ("-created_at",)
    readonly_fields = ("last_generated_date","created_at","updated_at")
    date_hierarchy = "next_run"
    list_per_page = 25
    fieldsets = (
        ("Basic Information",{
            "fields": ("user","title","transaction_type","amount","note")
        }),
        ("Categories",{
            "fields": ("income_category","expense_category","payment_method")
        }),
        ("Schedule",{
            "fields": ("frequency","start_date","end_date","next_run","last_generated_date")
        }),
        ("Status",{
            "fields": ("is_active",)
        }),
        ("System Information", {
            "fields": ("created_at", "updated_at"),"classes": ("collapse",)
        }),
    )

    @admin.display(description="Status")
    def status(self, obj):
        return obj.get_status()

    @admin.display(description="Type")
    def transaction_type(self, obj):
        return obj.get_transaction_type_display()

    @admin.display(description="Frequency")
    def frequency(self, obj):
        return obj.get_frequency_display()