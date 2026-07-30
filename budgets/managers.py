from django.db.models import Manager

from .querysets import BudgetQuerySet


class BudgetManager(Manager):
    """
    Budget model manager.
    """
    def get_queryset(self):
        return BudgetQuerySet(self.model, using=self._db)
    
    def with_spent(self):
        return self.get_queryset().with_spent_annotation()

    def for_user(self,user):
        return self.get_queryset().for_user(user)