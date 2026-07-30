from django.db.models.functions import Coalesce
from django.db.models import Count, Sum
from decimal import Decimal

from expense.models import Expense
from income.models import Income


def calculate_summary(income_queryset, expense_queryset):
    total_income = income_queryset.aggregate(total=Coalesce(Sum("amount"), Decimal("0.00")))["total"]
    total_expense = expense_queryset.aggregate(total=Coalesce(Sum("amount"), Decimal("0.00")))["total"]
    income_count = income_queryset.aggregate(total=Count("id"))["total"]
    expense_count = expense_queryset.aggregate(total=Count("id"))["total"]
    net_profit = total_income - total_expense

    return {
        "income_queryset": income_queryset.order_by("-date"),
        "expense_queryset": expense_queryset.order_by("-date"),
        "total_income": total_income,
        "total_expense": total_expense,
        "net_profit": net_profit,
        "income_count": income_count,
        "expense_count": expense_count,
    }


def get_monthly_report(user, month, year):
    income_queryset = Income.objects.filter(user=user,date__year=year,date__month=month)
    expense_queryset = Expense.objects.filter(user=user,date__year=year,date__month=month)
    return calculate_summary(income_queryset,expense_queryset)

def get_yearly_report(user, year):
    income_queryset = Income.objects.filter(user=user,date__year=year)
    expense_queryset = Expense.objects.filter(user=user,date__year=year,)
    return calculate_summary(income_queryset,expense_queryset,)

def get_custom_report(user, start_date, end_date):
    income_queryset = Income.objects.filter(user=user,date__range=(start_date, end_date))
    expense_queryset = Expense.objects.filter(user=user,date__range=(start_date, end_date),)
    return calculate_summary(income_queryset,expense_queryset)