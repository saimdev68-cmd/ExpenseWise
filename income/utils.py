from django.db.models import Sum


def calculate_total_income(queryset):
    total_income = queryset.aggregate(total=Sum('amount'))['total'] or 0
    return total_income