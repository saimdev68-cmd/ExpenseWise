from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import TestCase

from income.admin import IncomeAdmin
from income.models import Income

User = get_user_model()


class MockRequest:
    pass


class IncomeAdminTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.site = AdminSite()
        cls.admin = IncomeAdmin(Income, cls.site)

    # -------------------------------------------------
    # Model Registration
    # -------------------------------------------------

    def test_model_registered(self):
        self.assertEqual(
            self.admin.model,
            Income,
        )

    # -------------------------------------------------
    # list_display
    # -------------------------------------------------

    def test_list_display(self):
        self.assertEqual(
            self.admin.list_display,
            (
                "user",
                "title",
                "amount",
                "category",
                "date",
                "created_at",
            ),
        )

    # -------------------------------------------------
    # list_filter
    # -------------------------------------------------

    def test_list_filter(self):
        self.assertEqual(
            self.admin.list_filter,
            (
                "category",
                "date",
                "created_at",
            ),
        )

    # -------------------------------------------------
    # search_fields
    # -------------------------------------------------

    def test_search_fields(self):
        self.assertEqual(
            self.admin.search_fields,
            (
                "title",
                "note",
                "user__email",
            ),
        )

    # -------------------------------------------------
    # ordering
    # -------------------------------------------------

    def test_ordering(self):
        self.assertEqual(
            self.admin.ordering,
            (
                "-date",
                "-created_at",
            ),
        )

    # -------------------------------------------------
    # readonly_fields
    # -------------------------------------------------

    def test_readonly_fields(self):
        self.assertEqual(
            self.admin.readonly_fields,
            (
                "created_at",
                "updated_at",
            ),
        )

    # -------------------------------------------------
    # Pagination
    # -------------------------------------------------

    def test_list_per_page(self):
        self.assertEqual(
            self.admin.list_per_page,
            25,
        )

    # -------------------------------------------------
    # Date Hierarchy
    # -------------------------------------------------

    def test_date_hierarchy(self):
        self.assertEqual(
            self.admin.date_hierarchy,
            "date",
        )

    # -------------------------------------------------
    # Fieldsets
    # -------------------------------------------------

    def test_fieldsets_exist(self):
        self.assertEqual(
            len(self.admin.fieldsets),
            2,
        )

    def test_first_fieldset(self):
        title, options = self.admin.fieldsets[0]

        self.assertEqual(
            title,
            "Income Information",
        )

        self.assertIn(
            "user",
            options["fields"],
        )

        self.assertIn(
            "title",
            options["fields"],
        )

        self.assertIn(
            "amount",
            options["fields"],
        )

        self.assertIn(
            "category",
            options["fields"],
        )

        self.assertIn(
            "is_recurring",
            options["fields"],
        )

    def test_second_fieldset(self):
        title, options = self.admin.fieldsets[1]

        self.assertEqual(
            title,
            "System Information",
        )

        self.assertIn(
            "created_at",
            options["fields"],
        )

        self.assertIn(
            "updated_at",
            options["fields"],
        )