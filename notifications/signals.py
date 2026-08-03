from django.db.models.signals import post_save
from django.dispatch import receiver
from expense.models import Expense
from budgets.models import Budget

from income.models import Income
from django.urls import reverse
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.db.models import DecimalField
from decimal import Decimal

from .models import Notification


def create_notification( *,user,title,message,notification_type,url=None):
    exists = Notification.objects.filter(user=user,title=title,message=message,url=url,is_read=False).exists()
    if not exists:
        return Notification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            url=url
        )

@receiver(post_save, sender=Expense)
def check_budget_exceeded(sender,instance,created,**kwargs):
    if not created:
        return
    budgets = Budget.objects.filter(user=instance.user,
    category=instance.category,
    month=instance.date.month,
    year=instance.date.year)
    for budget in budgets:
        if budget.spent > budget.amount:
            create_notification(
                user=instance.user,
                title="Budget Exceeded",
                message=(f"You have exceeded your {budget.get_category_display()} budget."),
                notification_type=
                Notification.NotificationType.BUDGET,
                url=reverse("budget_detail",kwargs={"pk": budget.pk})
            )

@receiver(post_save,sender=Income)
def income_created_notification(sender,instance,created,**kwargs):
    if created and getattr(instance,"is_recurring",False):
        create_notification(
            user=instance.user,
            title="Income Added",
            message=f"{instance.title} has been added successfully.",
            notification_type=Notification.NotificationType.RECURRING,
            url=reverse("income_detail",kwargs={"pk": instance.pk}))

@receiver(post_save,sender=Expense)
def recurring_expense_notification(sender,instance,created,**kwargs):
    if created and getattr(instance,"is_recurring",False):
        create_notification(
            user=instance.user,
            title="Payment Created",
            message=f"{instance.title} payment has been created.",
            notification_type=Notification.NotificationType.RECURRING,
            url=reverse("expense_detail",kwargs={"pk": instance.pk}))