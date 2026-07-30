from django.db.models import QuerySet


class ExpenseQuerySet(QuerySet):
    """
    Expense model custom query.
    """
    def for_user(self,user):
        return self.filter(user=user)