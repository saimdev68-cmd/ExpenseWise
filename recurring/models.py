from expense.models import ExpenseCategory, PaymentMethod
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator

from django.core.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from django.db import models , transaction

from expense.models import Expense
from django.utils import timezone
from income.models import Income

from django.conf import settings
from django.urls import reverse
from decimal import Decimal

from .querysets import RecurringQuerySet


class TransactionType(models.TextChoices):
    INCOME = "INCOME", _("Income")
    EXPENSE = "EXPENSE", _("Expense")


class Frequency(models.TextChoices):
    DAILY = "DAILY", _("Daily")
    WEEKLY = "WEEKLY", _("Weekly")
    MONTHLY = "MONTHLY", _("Monthly")
    YEARLY = "YEARLY", _("Yearly")

class Status(models.TextChoices):
    ACTIVE = "ACTIVE", _("Active")
    INACTIVE = "INACTIVE", _("Inactive")
    FINISHED = "FINISHED", _("Finished")


class RecurringTransaction(models.Model):
    """
    Stores a user's recurring transaction.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="recurring_transactions")
    transaction_type = models.CharField(max_length=10,choices=TransactionType.choices,db_index=True)
    title = models.CharField(max_length=255,help_text=_("Example: Monthly Salary, Netflix, House Rent"))

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('1.00'))],
        help_text=_("Enter the amount.")
    )

    income_category = models.CharField(max_length=20,choices=Income.Category.choices,blank=True)
    expense_category = models.CharField(max_length=20,choices=ExpenseCategory.choices,blank=True)
    payment_method = models.CharField(max_length=20,choices=PaymentMethod.choices,blank=True)

    frequency = models.CharField(max_length=10,choices=Frequency.choices,db_index=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True,blank=True)
    next_run = models.DateField(db_index=True)
    last_generated_date = models.DateField(null=True,blank=True)
    note = models.TextField(blank=True,help_text=_("Optional note about this recurring transaction."))
    is_active = models.BooleanField(default=True,db_index=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = RecurringQuerySet.as_manager()

    class Meta:
        db_table = 'recurring_transactions'
        verbose_name = _("Recurring Transaction")
        verbose_name_plural = _("Recurring Transactions")
        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["user", "next_run", "is_active"],name="recurring_user_next_idx"),
            models.Index(fields=["user","transaction_type"],name="recurring_user_transaction_idx"),
            models.Index(fields=['user','frequency'],name="recurring_user_frequency_idx"),
            models.Index(fields=["user",'is_active'],name="recurring_user_is_active_idx"),
            models.Index(fields=["is_active", "next_run"],name="recurring_scheduler_idx")
        ]

        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(
                        transaction_type=TransactionType.INCOME,
                        income_category__gt=""
                    )
                    |
                    models.Q(
                        transaction_type=TransactionType.EXPENSE,
                        expense_category__gt="",
                        payment_method__gt=""
                    )
                ),
                name="valid_recurring_transaction"
            )
        ]

    def __str__(self):
        return f"{self.title} - {self.get_transaction_type_display()}"

    def get_absolute_url(self):
        return reverse("recurring_detail", kwargs={"pk": self.pk})
    

    def clean(self):
        super().clean()
            
        if self.start_date and self.next_run:
            if self.next_run < self.start_date:
                raise ValidationError({"next_run": _("Next run cannot be before start date.")})

        if self.end_date and self.end_date < self.start_date:
            raise ValidationError({"end_date": _("End date cannot be before start date.")})

        if self.transaction_type == TransactionType.INCOME:

            if not self.income_category:
                raise ValidationError({"income_category":_("Please choose an income category.")})

            self.expense_category = ""
            self.payment_method = ""

        elif self.transaction_type == TransactionType.EXPENSE:

            if not self.expense_category:
                raise ValidationError({"expense_category":_("Please choose an expense category.")})

            if not self.payment_method:
                raise ValidationError({"payment_method":_("Please choose a payment method.")})

            self.income_category = ""

    def save(self, *args, **kwargs):
        if self.title:
            self.title = self.title.strip()
        if self.note:
            self.note = self.note.strip()
        if not self.pk and not self.next_run:
            self.next_run = self.start_date
        self.full_clean()
        return super().save(*args, **kwargs)
    
    def calculate_next_run(self, from_date=None):
        if from_date is None:
            from_date = self.next_run

        if self.frequency == Frequency.DAILY:
            return from_date + timezone.timedelta(days=1)

        if self.frequency == Frequency.WEEKLY:
            return from_date + timezone.timedelta(weeks=1)

        if self.frequency == Frequency.MONTHLY:
            return from_date + relativedelta(months=1)

        if self.frequency == Frequency.YEARLY:
            return from_date + relativedelta(years=1)

        return from_date

    def advance_next_run(self):
        self.next_run = self.calculate_next_run()

    def is_finished(self):
        if self.end_date:
            return timezone.localdate() > self.end_date
        return False

    def can_run(self):
        return self.is_active and not self.is_finished() and self.next_run <= timezone.localdate()

    @property
    def get_status(self):
        if self.is_finished():
            return Status.FINISHED

        if self.is_active:
            return Status.ACTIVE

        return Status.INACTIVE

    def days_until_next_run(self):
        return (self.next_run - timezone.localdate()).days

    @transaction.atomic
    def run_now(self):
        if not self.can_run():
            return None

        if self.last_generated_date == self.next_run:
            return None

        if self.transaction_type == TransactionType.INCOME:
            transaction_obj = Income.objects.create(
                user=self.user,
                title=self.title,
                amount=self.amount,
                category=self.income_category,
                date=self.next_run,
                note=self.note,
                is_recurring=True,
            )
        else:
            transaction_obj = Expense.objects.create(
                user=self.user,
                title=self.title,
                amount=self.amount,
                category=self.expense_category,
                payment_method=self.payment_method,
                date=self.next_run,
                note=self.note,
                is_recurring=True,
            )

        self.last_generated_date = self.next_run
        self.advance_next_run()

        if self.end_date and self.next_run > self.end_date:
            self.is_active = False

        self.save(
            update_fields=[
                "next_run",
                "last_generated_date",
                "is_active",
                "updated_at",
            ]
        )

        return transaction_obj