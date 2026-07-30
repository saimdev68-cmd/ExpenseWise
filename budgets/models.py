from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from expense.models import Expense , ExpenseCategory

from django.db.models.functions import Coalesce
from django.db.models import DecimalField
from django.conf import settings

from django.urls import reverse
from django.db.models import Sum
from django.db import models
from decimal import Decimal

from .constants import NO_SPEND , WITHIN , REACHED , EXCEED
from .managers import BudgetManager
from .utils import current_year


class Budget(models.Model):
    """
    Stores a user's budget transaction.
    """
    CATEGORY_CHOICES = ExpenseCategory

    MONTH_CHOICES = [
        (1, "January"),
        (2, "February"),
        (3, "March"),
        (4, "April"),
        (5, "May"),
        (6, "June"),
        (7, "July"),
        (8, "August"),
        (9, "September"),
        (10, "October"),
        (11, "November"),
        (12, "December"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="budgets")
    category = models.CharField(max_length=50,choices=CATEGORY_CHOICES,db_index=True)

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('1.00'))],
        help_text=_("Monthly budget amount.")
    )
    
    month = models.PositiveSmallIntegerField(choices=MONTH_CHOICES)
    year = models.PositiveIntegerField(default=current_year,db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = BudgetManager()

    class Meta:
        db_table = "budgets"
        verbose_name = _("Budget")
        verbose_name_plural = _("Budgets")
        ordering = ["-year", "-month", "-created_at"]
        indexes = [
            models.Index(fields=["user","category"],name="budget_user_category_idx"),
            models.Index(fields=["user","year"],name="budget_user_year_idx"),
            models.Index(fields=["user","year","month"],name="budget_user_year_month__idx"),
        ]

        constraints = [
            models.UniqueConstraint(
                fields=["user","category","month","year"],
                name="unique_user_category_month_year_budget",
            ),
            models.CheckConstraint(
                condition=models.Q(amount__gt=0),
                name="budget_amount_gt_zero",
            ),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.category}"

    def get_absolute_url(self):
        return reverse("budget_detail", kwargs={"pk": self.pk})
    

    @property
    def spent(self):
        if hasattr(self, '_spent_annotated'):
            return self._spent_annotated
        
        total = Expense.objects.filter(
            user=self.user,
            category=self.category,
            date__month=self.month,
            date__year=self.year,
        ).aggregate(
            total=Coalesce(
                Sum("amount"),
                Decimal("0.00"),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            )
        )["total"]
        return total

    @property
    def remaining(self):
        return self.amount - self.spent

    @property
    def percentage_used(self):
        if self.amount == 0:
            return Decimal("0.00")
        percentage = (self.spent / self.amount) * Decimal("100")
        return round(percentage, 2)

    @property
    def progress_percentage(self):
        return min(self.percentage_used, Decimal("100"))

    @property
    def status(self):
        if self.spent == 0:
            return NO_SPEND

        if self.spent < self.amount:
            return WITHIN

        if self.spent == self.amount:
            return REACHED

        return EXCEED

    @property
    def warning_message(self):
        if self.spent > self.amount:
            return (f"You have exceeded your {self.get_category_display()} budget.")
        
        return None