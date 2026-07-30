from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from expense.models import Expense, ExpenseCategory, PaymentMethod

User = get_user_model()


class ExpenseModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="john@example.com",
            name="John",
            password="testpass123"
        )

        cls.expense = Expense.objects.create(
            user=cls.user,
            title="Internet Bill",
            amount=Decimal("2500.00"),
            category=ExpenseCategory.BILLS,
            payment_method=PaymentMethod.CASH,
            date=timezone.localdate(),
            note=" Monthly bill "
        )

    # ---------------------------------------------------------
    # Model Creation
    # ---------------------------------------------------------

    def test_expense_is_created(self):
        self.assertEqual(Expense.objects.count(), 1)

    def test_expense_user(self):
        self.assertEqual(self.expense.user, self.user)

    def test_expense_title(self):
        self.assertEqual(self.expense.title, "Internet Bill")

    def test_expense_amount(self):
        self.assertEqual(self.expense.amount, Decimal("2500.00"))

    def test_expense_category(self):
        self.assertEqual(
            self.expense.category,
            ExpenseCategory.BILLS
        )

    def test_expense_payment_method(self):
        self.assertEqual(
            self.expense.payment_method,
            PaymentMethod.CASH
        )

    # ---------------------------------------------------------
    # __str__
    # ---------------------------------------------------------

    def test_str_method(self):
        expected = f"{self.user} | Internet Bill | 2500.00"
        self.assertEqual(str(self.expense), expected)

    # ---------------------------------------------------------
    # Absolute URL
    # ---------------------------------------------------------

    def test_get_absolute_url(self):
        self.assertEqual(
            self.expense.get_absolute_url(),
            reverse(
                "expense_detail",
                kwargs={"pk": self.expense.pk},
            ),
        )

    # ---------------------------------------------------------
    # Ordering
    # ---------------------------------------------------------

    def test_default_ordering(self):
        newer = Expense.objects.create(
            user=self.user,
            title="Fuel",
            amount=1000,
            category=ExpenseCategory.TRANSPORT,
            payment_method=PaymentMethod.CASH,
            date=timezone.localdate(),
        )

        queryset = Expense.objects.all()

        self.assertEqual(queryset.first(), newer)

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    def test_future_date_validation(self):
        expense = Expense(
            user=self.user,
            title="Future",
            amount=100,
            category=ExpenseCategory.FOOD,
            payment_method=PaymentMethod.CASH,
            date=timezone.localdate() + timedelta(days=1),
        )

        with self.assertRaises(ValidationError):
            expense.full_clean()

    def test_amount_must_be_positive(self):
        expense = Expense(
            user=self.user,
            title="Negative",
            amount=-10,
            category=ExpenseCategory.FOOD,
            payment_method=PaymentMethod.CASH,
            date=timezone.localdate(),
        )

        with self.assertRaises(ValidationError):
            expense.full_clean()

    def test_zero_amount_validation(self):
        expense = Expense(
            user=self.user,
            title="Zero",
            amount=0,
            category=ExpenseCategory.FOOD,
            payment_method=PaymentMethod.CASH,
            date=timezone.localdate(),
        )

        with self.assertRaises(ValidationError):
            expense.full_clean()

    # ---------------------------------------------------------
    # Save Behaviour
    # ---------------------------------------------------------

    def test_note_is_trimmed_before_save(self):
        self.assertEqual(
            self.expense.note,
            "Monthly bill"
        )

    def test_empty_note_allowed(self):
        expense = Expense.objects.create(
            user=self.user,
            title="Food",
            amount=250,
            category=ExpenseCategory.FOOD,
            payment_method=PaymentMethod.CASH,
            date=timezone.localdate(),
            note=""
        )

        self.assertEqual(expense.note, "")

    # ---------------------------------------------------------
    # Meta
    # ---------------------------------------------------------

    def test_verbose_name(self):
        self.assertEqual(
            Expense._meta.verbose_name,
            "Expense"
        )

    def test_verbose_name_plural(self):
        self.assertEqual(
            Expense._meta.verbose_name_plural,
            "Expense Records"
        )

    def test_ordering_meta(self):
        self.assertEqual(
            Expense._meta.ordering,
            ["-date", "-created_at"]
        )

    # ---------------------------------------------------------
    # Queryset
    # ---------------------------------------------------------

    def test_for_user_queryset(self):
        other = User.objects.create_user(
            email="other@example.com",
            first_name="Other",
            password="12345678"
        )

        Expense.objects.create(
            user=other,
            title="Shopping",
            amount=500,
            category=ExpenseCategory.SHOPPING,
            payment_method=PaymentMethod.CASH,
            date=timezone.localdate(),
        )

        queryset = Expense.objects.for_user(self.user)

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first(), self.expense)

    # ---------------------------------------------------------
    # Database Constraint
    # ---------------------------------------------------------

    def test_database_positive_amount_constraint(self):
        with self.assertRaises((ValidationError, IntegrityError)):
            Expense.objects.create(
                user=self.user,
                title="Invalid",
                amount=-100,
                category=ExpenseCategory.FOOD,
                payment_method=PaymentMethod.CASH,
                date=timezone.localdate(),
            )

    # ---------------------------------------------------------
    # Defaults
    # ---------------------------------------------------------

    def test_is_recurring_default_false(self):
        self.assertFalse(self.expense.is_recurring)

    def test_created_at_exists(self):
        self.assertIsNotNone(self.expense.created_at)

    def test_updated_at_exists(self):
        self.assertIsNotNone(self.expense.updated_at)