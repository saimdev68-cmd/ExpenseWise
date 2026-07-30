from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

from django.utils import timezone
from django.conf import settings
from django.urls import reverse

from django.db import models
from decimal import Decimal

from .queysets import IncomeQuerySet


class Income(models.Model):
    """
    Stores a user's income transaction.
    """

    class Category(models.TextChoices):
        SALARY = "SALARY", _("Salary")
        FREELANCING = "FREELANCING", _("Freelancing")
        BUSINESS = "BUSINESS", _("Business")
        INVESTMENT = "INVESTMENT", _("Investment")
        GIFT = "GIFT", _("Gift")
        OTHER = "OTHER", _("Other")

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="incomes")
    title = models.CharField(max_length=255)

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("1.00"))],
        help_text=_("Enter the income amount."),
    )

    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        db_index=True
    )
    
    date = models.DateField(db_index=True)
    note = models.TextField(blank=True,help_text=_("Optional notes about this income."))
    is_recurring = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = IncomeQuerySet.as_manager()

    class Meta:
        db_table = 'incomes'
        verbose_name = _("Income")
        verbose_name_plural = _("Income Records")
        ordering = ["-date", "-created_at"]
        indexes = [
            models.Index(fields=["user", "date"],name="income_user_date_idx"),
            models.Index(fields=["user", "category"],name="income_user_category_idx"),
        ]
        constraints = [
            models.CheckConstraint(condition=models.Q(amount__gt=0),name="income_amount_positive")
        ]

    def __str__(self):
        return f"{self.title} - {self.amount}"

    def get_absolute_url(self):
        return reverse("income_detail", kwargs={"pk": self.pk})

    def clean(self):
        super().clean()

        if self.date and self.date > timezone.localdate():
            raise ValidationError({"date": _("Income date cannot be in the future.")})

    def save(self, *args, **kwargs):
        if self.title:
            self.title = self.title.strip()

        if self.note:
            self.note = self.note.strip()

        self.full_clean()
        return super().save(*args, **kwargs)