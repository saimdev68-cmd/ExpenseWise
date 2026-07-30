from django.utils import timezone
from django.db.models import Q
from datetime import timedelta


def expense_filter(queryset, params):
    
    search = params.get("search", "").strip()
    category = params.get("category", "")
    payment_method = params.get("payment_method", "")
    start_date = params.get("start_date", "")
    end_date = params.get("end_date", "")
    min_amount = params.get("min_amount", "")
    max_amount = params.get("max_amount", "")
    sort = params.get("sort", "newest")

    if search:
        queryset = queryset.filter(
            Q(note__icontains=search)|
            Q(title__icontains=search)
            )

    if category:
        queryset = queryset.filter(category=category)

    if payment_method:
        queryset = queryset.filter(payment_method=payment_method)

    if start_date:
        queryset = queryset.filter(date__gte=start_date)

    if end_date:
        queryset = queryset.filter(date__lte=end_date)

    if min_amount:
        queryset = queryset.filter(amount__gte=min_amount)

    if max_amount:
        queryset = queryset.filter(amount__lte=max_amount)

    sort_options = {
        "newest": ("-date", "-created_at"),
        "oldest": ("date", "created_at"),
        "highest": ("-amount",),
        "lowest": ("amount",),
    }

    queryset = queryset.order_by(*sort_options.get(sort, ("-date", "-created_at")))
    today = timezone.localdate()
    period = params.get("period")

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