from django.db.models import QuerySet


class NotificationQuerySet(QuerySet):
    """
    Notification model custom query.
    """
    def for_user(self,user):
        return self.filter(user=user)