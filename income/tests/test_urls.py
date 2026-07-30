from django.test import SimpleTestCase
from django.urls import resolve, reverse

from income.views import (
    IncomeCreateView,
    IncomeDeleteView,
    IncomeDetailView,
    IncomeListView,
    IncomeUpdateView,
)


class IncomeURLTest(SimpleTestCase):

    # ---------------------------------------------
    # Reverse URLs
    # ---------------------------------------------

    def test_income_list_url(self):
        self.assertEqual(
            reverse("income_list"),
            "/income/",
        )

    def test_income_add_url(self):
        self.assertEqual(
            reverse("income_add"),
            "/income/add/",
        )

    def test_income_detail_url(self):
        self.assertEqual(
            reverse(
                "income_detail",
                kwargs={"pk": 1},
            ),
            "/income/1/",
        )

    def test_income_edit_url(self):
        self.assertEqual(
            reverse(
                "income_edit",
                kwargs={"pk": 1},
            ),
            "/income/1/edit/",
        )

    def test_income_delete_url(self):
        self.assertEqual(
            reverse(
                "income_delete",
                kwargs={"pk": 1},
            ),
            "/income/1/delete/",
        )

    # ---------------------------------------------
    # Resolve URLs
    # ---------------------------------------------

    def test_income_list_resolves(self):
        resolver = resolve("/income/")

        self.assertEqual(
            resolver.func.view_class,
            IncomeListView,
        )

    def test_income_add_resolves(self):
        resolver = resolve("/income/add/")

        self.assertEqual(
            resolver.func.view_class,
            IncomeCreateView,
        )

    def test_income_detail_resolves(self):
        resolver = resolve("/income/1/")

        self.assertEqual(
            resolver.func.view_class,
            IncomeDetailView,
        )

    def test_income_edit_resolves(self):
        resolver = resolve("/income/1/edit/")

        self.assertEqual(
            resolver.func.view_class,
            IncomeUpdateView,
        )

    def test_income_delete_resolves(self):
        resolver = resolve("/income/1/delete/")

        self.assertEqual(
            resolver.func.view_class,
            IncomeDeleteView,
        )