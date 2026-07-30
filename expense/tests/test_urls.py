from django.test import SimpleTestCase
from django.urls import resolve, reverse

from expense.views import (
    ExpenseListView,
    ExpenseCreateView,
    ExpenseDetailView,
    ExpenseUpdateView,
    ExpenseDeleteView,
)


class ExpenseURLTests(SimpleTestCase):
    """Tests for expense URL configuration."""

    # ==========================================================
    # Reverse URL Tests
    # ==========================================================

    def test_expense_list_reverse(self):
        self.assertEqual(
            reverse("expense_list"),
            "/expense/",
        )

    def test_expense_add_reverse(self):
        self.assertEqual(
            reverse("expense_add"),
            "/expense/add/",
        )

    def test_expense_detail_reverse(self):
        self.assertEqual(
            reverse(
                "expense_detail",
                kwargs={"pk": 10},
            ),
            "/expense/10/",
        )

    def test_expense_edit_reverse(self):
        self.assertEqual(
            reverse(
                "expense_edit",
                kwargs={"pk": 10},
            ),
            "/expense/10/edit/",
        )

    def test_expense_delete_reverse(self):
        self.assertEqual(
            reverse(
                "expense_delete",
                kwargs={"pk": 10},
            ),
            "/expense/10/delete/",
        )

    # ==========================================================
    # Resolve URL Tests
    # ==========================================================

    def test_expense_list_resolves(self):
        resolver = resolve("/expense/")

        self.assertEqual(
            resolver.func.view_class,
            ExpenseListView,
        )

    def test_expense_add_resolves(self):
        resolver = resolve("/expense/add/")

        self.assertEqual(
            resolver.func.view_class,
            ExpenseCreateView,
        )

    def test_expense_detail_resolves(self):
        resolver = resolve("/expense/1/")

        self.assertEqual(
            resolver.func.view_class,
            ExpenseDetailView,
        )

    def test_expense_edit_resolves(self):
        resolver = resolve("/expense/1/edit/")

        self.assertEqual(
            resolver.func.view_class,
            ExpenseUpdateView,
        )

    def test_expense_delete_resolves(self):
        resolver = resolve("/expense/1/delete/")

        self.assertEqual(
            resolver.func.view_class,
            ExpenseDeleteView,
        )

    # ==========================================================
    # URL Names
    # ==========================================================

    def test_url_name_expense_list(self):
        resolver = resolve("/expense/")
        self.assertEqual(
            resolver.url_name,
            "expense_list",
        )

    def test_url_name_expense_add(self):
        resolver = resolve("/expense/add/")
        self.assertEqual(
            resolver.url_name,
            "expense_add",
        )

    def test_url_name_expense_detail(self):
        resolver = resolve("/expense/15/")
        self.assertEqual(
            resolver.url_name,
            "expense_detail",
        )

    def test_url_name_expense_edit(self):
        resolver = resolve("/expense/15/edit/")
        self.assertEqual(
            resolver.url_name,
            "expense_edit",
        )

    def test_url_name_expense_delete(self):
        resolver = resolve("/expense/15/delete/")
        self.assertEqual(
            resolver.url_name,
            "expense_delete",
        )