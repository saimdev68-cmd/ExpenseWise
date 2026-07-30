from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from income.models import Income
from income.selectors import filter_income
from unittest.mock import patch



User = get_user_model()


class FilterIncomeSelectorTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            name="user",
            email="user1@example.com",
            password="password123",
        )

        today = timezone.localdate()

        cls.salary = Income.objects.create(
            user=cls.user,
            title="Monthly Salary",
            amount=Decimal("50000"),
            category=Income.Category.SALARY,
            date=today,
            note="Office salary",
        )

        cls.freelancing = Income.objects.create(
            user=cls.user,
            title="Website Project",
            amount=Decimal("15000"),
            category=Income.Category.FREELANCING,
            date=today - timedelta(days=1),
            note="Client payment",
        )

        cls.business = Income.objects.create(
            user=cls.user,
            title="Business Profit",
            amount=Decimal("90000"),
            category=Income.Category.BUSINESS,
            date=today - timedelta(days=5),
            note="Shop income",
        )

        cls.gift = Income.objects.create(
            user=cls.user,
            title="Birthday Gift",
            amount=Decimal("5000"),
            category=Income.Category.GIFT,
            date=today.replace(month=1, day=10),
            note="Gift from friend",
        )

    def get_queryset(self):
        return Income.objects.all()
    
    def test_search_title(self):
        qs = filter_income(
            self.get_queryset(),
            {"q": "Salary"},
        )

        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first(), self.salary)

    def test_search_note(self):
        qs = filter_income(
            self.get_queryset(),
            {"q": "Client"},
        )

        self.assertEqual(qs.first(), self.freelancing)

    def test_search_category(self):
        qs = filter_income(
            self.get_queryset(),
            {"q": "BUSINESS"},
        )

        self.assertEqual(qs.first(), self.business)

    def test_search_no_match(self):
        qs = filter_income(
            self.get_queryset(),
            {"q": "Nothing"},
        )

        self.assertEqual(qs.count(), 0)

    def test_category_filter(self):
        qs = filter_income(
            self.get_queryset(),
            {"category": Income.Category.GIFT},
        )

        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first(), self.gift)

    def test_invalid_category(self):
        qs = filter_income(
            self.get_queryset(),
            {"category": "INVALID"},
        )

        self.assertEqual(qs.count(), 0)
    
    def test_min_amount(self):
        qs = filter_income(
            self.get_queryset(),
            {"min_amount": "20000"},
        )

        self.assertEqual(qs.count(), 2)

    def test_max_amount(self):
        qs = filter_income(
            self.get_queryset(),
            {"max_amount": "10000"},
        )

        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first(), self.gift)

    def test_amount_range(self):
        qs = filter_income(
            self.get_queryset(),
            {
                "min_amount": "10000",
                "max_amount": "60000",
            },
        )

        self.assertEqual(qs.count(), 2)

    def test_from_date(self):
        today = timezone.localdate()

        qs = filter_income(
            self.get_queryset(),
            {
                "from_date": today - timedelta(days=2),
            },
        )

        self.assertEqual(qs.count(), 2)

    def test_to_date(self):
        today = timezone.localdate()

        qs = filter_income(
            self.get_queryset(),
            {
                "to_date": today - timedelta(days=2),
            },
        )

        self.assertEqual(qs.count(), 2)

    def test_date_range(self):
        today = timezone.localdate()

        qs = filter_income(
            self.get_queryset(),
            {
                "from_date": today - timedelta(days=6),
                "to_date": today - timedelta(days=1),
            },
        )

        self.assertEqual(qs.count(), 2)
    
    def test_sort_highest(self):
        qs = filter_income(
            self.get_queryset(),
            {"sort": "highest"},
        )

        self.assertEqual(qs.first(), self.business)

    def test_sort_lowest(self):
        qs = filter_income(
            self.get_queryset(),
            {"sort": "lowest"},
        )

        self.assertEqual(qs.first(), self.gift)

    def test_sort_oldest(self):
        qs = filter_income(
            self.get_queryset(),
            {"sort": "oldest"},
        )

        self.assertEqual(qs.first(), self.gift)

    def test_invalid_sort_defaults_to_newest(self):
        qs = filter_income(
            self.get_queryset(),
            {"sort": "invalid"},
        )

        self.assertEqual(qs.first(), self.salary)

    def test_today(self):
        qs = filter_income(
            self.get_queryset(),
            {"period": "today"},
        )

        self.assertEqual(qs.count(), 1)

    def test_yesterday(self):
        qs = filter_income(
            self.get_queryset(),
            {"period": "yesterday"},
        )

        self.assertEqual(qs.count(), 1)

    def test_last_7_days(self):
        qs = filter_income(
            self.get_queryset(),
            {"period": "last_7_days"},
        )

        self.assertEqual(qs.count(), 3)

    def test_this_month(self):
        today = timezone.localdate()

        if self.gift.date.month == today.month:
            expected = 4
        else:
            expected = 3

        qs = filter_income(
            self.get_queryset(),
            {"period": "this_month"},
        )

        self.assertEqual(qs.count(), expected)

    def test_this_year(self):
        qs = filter_income(
            self.get_queryset(),
            {"period": "this_year"},
        )

        self.assertEqual(qs.count(), 4)

    def test_combined_filters(self):
        qs = filter_income(
            self.get_queryset(),
            {
                "category": Income.Category.SALARY,
                "min_amount": "10000",
                "q": "Salary",
            },
        )

        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first(), self.salary)

    def test_empty_params_returns_all(self):
        qs = filter_income(
            self.get_queryset(),
            {},
        )

        self.assertEqual(qs.count(), 4)

    def test_no_results(self):
        qs = filter_income(
            self.get_queryset(),
            {
                "q": "XYZ",
                "category": Income.Category.SALARY,
            },
        )

        self.assertEqual(qs.count(), 0)