from decimal import Decimal
from datetime import date
from dateutil.relativedelta import relativedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.utils import timezone
from django.views.generic import TemplateView

from income.models import Income
from expense.models import Expense

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        today = date.today()
        
        # 1. Last 365 Days Metrics
        one_year_ago = today - relativedelta(days=365)
        
        total_income_365 = Income.objects.filter(
            user=user, date__gte=one_year_ago, date__lte=today
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        total_expense_365 = Expense.objects.filter(
            user=user, date__gte=one_year_ago, date__lte=today
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        # 2. Current Month vs Last Month Comparison
        current_month_start = today.replace(day=1)
        last_month_start = current_month_start - relativedelta(months=1)
        last_month_end = current_month_start - relativedelta(days=1)

        # Current Month totals
        this_month_income = Income.objects.filter(
            user=user, date__gte=current_month_start, date__lte=today
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        this_month_expense = Expense.objects.filter(
            user=user, date__gte=current_month_start, date__lte=today
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        # Last Month totals
        last_month_income = Income.objects.filter(
            user=user, date__gte=last_month_start, date__lte=last_month_end
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        last_month_expense = Expense.objects.filter(
            user=user, date__gte=last_month_start, date__lte=last_month_end
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        # Percentage Changes Helper
        def calculate_change(current, previous):
            if previous > 0:
                return round(((current - previous) / previous) * 100, 1)
            return round(100.0, 1) if current > 0 else round(0.0, 1)

        income_change = calculate_change(this_month_income, last_month_income)
        expense_change = calculate_change(this_month_expense, last_month_expense)

        # Balance calculations
        current_balance = total_income_365 - total_expense_365
        this_month_balance = this_month_income - this_month_expense
        last_month_balance = last_month_income - last_month_expense
        balance_change = calculate_change(this_month_balance, last_month_balance)

        # Savings Rate calculations: ((Income - Expense) / Income) * 100
        this_month_savings_rate = 0
        if this_month_income > 0:
            this_month_savings_rate = round((this_month_balance / this_month_income) * 100)

        last_month_savings_rate = 0
        if last_month_income > 0:
            last_month_savings_rate = round((last_month_balance / last_month_income) * 100)
            
        savings_rate_change = this_month_savings_rate - last_month_savings_rate

        # Pack data into context
        context['today'] = today
        context['metrics'] = {
            'income': {
                'total': total_income_365,
                'change': income_change,
            },
            'expense': {
                'total': total_expense_365,
                'change': expense_change,
            },
            'balance': {
                'total': current_balance,
                'change': balance_change,
            },
            'savings_rate': {
                'total': this_month_savings_rate if this_month_savings_rate > 0 else 0,
                'change': savings_rate_change,
            }
        }
        return context
    
from django.http import JsonResponse
from django.db.models.functions import TruncDate
from calendar import monthrange
from django.db.models import Count

class ChartDataAPIView(LoginRequiredMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        user = request.user
        period = request.GET.get('period', 'this_month')
        today = date.today()
        
        if period == 'last_month':
            start_date = (today - relativedelta(months=1)).replace(day=1)
            end_date = start_date + relativedelta(days=monthrange(start_date.year, start_date.month)[1] - 1)
        elif period == 'last_30_days':
            start_date = today - relativedelta(days=30)
            end_date = today
        elif period == 'last_90_days':
            start_date = today - relativedelta(days=90)
            end_date = today
        else:
            start_date = today.replace(day=1)
            end_date = today

        # 1. Bar Chart: Daily Aggregations
        days_count = (end_date - start_date).days + 1
        date_list = [start_date + relativedelta(days=x) for x in range(days_count)]
        labels = [d.strftime('%d %b') for d in date_list]

        income_queryset = (
            Income.objects.filter(user=user, date__gte=start_date, date__lte=end_date)
            .values('date')
            .annotate(total=Sum('amount'))
        )
        expense_queryset = (
            Expense.objects.filter(user=user, date__gte=start_date, date__lte=end_date)
            .values('date')
            .annotate(total=Sum('amount'))
        )

        income_map = {res['date']: res['total'] for res in income_queryset}
        expense_map = {res['date']: res['total'] for res in expense_queryset}

        income_data = [float(income_map.get(d, 0.0)) for d in date_list]
        expense_data = [float(expense_map.get(d, 0.0)) for d in date_list]

        # 2. Donut Chart: Expense Categories
        cat_query = (
            Expense.objects.filter(user=user, date__gte=start_date, date__lte=end_date)
            .values('category')
            .annotate(total=Sum('amount'))
            .order_by('-total')
        )
        
        total_expense_sum = float(Expense.objects.filter(user=user, date__gte=start_date, date__lte=end_date).aggregate(Sum('amount'))['amount__sum'] or 0.0)
        
        from expense.models import ExpenseCategory
        cat_choices = dict(ExpenseCategory.choices)

        cat_labels, cat_amounts, cat_percentages = [], [], []
        for item in cat_query:
            amt = float(item['total'])
            pct = round((amt / total_expense_sum) * 100, 1) if total_expense_sum > 0 else 0
            
            raw_category = item['category']
            clean_label = cat_choices.get(raw_category, raw_category)
            
            cat_labels.append(clean_label)
            cat_amounts.append(amt)
            cat_percentages.append(pct)

        return JsonResponse({
            'bar_labels': labels,
            'income_data': income_data,
            'expense_data': expense_data,
            'donut_labels': cat_labels,
            'donut_data': cat_amounts,
            'donut_percentages': cat_percentages,
            'donut_total': total_expense_sum,
        })