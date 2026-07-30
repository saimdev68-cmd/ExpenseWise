from django.db.models import QuerySet


class RecurringQuerySet(QuerySet):
    """
    Recurring transaction model custom query.
    """
    def for_user(self,user):
        return self.filter(user=user)