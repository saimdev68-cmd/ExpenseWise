from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import TestCase

from expense.admin import ExpenseAdmin
from expense.models import Expense

User = get_user_model()


class MockRequest:
    pass


class ExpenseAdminTest(TestCase):
    """Tests for ExpenseAdmin configuration."""

    @classmethod
    def setUpTestData(cls):
        cls.site = AdminSite()
        cls.admin = ExpenseAdmin(Expense, cls.site)

        cls.user = User.objects.create_user(
            email="john@example.com",
            name="John",
            password="password123",
        )

    # =====================================================
    # Admin Registration
    # =====================================================

    def test_admin_model(self):
        self.assertEqual(
            self.admin.model,
            Expense,
        )

    # =====================================================
    # list_display
    # =====================================================

    def test_list_display(self):
        self.assertEqual(
            self.admin.list_display,
            (
                "user",
                "title",
                "amount",
                "category",
                "payment_method",
                "date",
                "created_at",
            ),
        )

    # =====================================================
    # list_filter
    # =====================================================

    def test_list_filter(self):
        self.assertEqual(
            self.admin.list_filter,
            (
                "category",
                "payment_method",
                "date",
            ),
        )

    # =====================================================
    # search_fields
    # =====================================================

    def test_search_fields(self):
        self.assertEqual(
            self.admin.search_fields,
            (
                "title",
                "user__email",
                "note",
            ),
        )

    # =====================================================
    # ordering
    # =====================================================

    def test_ordering(self):
        self.assertEqual(
            self.admin.ordering,
            (
                "-date",
                "-created_at",
            ),
        )

    # =====================================================
    # readonly_fields
    # =====================================================

    def test_readonly_fields(self):
        self.assertEqual(
            self.admin.readonly_fields,
            (
                "created_at",
                "updated_at",
            ),
        )

    # =====================================================
    # Pagination
    # =====================================================

    def test_list_per_page(self):
        self.assertEqual(
            self.admin.list_per_page,
            25,
        )

    # =====================================================
    # Date Hierarchy
    # =====================================================

    def test_date_hierarchy(self):
        self.assertEqual(
            self.admin.date_hierarchy,
            "date",
        )

    # =====================================================
    # Fieldsets
    # =====================================================

    def test_fieldsets(self):
        self.assertEqual(len(self.admin.fieldsets), 2)

    def test_information_fieldset(self):
        title, options = self.admin.fieldsets[0]

        self.assertEqual(
            title,
            "Expense Information",
        )

        self.assertEqual(
            options["fields"],
            (
                "user",
                "title",
                "amount",
                "category",
                "payment_method",
                "date",
                "note",
            ),
        )

    def test_timestamp_fieldset(self):
        title, options = self.admin.fieldsets[1]

        self.assertEqual(
            title,
            "Timestamps",
        )

        self.assertEqual(
            options["fields"],
            (
                "created_at",
                "updated_at",
            ),
        )

        self.assertEqual(
            options["classes"],
            ("collapse",),
        )

    # =====================================================
    # Queryset
    # =====================================================

    def test_get_queryset(self):
        request = MockRequest()

        queryset = self.admin.get_queryset(request)

        self.assertEqual(
            queryset.model,
            Expense,
        )

    # =====================================================
    # Form
    # =====================================================

    def test_get_form(self):
        request = MockRequest()

        form = self.admin.get_form(request)

        self.assertIn(
            "title",
            form.base_fields,
        )

        self.assertIn(
            "amount",
            form.base_fields,
        )

        self.assertIn(
            "category",
            form.base_fields,
        )

        self.assertIn(
            "payment_method",
            form.base_fields,
        )

        self.assertIn(
            "date",
            form.base_fields,
        )

        self.assertIn(
            "note",
            form.base_fields,
        )

    # =====================================================
    # Admin Attributes
    # =====================================================

    def test_has_search(self):
        self.assertTrue(
            bool(self.admin.search_fields)
        )

    def test_has_filters(self):
        self.assertTrue(
            bool(self.admin.list_filter)
        )

    def test_has_ordering(self):
        self.assertTrue(
            bool(self.admin.ordering)
        )

    def test_has_readonly_fields(self):
        self.assertTrue(
            bool(self.admin.readonly_fields)
        )