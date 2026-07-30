from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.db import models

from .querysets import NotificationQuerySet


class Notification(models.Model):
    """
    Stores a user's notification.
    """

    class NotificationType(models.TextChoices):
        BUDGET = "BUDGET", _("Budget")
        EXPENSE = "EXPENSE", _("Expense")
        INCOME = "INCOME", _("Income")
        RECURRING = "RECURRING", _("Recurring")
        REMINDER = "REMINDER", _("Reminder")
        SYSTEM = "SYSTEM", _("System")

    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="notifications")
    title = models.CharField(max_length=255)

    message = models.TextField()
    notification_type = models.CharField(max_length=20,choices=NotificationType.choices,default=NotificationType.SYSTEM)
    url = models.CharField(max_length=500,blank=True,null=True)
    
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = NotificationQuerySet.as_manager()

    class Meta:
        db_table = "notifications"
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} - {self.title}"

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=["is_read"])