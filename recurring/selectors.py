
def recurring_filter(queryset,params):
    status = params.get("status")
    transaction_type = params.get("type")
    frequency = params.get("frequency")

    if transaction_type:
        queryset = queryset.filter(transaction_type=transaction_type)

    if frequency:
        queryset = queryset.filter(frequency=frequency)

    if status == "active":
        queryset = queryset.filter(is_active=True)

    elif status == "inactive":
        queryset = queryset.filter(is_active=False)

    return queryset