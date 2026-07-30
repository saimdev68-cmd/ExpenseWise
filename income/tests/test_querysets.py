from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from income.models import Income

User = get_user_model()


class IncomeQuerySetTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(
            name="user1",
            email="user1@example.com",
            password="password123",
        )

        cls.user2 = User.objects.create_user(
            name="user2",
            email="user2@example.com",
            password="password123",
        )

        cls.income1 = Income.objects.create(
            user=cls.user1,
            title="Salary",
            amount=Decimal("50000"),
            category=Income.Category.SALARY,
            date=timezone.localdate(),
        )

        cls.income2 = Income.objects.create(
            user=cls.user1,
            title="Freelancing",
            amount=Decimal("15000"),
            category=Income.Category.FREELANCING,
            date=timezone.localdate(),
        )

        cls.income3 = Income.objects.create(
            user=cls.user2,
            title="Business",
            amount=Decimal("90000"),
            category=Income.Category.BUSINESS,
            date=timezone.localdate(),
        )

    # -------------------------------------------------
    # for_user()
    # -------------------------------------------------

    def test_for_user_returns_only_user_records(self):
        queryset = Income.objects.for_user(self.user1)

        self.assertEqual(queryset.count(), 2)
        self.assertIn(self.income1, queryset)
        self.assertIn(self.income2, queryset)
        self.assertNotIn(self.income3, queryset)

    def test_for_user_second_user(self):
        queryset = Income.objects.for_user(self.user2)

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first(), self.income3)

    def test_for_user_empty_queryset(self):
        user = User.objects.create_user(
            name="empty",
            email="empty@example.com",
            password="password123",
        )

        queryset = Income.objects.for_user(user)

        self.assertEqual(queryset.count(), 0)
        self.assertFalse(queryset.exists())

    # -------------------------------------------------
    # Queryset chaining
    # -------------------------------------------------

    def test_queryset_can_be_chained(self):
        queryset = (
            Income.objects
            .for_user(self.user1)
            .filter(category=Income.Category.SALARY)
        )

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first(), self.income1)

    def test_queryset_ordering_is_preserved(self):
        queryset = Income.objects.for_user(self.user1)

        self.assertEqual(
            list(queryset),
            sorted(
                queryset,
                key=lambda obj: (obj.date, obj.created_at),
                reverse=True,
            ),
        )

    # -------------------------------------------------
    # Further filtering
    # -------------------------------------------------

    def test_filter_by_amount_after_for_user(self):
        queryset = (
            Income.objects
            .for_user(self.user1)
            .filter(amount__gte=30000)
        )

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first(), self.income1)

    def test_filter_by_title_after_for_user(self):
        queryset = (
            Income.objects
            .for_user(self.user1)
            .filter(title__icontains="salary")
        )

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first(), self.income1)