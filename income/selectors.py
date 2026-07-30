from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
from decimal import Decimal


def filter_income(queryset, params):

    search = params.get("search")
    category = params.get("category")
    sort = params.get("sort", "newest")
    from_date = params.get("from_date")
    to_date = params.get("to_date")
    min_amount = params.get("min_amount")
    max_amount = params.get("max_amount")
    period = params.get("period")
    today = timezone.localdate()

    if search:
        queryset = queryset.filter(
            Q(title__icontains=search) |
            Q(category__icontains=search) |
            Q(note__icontains=search)
        )

    if category:
        queryset = queryset.filter(category=category)

    if from_date:
        queryset = queryset.filter(date__gte=from_date)
    if to_date:
        queryset = queryset.filter(date__lte=to_date)

    if min_amount:
        queryset = queryset.filter(amount__gte=Decimal(min_amount))
    if max_amount:
        queryset = queryset.filter(amount__lte=Decimal(max_amount))

    sort_options = {
        "newest": ("-date", "-created_at"),
        "oldest": ("date", "created_at"),
        "highest": ("-amount",),
        "lowest": ("amount",),
    }

    queryset = queryset.order_by(
        *sort_options.get(sort, ("-date", "-created_at"))
    )

    if period == "today":
        queryset = queryset.filter(date=today)

    elif period == "yesterday":
        queryset = queryset.filter(date=today - timedelta(days=1))

    elif period == "last_7_days":
        queryset = queryset.filter(date__gte=today - timedelta(days=6))

    elif period == "this_month":
        queryset = queryset.filter(
            date__year=today.year,
            date__month=today.month,
        )

    elif period == "last_month":
        if today.month == 1:
            year = today.year - 1
            month = 12
        else:
            year = today.year
            month = today.month - 1

        queryset = queryset.filter(
            date__year=year,
            date__month=month,
        )

    elif period == "this_year":
        queryset = queryset.filter(date__year=today.year)

    return queryset