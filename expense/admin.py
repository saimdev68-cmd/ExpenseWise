from django.contrib import admin

from .models import Expense


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    """
    Expense model admin.
    """
    list_display = ("user","title","amount","category","payment_method","date","created_at")
    list_filter = ("category","payment_method","date")
    search_fields = ("title","user__email","note")
    ordering = ("-date","-created_at")
    date_hierarchy = "date"
    readonly_fields = ("created_at","updated_at")
    list_per_page = 25
    fieldsets = (
        ("Expense Information",{
            "fields": ("user","title","amount","category","payment_method",'is_recurring',"date","note")
        }),
        ("Timestamps",{
            "fields": ("created_at","updated_at"),"classes": ("collapse",)
        }),
    )
    