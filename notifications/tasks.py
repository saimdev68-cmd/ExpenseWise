from recurring.models import RecurringTransaction
from django.contrib.auth import get_user_model
from expense.models import Expense
from django.utils import timezone

from django.urls import reverse
from celery import shared_task
from datetime import timedelta

from .signals import create_notification
from .models import Notification


User = get_user_model()


@shared_task
def daily_expense_reminder():
    today = timezone.localdate()
    users = User.objects.filter(is_active=True)
    for user in users:
        has_expense = Expense.objects.filter(user=user,date=today).exists()
        if not has_expense:
            create_notification(user=user,
                title="Expense Reminder",
                message=("Don't forget to add today's expenses."),
                notification_type=Notification.NotificationType.REMINDER,
                url=reverse("expense_add")
            )

@shared_task
def monthly_report_ready():
    users = User.objects.all()
    for user in users:
        create_notification(
            user=user,
            title="Monthly Report Ready",
            message=("Your monthly financial report is ready."),
            notification_type=Notification.NotificationType.REPORT,
            url=reverse("reports_monthly"))


@shared_task
def upcoming_recurring_payment():
    today = timezone.localdate()
    upcoming_date = today + timedelta(days=3)
    recurring_transactions = RecurringTransaction.objects.filter(
            next_run__lte=upcoming_date,
            next_run__gte=today
        )
    for transaction in recurring_transactions:
        day_left = (transaction.next_run - today).days
        create_notification(
            user=transaction.user,
            title="Upcoming Payment",
            message=f"{transaction.title} will be processed in {day_left} days.",
            notification_type=
            Notification.NotificationType.RECURRING,
            url=reverse("recurring_detail",
                kwargs={"pk": transaction.pk}
            )
        )

@shared_task
def delete_old_notifications():
    limit_date = timezone.now()-timedelta(days=90)
    Notification.objects.filter(created_at__lt=limit_date).delete()