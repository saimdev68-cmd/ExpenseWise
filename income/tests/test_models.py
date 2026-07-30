from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from income.models import Income

User = get_user_model()


class IncomeModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            name="saim",
            email="saim@example.com",
            password="testpass123"
        )

        cls.income = Income.objects.create(
            user=cls.user,
            title="Monthly Salary",
            amount=Decimal("50000.00"),
            category=Income.Category.SALARY,
            date=timezone.localdate(),
            note="Salary for July"
        )

    # -----------------------------------------------------
    # Object Creation
    # -----------------------------------------------------

    def test_income_created_successfully(self):
        self.assertEqual(Income.objects.count(), 1)
        self.assertEqual(self.income.title, "Monthly Salary")
        self.assertEqual(self.income.amount, Decimal("50000.00"))
        self.assertEqual(self.income.category, Income.Category.SALARY)

    # -----------------------------------------------------
    # __str__
    # -----------------------------------------------------

    def test_str_method(self):
        expected = (
            f"{self.user} | "
            f"{self.income.title} | "
            f"{self.income.amount}"
        )

        self.assertEqual(str(self.income), expected)

    # -----------------------------------------------------
    # get_absolute_url
    # -----------------------------------------------------

    def test_get_absolute_url(self):
        self.assertEqual(
            self.income.get_absolute_url(),
            reverse("income_detail", kwargs={"pk": self.income.pk})
        )

    # -----------------------------------------------------
    # Ordering
    # -----------------------------------------------------

    def test_default_ordering(self):

        newer = Income.objects.create(
            user=self.user,
            title="Bonus",
            amount=1000,
            category=Income.Category.OTHER,
            date=timezone.localdate(),
        )

        incomes = Income.objects.all()

        self.assertEqual(incomes.first(), newer)

    # -----------------------------------------------------
    # Auto timestamps
    # -----------------------------------------------------

    def test_created_at_is_set(self):
        self.assertIsNotNone(self.income.created_at)

    def test_updated_at_is_set(self):
        self.assertIsNotNone(self.income.updated_at)

    # -----------------------------------------------------
    # Recurring default
    # -----------------------------------------------------

    def test_is_recurring_default_false(self):
        self.assertFalse(self.income.is_recurring)

    # -----------------------------------------------------
    # Note stripping
    # -----------------------------------------------------

    def test_note_is_stripped_before_save(self):

        income = Income.objects.create(
            user=self.user,
            title="Gift",
            amount=500,
            category=Income.Category.GIFT,
            date=timezone.localdate(),
            note="   Thank you!   ",
        )

        self.assertEqual(income.note, "Thank you!")

    # -----------------------------------------------------
    # Future date validation
    # -----------------------------------------------------

    def test_future_date_not_allowed(self):

        income = Income(
            user=self.user,
            title="Future",
            amount=1000,
            category=Income.Category.OTHER,
            date=timezone.localdate() + timedelta(days=1),
        )

        with self.assertRaises(ValidationError):
            income.full_clean()

    # -----------------------------------------------------
    # Amount validation
    # -----------------------------------------------------

    def test_zero_amount_not_allowed(self):

        income = Income(
            user=self.user,
            title="Invalid",
            amount=0,
            category=Income.Category.OTHER,
            date=timezone.localdate(),
        )

        with self.assertRaises(ValidationError):
            income.full_clean()

    def test_negative_amount_not_allowed(self):

        income = Income(
            user=self.user,
            title="Invalid",
            amount=-100,
            category=Income.Category.OTHER,
            date=timezone.localdate(),
        )

        with self.assertRaises(ValidationError):
            income.full_clean()

    # -----------------------------------------------------
    # Positive amount
    # -----------------------------------------------------

    def test_positive_amount_is_valid(self):

        income = Income(
            user=self.user,
            title="Business",
            amount=15000,
            category=Income.Category.BUSINESS,
            date=timezone.localdate(),
        )

        income.full_clean()

    # -----------------------------------------------------
    # Category choices
    # -----------------------------------------------------

    def test_default_category(self):

        income = Income(
            user=self.user,
            title="Unknown",
            amount=100,
            date=timezone.localdate(),
        )

        self.assertEqual(
            income.category,
            Income.Category.OTHER
        )

    # -----------------------------------------------------
    # Required fields
    # -----------------------------------------------------

    def test_title_is_required(self):

        income = Income(
            user=self.user,
            title="",
            amount=100,
            date=timezone.localdate(),
        )

        with self.assertRaises(ValidationError):
            income.full_clean()

    def test_date_is_required(self):

        income = Income(
            user=self.user,
            title="Salary",
            amount=100,
        )

        with self.assertRaises(ValidationError):
            income.full_clean()

    # -----------------------------------------------------
    # Database constraint
    # -----------------------------------------------------

    def test_amount_constraint_exists(self):

        constraint_names = [
            constraint.name
            for constraint in Income._meta.constraints
        ]

        self.assertIn(
            "income_amount_positive",
            constraint_names
        )

    # -----------------------------------------------------
    # Meta
    # -----------------------------------------------------

    def test_verbose_name(self):
        self.assertEqual(
            Income._meta.verbose_name,
            "Income"
        )

    def test_verbose_name_plural(self):
        self.assertEqual(
            Income._meta.verbose_name_plural,
            "Income Records"
        )

    def test_ordering_meta(self):
        self.assertEqual(
            Income._meta.ordering,
            ["-date", "-created_at"]
        )