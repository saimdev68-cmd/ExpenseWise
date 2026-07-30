from decimal import Decimal
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from expense.models import (
    Expense,
    ExpenseCategory,
    PaymentMethod,
)
from expense.selectors import expense_filter

User = get_user_model()


class ExpenseSelectorTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="john@example.com",
            name="John",
            password="password123",
        )

        today = timezone.localdate()

        cls.food = Expense.objects.create(
            user=cls.user,
            title="Pizza",
            amount=Decimal("500"),
            category=ExpenseCategory.FOOD,
            payment_method=PaymentMethod.CASH,
            date=today,
            note="Delicious pizza",
        )

        cls.transport = Expense.objects.create(
            user=cls.user,
            title="Fuel",
            amount=Decimal("2500"),
            category=ExpenseCategory.TRANSPORT,
            payment_method=PaymentMethod.DEBIT_CARD,
            date=today - timedelta(days=1),
            note="Petrol",
        )

        cls.bill = Expense.objects.create(
            user=cls.user,
            title="Internet",
            amount=Decimal("3500"),
            category=ExpenseCategory.BILLS,
            payment_method=PaymentMethod.BANK_TRANSFER,
            date=today - timedelta(days=20),
            note="StormFiber",
        )

    # ---------------------------------------------------------
    # Search
    # ---------------------------------------------------------

    def test_search_by_title(self):
        qs = expense_filter(
            Expense.objects.all(),
            {"search": "Pizza"},
        )

        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first(), self.food)

    def test_search_by_note(self):
        qs = expense_filter(
            Expense.objects.all(),
            {"search": "Storm"},
        )

        self.assertEqual(qs.first(), self.bill)

    # ---------------------------------------------------------
    # Category
    # ---------------------------------------------------------

    def test_category_filter(self):
        qs = expense_filter(
            Expense.objects.all(),
            {"category": ExpenseCategory.FOOD},
        )

        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first(), self.food)

    # ---------------------------------------------------------
    # Payment Method
    # ---------------------------------------------------------

    def test_payment_method_filter(self):
        qs = expense_filter(
            Expense.objects.all(),
            {
                "payment_method": PaymentMethod.DEBIT_CARD,
            },
        )

        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first(), self.transport)

    # ---------------------------------------------------------
    # Min Amount
    # ---------------------------------------------------------

    def test_min_amount_filter(self):
        qs = expense_filter(
            Expense.objects.all(),
            {"min_amount": "1000"},
        )

        self.assertEqual(qs.count(), 2)

    # ---------------------------------------------------------
    # Max Amount
    # ---------------------------------------------------------

    def test_max_amount_filter(self):
        qs = expense_filter(
            Expense.objects.all(),
            {"max_amount": "1000"},
        )

        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first(), self.food)

    # ---------------------------------------------------------
    # Date Range
    # ---------------------------------------------------------

    def test_start_date_filter(self):
        start = timezone.localdate() - timedelta(days=2)

        qs = expense_filter(
            Expense.objects.all(),
            {"start_date": start},
        )

        self.assertEqual(qs.count(), 2)

    def test_end_date_filter(self):
        end = timezone.localdate() - timedelta(days=2)

        qs = expense_filter(
            Expense.objects.all(),
            {"end_date": end},
        )

        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first(), self.bill)

    # ---------------------------------------------------------
    # Sort
    # ---------------------------------------------------------

    def test_sort_highest(self):
        qs = expense_filter(
            Expense.objects.all(),
            {"sort": "highest"},
        )

        self.assertEqual(qs.first(), self.bill)

    def test_sort_lowest(self):
        qs = expense_filter(
            Expense.objects.all(),
            {"sort": "lowest"},
        )

        self.assertEqual(qs.first(), self.food)

    def test_sort_oldest(self):
        qs = expense_filter(
            Expense.objects.all(),
            {"sort": "oldest"},
        )

        self.assertEqual(qs.first(), self.bill)

    def test_sort_newest(self):
        qs = expense_filter(
            Expense.objects.all(),
            {"sort": "newest"},
        )

        self.assertEqual(qs.first(), self.food)

    # ---------------------------------------------------------
    # Period
    # ---------------------------------------------------------

    def test_today_filter(self):
        qs = expense_filter(
            Expense.objects.all(),
            {"period": "today"},
        )

        self.assertEqual(qs.count(), 1)

    def test_yesterday_filter(self):
        qs = expense_filter(
            Expense.objects.all(),
            {"period": "yesterday"},
        )

        self.assertEqual(qs.count(), 1)

    def test_last_7_days_filter(self):
        qs = expense_filter(
            Expense.objects.all(),
            {"period": "last_7_days"},
        )

        self.assertEqual(qs.count(), 2)

    def test_this_month_filter(self):
        qs = expense_filter(
            Expense.objects.all(),
            {"period": "this_month"},
        )

        self.assertGreaterEqual(qs.count(), 2)

    def test_this_year_filter(self):
        qs = expense_filter(
            Expense.objects.all(),
            {"period": "this_year"},
        )

        self.assertEqual(qs.count(), 3)

    # ---------------------------------------------------------
    # Combined Filters
    # ---------------------------------------------------------

    def test_combined_filters(self):
        qs = expense_filter(
            Expense.objects.all(),
            {
                "category": ExpenseCategory.FOOD,
                "payment_method": PaymentMethod.CASH,
                "min_amount": "100",
                "max_amount": "1000",
            },
        )

        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first(), self.food)

    # ---------------------------------------------------------
    # Empty Result
    # ---------------------------------------------------------

    def test_no_matching_results(self):
        qs = expense_filter(
            Expense.objects.all(),
            {
                "search": "Laptop",
            },
        )

        self.assertEqual(qs.count(), 0)