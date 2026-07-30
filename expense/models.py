from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

from django.utils import timezone
from django.conf import settings
from django.urls import reverse

from django.db import models
from decimal import Decimal

from .querysets import ExpenseQuerySet


class ExpenseCategory(models.TextChoices):
    FOOD = "FOOD", _("Food")
    TRANSPORT = "TRANSPORT", _("Transport")
    SHOPPING = "SHOPPING", _("Shopping")
    BILLS = "BILLS", _("Bills")
    ENTERTAINMENT = "ENTERTAINMENT", _("Entertainment")
    HEALTH = "HEALTH", _("Health")
    EDUCATION = "EDUCATION", _("Education")
    TRAVEL = "TRAVEL", _("Travel")
    MOBILE = "MOBILE", _("Mobile")
    SOFTWARE = "SOFTWARE", _("Software")
    OTHER = "OTHER", _("Other")


class PaymentMethod(models.TextChoices):
    CASH = "CASH", _("Cash")
    BANK_TRANSFER = "BANK_TRANSFER", _("Bank Transfer")
    DEBIT_CARD = "DEBIT_CARD", _("Debit Card")
    CREDIT_CARD = "CREDIT_CARD", _("Credit Card")
    JAZZCASH = "JAZZCASH", _("JazzCash")
    EASYPAISA = "EASYPAISA", _("EasyPaisa")
    OTHER = "OTHER", _("Other")


class Expense(models.Model):
    """
    Stores a user's expense transaction.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="expenses")
    title = models.CharField(max_length=255)
    
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('1.00'))],
        help_text=_("Enter the expense amount.")
    )

    category = models.CharField(
        max_length=20,
        choices=ExpenseCategory.choices,
        db_index=True
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        db_index=True
    )

    date = models.DateField(db_index=True)
    note = models.TextField(blank=True,help_text=_("Optional note about this expense."))
    is_recurring = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ExpenseQuerySet.as_manager()

    class Meta:
        db_table = 'expenses'
        verbose_name = _("Expense")
        verbose_name_plural = _("Expense Records")
        ordering = ["-date", "-created_at"]
        indexes = [
            models.Index(fields=["user", "date"],name="expense_user_date_idx"),
            models.Index(fields=["user", "category"],name="expense_user_category_idx"),
            models.Index(fields=["user", "payment_method"],name="expense_user_payment_idx"),
        ]
        constraints = [
            models.CheckConstraint(condition=models.Q(amount__gt=0),name="expense_amount_positive")
        ]

    def __str__(self):
        return f"{self.title} - {self.amount}"

    def get_absolute_url(self):
        return reverse("expense_detail", kwargs={"pk": self.pk})

    def clean(self):
        super().clean()

        if self.date and self.date > timezone.localdate():
            raise ValidationError({"date": _("Expense date cannot be in the future.")})


    def save(self, *args, **kwargs):
        if self.title:
            self.title = self.title.strip()
        if self.note:
            self.note = self.note.strip()
        self.full_clean()
        super().save(*args, **kwargs)