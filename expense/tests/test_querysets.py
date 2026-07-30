from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from expense.models import Expense, ExpenseCategory, PaymentMethod

User = get_user_model()


class ExpenseQuerySetTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(
            email="john@example.com",
            name="John",
            password="password123",
        )

        cls.user2 = User.objects.create_user(
            email="jane@example.com",
            name="Jane",
            password="password123",
        )

        cls.expense1 = Expense.objects.create(
            user=cls.user1,
            title="Internet Bill",
            amount=Decimal("2500.00"),
            category=ExpenseCategory.BILLS,
            payment_method=PaymentMethod.CASH,
            date=timezone.localdate(),
        )

        cls.expense2 = Expense.objects.create(
            user=cls.user1,
            title="Fuel",
            amount=Decimal("1200.00"),
            category=ExpenseCategory.TRANSPORT,
            payment_method=PaymentMethod.DEBIT_CARD,
            date=timezone.localdate(),
        )

        cls.expense3 = Expense.objects.create(
            user=cls.user2,
            title="Shopping",
            amount=Decimal("5000.00"),
            category=ExpenseCategory.SHOPPING,
            payment_method=PaymentMethod.CREDIT_CARD,
            date=timezone.localdate(),
        )

    # ---------------------------------------------------------
    # for_user()
    # ---------------------------------------------------------

    def test_for_user_returns_only_user_expenses(self):
        queryset = Expense.objects.for_user(self.user1)

        self.assertEqual(queryset.count(), 2)

        self.assertIn(self.expense1, queryset)
        self.assertIn(self.expense2, queryset)
        self.assertNotIn(self.expense3, queryset)

    def test_for_user_second_user(self):
        queryset = Expense.objects.for_user(self.user2)

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first(), self.expense3)

    def test_for_user_empty_queryset(self):
        user = User.objects.create_user(
            email="empty@example.com",
            first_name="Empty",
            password="password123",
        )

        queryset = Expense.objects.for_user(user)

        self.assertEqual(queryset.count(), 0)

    def test_for_user_returns_queryset(self):
        queryset = Expense.objects.for_user(self.user1)

        self.assertTrue(hasattr(queryset, "filter"))
        self.assertTrue(hasattr(queryset, "order_by"))

    def test_queryset_chainable(self):
        queryset = (
            Expense.objects
            .for_user(self.user1)
            .filter(category=ExpenseCategory.BILLS)
        )

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first(), self.expense1)