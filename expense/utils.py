from django.db.models import Sum


def calculate_total_expense(queryset):
    total_expense = queryset.aggregate(total=Sum('amount'))['total'] or 0
    return total_expense