from dateutil.relativedelta import relativedelta
from operator import attrgetter
from decimal import Decimal
from itertools import chain
from datetime import date

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.db.models import Sum
from calendar import monthrange

from expense.models import Expense, ExpenseCategory
from recurring.models import RecurringTransaction 
from budgets.models import Budget
from income.models import Income

from django.db.models import Sum, Q
from django.db.models.functions import Coalesce
from django.db.models import DecimalField, Value


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    User Dashboard View.
    """
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        today = date.today()
        
        # 1. Top Metrics Calculation (Last 365 days & Month over Month)
        one_month_ago = today - relativedelta(months=1)
        current_month_start = today.replace(day=1)
        last_month_start = current_month_start - relativedelta(months=1)
        last_month_end = current_month_start - relativedelta(days=1)

        expense_stats = (
            Expense.objects
            .filter(user=user)
            .aggregate(
                total=Coalesce(
                    Sum(
                        "amount",
                        filter=Q(
                            date__gte=one_month_ago,
                            date__lte=today,
                        ),
                    ),
                    Value(Decimal("0.00")),
                    output_field=DecimalField(),
                ),
                this_month=Coalesce(
                    Sum(
                        "amount",
                        filter=Q(
                            date__gte=current_month_start,
                            date__lte=today,
                        ),
                    ),
                    Value(Decimal("0.00")),
                    output_field=DecimalField(),
                ),
                last_month=Coalesce(
                    Sum(
                        "amount",
                        filter=Q(
                            date__gte=last_month_start,
                            date__lte=last_month_end,
                        ),
                    ),
                    Value(Decimal("0.00")),
                    output_field=DecimalField(),
                ),
            )
        )

        income_stats = (
            Income.objects
            .filter(user=user)
            .aggregate(
                total=Coalesce(
                    Sum(
                        "amount",
                        filter=Q(
                            date__gte=one_month_ago,
                            date__lte=today,
                        ),
                    ),
                    Value(Decimal("0.00")),
                    output_field=DecimalField(),
                ),
                this_month=Coalesce(
                    Sum(
                        "amount",
                        filter=Q(
                            date__gte=current_month_start,
                            date__lte=today,
                        ),
                    ),
                    Value(Decimal("0.00")),
                    output_field=DecimalField(),
                ),
                last_month=Coalesce(
                    Sum(
                        "amount",
                        filter=Q(
                            date__gte=last_month_start,
                            date__lte=last_month_end,
                        ),
                    ),
                    Value(Decimal("0.00")),
                    output_field=DecimalField(),
                ),
            )
        )

        total_income_30 = income_stats["total"]
        total_expense_30 = expense_stats["total"]

        this_month_income = income_stats["this_month"]
        this_month_expense = expense_stats['this_month']
        last_month_income = income_stats["last_month"]
        last_month_expense = expense_stats["last_month"]

        def calculate_change(current, previous):
            if previous > 0:
                return round(((current - previous) / previous) * 100, 1)
            return round(100.0, 1) if current > 0 else round(0.0, 1)

        current_balance = total_income_30 - total_expense_30
        this_month_balance = this_month_income - this_month_expense
        last_month_balance = last_month_income - last_month_expense

        savings_rate = round((current_balance / total_income_30) * 100) if total_income_30 > 0 else 0
        this_month_savings_rate = round((this_month_balance / this_month_income) * 100) if this_month_income > 0 else 0
        last_month_savings_rate = round((last_month_balance / last_month_income) * 100) if last_month_income > 0 else 0

        # 2. Budget Overview (Ordered by Spend Percentage)
        budgets = list(
            Budget.objects.for_user(user)
            .with_spent_annotation()
            .filter(
                month=today.month,
                year=today.year,
            )
        )
        budgets.sort(key=lambda x: x.percentage_used, reverse=True)
        top_budgets = budgets[:4]

        # 3. Recent Transactions (Combining Income & Expense)
        incomes = Income.objects.filter(user=user).order_by('-date', '-created_at')[:5]
        expenses = Expense.objects.filter(user=user).order_by('-date', '-created_at')[:5]
        
        # Mark types for the template
        for inc in incomes: inc.is_income = True
        for exp in expenses: exp.is_income = False
        
        recent_transactions = sorted(
            chain(incomes, expenses),
            key=attrgetter('date', 'created_at'),
            reverse=True
        )[:5]

        # 4. Upcoming Recurring Payments
        upcoming_recurring = RecurringTransaction.objects.filter(
            user=user, is_active=True, next_run__gte=today
        ).order_by('next_run')[:4]

        context.update({
            'today': today,
            'metrics': {
                'income': {'total': total_income_30, 'change': calculate_change(this_month_income, last_month_income)},
                'expense': {'total': total_expense_30, 'change': calculate_change(this_month_expense, last_month_expense)},
                'balance': {'total': current_balance, 'change': calculate_change(this_month_balance, last_month_balance)},
                'savings_rate': {'total': savings_rate if savings_rate > 0 else 0, 'change': this_month_savings_rate - last_month_savings_rate}
            },
            'budgets': top_budgets,
            'recent_transactions': recent_transactions,
            'upcoming_recurring': upcoming_recurring,
        })
        return context


class ChartDataAPIView(LoginRequiredMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        user = request.user
        chart_type = request.GET.get('chart_type', 'bar') # bar, donut, trend
        period = request.GET.get('period', 'this_month')
        today = date.today()
        
        # Determine Date Range
        if period == 'last_month':
            start_date = (today - relativedelta(months=1)).replace(day=1)
            end_date = start_date + relativedelta(days=monthrange(start_date.year, start_date.month)[1] - 1)
        elif period == 'last_30_days':
            start_date = today - relativedelta(days=30)
            end_date = today
        elif period == 'last_90_days':
            start_date = today - relativedelta(days=90)
            end_date = today
        elif period == 'last_6_months':
            start_date = today - relativedelta(months=6)
            end_date = today
        elif period == 'this_year':
            start_date = today.replace(month=1, day=1)
            end_date = today
        elif period == 'last_year':
            start_date = (today - relativedelta(years=1)).replace(month=1, day=1)
            end_date = start_date.replace(month=12, day=31)
        elif period == 'last_365_days':
            start_date = today - relativedelta(days=365)
            end_date = today
        else: # this_month
            start_date = today.replace(day=1)
            end_date = today

        # ------------------- BAR CHART (Income vs Expense) -------------------
        if chart_type == 'bar':
            days_count = (end_date - start_date).days + 1
            date_list = [start_date + relativedelta(days=x) for x in range(days_count)]
            labels = [d.strftime('%d %b') for d in date_list]

            inc_qs = Income.objects.filter(user=user, date__gte=start_date, date__lte=end_date).values('date').annotate(total=Sum('amount'))
            exp_qs = Expense.objects.filter(user=user, date__gte=start_date, date__lte=end_date).values('date').annotate(total=Sum('amount'))

            inc_map = {res['date']: res['total'] for res in inc_qs}
            exp_map = {res['date']: res['total'] for res in exp_qs}

            return JsonResponse({
                'labels': labels,
                'income_data': [float(inc_map.get(d, 0.0)) for d in date_list],
                'expense_data': [float(exp_map.get(d, 0.0)) for d in date_list],
            })

        # ------------------- DONUT CHART (Expense Categories) -------------------
        elif chart_type == 'donut':
            cat_query = Expense.objects.filter(user=user, date__gte=start_date, date__lte=end_date).values('category').annotate(total=Sum('amount')).order_by('-total')
            total_sum = float(Expense.objects.filter(user=user, date__gte=start_date, date__lte=end_date).aggregate(Sum('amount'))['amount__sum'] or 0.0)
            
            cat_choices = dict(ExpenseCategory.choices)
            labels, amounts, percentages = [], [], []
            
            for item in cat_query:
                amt = float(item['total'])
                pct = round((amt / total_sum) * 100, 1) if total_sum > 0 else 0
                labels.append(cat_choices.get(item['category'], item['category']))
                amounts.append(amt)
                percentages.append(pct)

            return JsonResponse({
                'labels': labels,
                'data': amounts,
                'percentages': percentages,
                'total': total_sum,
            })

        # ------------------- TREND CHART (Spending Trend) -------------------
        elif chart_type == 'trend':
            # Group by month for long periods, by day for short periods
            days_diff = (end_date - start_date).days
            labels, data = [], []
            
            if days_diff > 90:
                # Group by Month
                current = start_date.replace(day=1)
                while current <= end_date:
                    month_end = current + relativedelta(days=monthrange(current.year, current.month)[1] - 1)
                    if month_end > end_date: month_end = end_date
                    total = Expense.objects.filter(user=user, date__gte=current, date__lte=month_end).aggregate(Sum('amount'))['amount__sum'] or 0.0
                    labels.append(current.strftime('%b %Y'))
                    data.append(float(total))
                    current += relativedelta(months=1)
            else:
                # Group by Day
                for i in range(days_diff + 1):
                    current = start_date + relativedelta(days=i)
                    total = Expense.objects.filter(user=user, date=current).aggregate(Sum('amount'))['amount__sum'] or 0.0
                    labels.append(current.strftime('%d %b'))
                    data.append(float(total))

            return JsonResponse({'labels': labels, 'data': data})

        return JsonResponse({'error': 'Invalid chart type'}, status=400)