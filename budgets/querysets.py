from django.db.models import Sum, OuterRef, Subquery, DecimalField, Value
from django.db.models.functions import Coalesce
from django.db.models import QuerySet

from expense.models import Expense
from decimal import Decimal


class BudgetQuerySet(QuerySet):
    """
    Budget model custom query.
    """
    def for_user(self,user):
        return self.filter(user=user)
    
    def with_spent_annotation(self):
        spent_subquery = Expense.objects.filter(
            user=OuterRef('user'),
            category=OuterRef('category'),
            date__year=OuterRef('year'),
            date__month=OuterRef('month')
        ).values('user', 'category', 'date__year', 'date__month').annotate(
            total=Coalesce(
                Sum('amount'), 
                Value(Decimal('0.00')), 
                output_field=DecimalField(max_digits=12, decimal_places=2)
            )
        ).values('total')
        
        return self.annotate(
            _spent_annotated=Coalesce(
                Subquery(spent_subquery[:1]),
                Value(Decimal('0.00')),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            )
        )