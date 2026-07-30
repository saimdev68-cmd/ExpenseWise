from django.db.models import QuerySet


class IncomeQuerySet(QuerySet):
    """
    Income model custom query.
    """
    def for_user(self, user):
        return self.filter(user=user)