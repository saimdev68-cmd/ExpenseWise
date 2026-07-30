from django.db.models.functions import Coalesce
from django.db.models import DecimalField
from django.utils import timezone

from django.db.models import Sum
from decimal import Decimal


def current_year():
    return timezone.now().year


def calculate_total_budget(queryset):
    return queryset.aggregate(
            total_budget=Coalesce(
                Sum("amount"),
                Decimal("0.00"),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            ),
        )


def calculate_total_spend(queryset):
    return sum(
            (budget.spent for budget in queryset),
            start=Decimal("0.00"),
        )