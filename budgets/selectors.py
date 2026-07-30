
def budget_filter(queryset, params):
    month = params.get("month")
    year = params.get("year",)
    category = params.get("category")
    sort = params.get("sort", "newest")

    if month:
        queryset = queryset.filter(month=month)

    if year:
        queryset = queryset.filter(year=year)

    if category:
        queryset = queryset.filter(category=category)

    ordering = {
        "newest": ("-year", "-month", "category"),
        "oldest": ("year", "month", "category"),
        "highest": ("-amount",),
        "lowest": ("amount",),
    }

    queryset = queryset.order_by(*ordering.get(sort, ordering["newest"]))
    return queryset