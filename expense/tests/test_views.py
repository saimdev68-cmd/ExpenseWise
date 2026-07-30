from decimal import Decimal
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from expense.models import Expense, ExpenseCategory, PaymentMethod

User = get_user_model()


class ExpenseViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="john@example.com",
            name="John",
            password="password123",
        )

        cls.other_user = User.objects.create_user(
            email="jane@example.com",
            name="Jane",
            password="password123",
        )

        today = timezone.localdate()

        cls.expense = Expense.objects.create(
            user=cls.user,
            title="Internet Bill",
            amount=Decimal("2500.00"),
            category=ExpenseCategory.BILLS,
            payment_method=PaymentMethod.CASH,
            date=today,
            note="Monthly bill",
        )

        cls.other_expense = Expense.objects.create(
            user=cls.other_user,
            title="Shopping",
            amount=Decimal("5000.00"),
            category=ExpenseCategory.SHOPPING,
            payment_method=PaymentMethod.CREDIT_CARD,
            date=today - timedelta(days=1),
            note="Mall",
        )

    # -----------------------------------------------------
    # Helpers
    # -----------------------------------------------------

    def login(self):
        self.client.login(
            email="john@example.com",
            password="password123",
        )

    # -----------------------------------------------------
    # Authentication
    # -----------------------------------------------------

    def test_list_requires_login(self):
        response = self.client.get(
            reverse("expense_list")
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_detail_requires_login(self):
        response = self.client.get(
            reverse(
                "expense_detail",
                kwargs={"pk": self.expense.pk},
            )
        )

        self.assertEqual(response.status_code, 302)

    def test_create_requires_login(self):
        response = self.client.get(
            reverse("expense_add")
        )

        self.assertEqual(response.status_code, 302)

    def test_update_requires_login(self):
        response = self.client.get(
            reverse(
                "expense_edit",
                kwargs={"pk": self.expense.pk},
            )
        )

        self.assertEqual(response.status_code, 302)

    def test_delete_requires_login(self):
        response = self.client.post(
            reverse(
                "expense_delete",
                kwargs={"pk": self.expense.pk},
            )
        )

        self.assertEqual(response.status_code, 302)

    # -----------------------------------------------------
    # Expense List
    # -----------------------------------------------------

    def test_list_page_status_code(self):
        self.login()

        response = self.client.get(
            reverse("expense_list")
        )

        self.assertEqual(response.status_code, 200)

    def test_list_template_used(self):
        self.login()

        response = self.client.get(
            reverse("expense_list")
        )

        self.assertTemplateUsed(
            response,
            "expense_list.html",
        )

    def test_context_object_name(self):
        self.login()

        response = self.client.get(
            reverse("expense_list")
        )

        self.assertIn("expenses", response.context)

    def test_user_only_sees_own_expenses(self):
        self.login()

        response = self.client.get(
            reverse("expense_list")
        )

        expenses = response.context["expenses"]

        self.assertIn(self.expense, expenses)
        self.assertNotIn(
            self.other_expense,
            expenses,
        )

    def test_categories_exist_in_context(self):
        self.login()

        response = self.client.get(
            reverse("expense_list")
        )

        self.assertIn(
            "categories",
            response.context,
        )

    def test_payment_methods_exist_in_context(self):
        self.login()

        response = self.client.get(
            reverse("expense_list")
        )

        self.assertIn(
            "payment_methods",
            response.context,
        )

    def test_filters_exist_in_context(self):
        self.login()

        response = self.client.get(
            reverse("expense_list")
        )

        self.assertIn(
            "filters",
            response.context,
        )

    def test_query_string_exists(self):
        self.login()

        response = self.client.get(
            reverse("expense_list")
        )

        self.assertIn(
            "query_string",
            response.context,
        )

    # -----------------------------------------------------
    # Detail View
    # -----------------------------------------------------

    def test_detail_status_code(self):
        self.login()

        response = self.client.get(
            reverse(
                "expense_detail",
                kwargs={"pk": self.expense.pk},
            )
        )

        self.assertEqual(response.status_code, 200)

    def test_detail_template(self):
        self.login()

        response = self.client.get(
            reverse(
                "expense_detail",
                kwargs={"pk": self.expense.pk},
            )
        )

        self.assertTemplateUsed(
            response,
            "expense_detail.html",
        )

    def test_detail_context(self):
        self.login()

        response = self.client.get(
            reverse(
                "expense_detail",
                kwargs={"pk": self.expense.pk},
            )
        )

        self.assertEqual(
            response.context["expense"],
            self.expense,
        )

    def test_user_cannot_view_other_users_expense(self):
        self.login()

        response = self.client.get(
            reverse(
                "expense_detail",
                kwargs={
                    "pk": self.other_expense.pk
                },
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

        # -----------------------------------------------------
    # Create View
    # -----------------------------------------------------

    def test_create_view_get(self):
        self.login()

        response = self.client.get(
            reverse("expense_add")
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "expense_form.html")
        self.assertContains(response, "Save Expense")

    def test_create_expense_success(self):
        self.login()

        expense_count = Expense.objects.count()

        response = self.client.post(
            reverse("expense_add"),
            {
                "title": "Electricity Bill",
                "amount": "3500",
                "category": ExpenseCategory.BILLS,
                "payment_method": PaymentMethod.BANK_TRANSFER,
                "date": timezone.localdate(),
                "note": "Monthly bill",
            },
            follow=True,
        )

        self.assertRedirects(response, reverse("expense_list"))
        self.assertEqual(
            Expense.objects.count(),
            expense_count + 1,
        )

    def test_create_assigns_logged_in_user(self):
        self.login()

        self.client.post(
            reverse("expense_add"),
            {
                "title": "Fuel",
                "amount": "2000",
                "category": ExpenseCategory.TRANSPORT,
                "payment_method": PaymentMethod.CASH,
                "date": timezone.localdate(),
                "note": "",
            },
        )

        expense = Expense.objects.latest("id")

        self.assertEqual(expense.user, self.user)

    def test_create_invalid_form(self):
        self.login()

        response = self.client.post(
            reverse("expense_add"),
            {
                "title": "",
                "amount": "",
                "category": "",
                "payment_method": "",
                "date": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Expense.objects.filter(user=self.user).count(),
            1,
        )

    def test_create_negative_amount(self):
        self.login()

        response = self.client.post(
            reverse("expense_add"),
            {
                "title": "Invalid",
                "amount": "-10",
                "category": ExpenseCategory.FOOD,
                "payment_method": PaymentMethod.CASH,
                "date": timezone.localdate(),
            },
        )

        self.assertFormError(
            response,
            "form",
            "amount",
            "Expense amount must be greater than zero.",
        )

    def test_create_future_date(self):
        self.login()

        response = self.client.post(
            reverse("expense_add"),
            {
                "title": "Future Expense",
                "amount": "100",
                "category": ExpenseCategory.FOOD,
                "payment_method": PaymentMethod.CASH,
                "date": timezone.localdate() + timedelta(days=1),
            },
        )

        self.assertFormError(
            response,
            "form",
            "date",
            "Expense date cannot be in the future.",
        )

    def test_create_trims_note(self):
        self.login()

        self.client.post(
            reverse("expense_add"),
            {
                "title": "Netflix",
                "amount": "1500",
                "category": ExpenseCategory.ENTERTAINMENT,
                "payment_method": PaymentMethod.CREDIT_CARD,
                "date": timezone.localdate(),
                "note": "   Monthly subscription   ",
            },
        )

        expense = Expense.objects.latest("id")

        self.assertEqual(
            expense.note,
            "Monthly subscription",
        )

    def test_create_without_note(self):
        self.login()

        self.client.post(
            reverse("expense_add"),
            {
                "title": "Water Bill",
                "amount": "900",
                "category": ExpenseCategory.BILLS,
                "payment_method": PaymentMethod.CASH,
                "date": timezone.localdate(),
                "note": "",
            },
        )

        expense = Expense.objects.latest("id")

        self.assertEqual(expense.note, "")

    def test_create_redirects_after_success(self):
        self.login()

        response = self.client.post(
            reverse("expense_add"),
            {
                "title": "Gas Bill",
                "amount": "1200",
                "category": ExpenseCategory.BILLS,
                "payment_method": PaymentMethod.CASH,
                "date": timezone.localdate(),
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse("expense_list"),
        )

    def test_success_message_after_create(self):
        self.login()

        response = self.client.post(
            reverse("expense_add"),
            {
                "title": "Internet",
                "amount": "2500",
                "category": ExpenseCategory.BILLS,
                "payment_method": PaymentMethod.CASH,
                "date": timezone.localdate(),
            },
            follow=True,
        )

        messages = list(response.context["messages"])

        self.assertTrue(
            any(
                "Expense added successfully."
                in str(message)
                for message in messages
            )
        )
    
        # -----------------------------------------------------
    # Update View
    # -----------------------------------------------------

    def test_update_view_get(self):
        self.login()

        response = self.client.get(
            reverse(
                "expense_edit",
                kwargs={"pk": self.expense.pk},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "expense_form.html")
        self.assertContains(response, "Edit Expense")

    def test_update_expense_success(self):
        self.login()

        response = self.client.post(
            reverse(
                "expense_edit",
                kwargs={"pk": self.expense.pk},
            ),
            {
                "title": "Updated Internet Bill",
                "amount": "3000",
                "category": ExpenseCategory.BILLS,
                "payment_method": PaymentMethod.BANK_TRANSFER,
                "date": timezone.localdate(),
                "note": "Updated note",
            },
            follow=True,
        )

        self.assertRedirects(response, reverse("expense_list"))

        self.expense.refresh_from_db()

        self.assertEqual(
            self.expense.title,
            "Updated Internet Bill",
        )

        self.assertEqual(
            self.expense.amount,
            Decimal("3000"),
        )

        self.assertEqual(
            self.expense.payment_method,
            PaymentMethod.BANK_TRANSFER,
        )

    def test_update_invalid_data(self):
        self.login()

        response = self.client.post(
            reverse(
                "expense_edit",
                kwargs={"pk": self.expense.pk},
            ),
            {
                "title": "",
                "amount": "",
                "category": "",
                "payment_method": "",
                "date": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response,
            "form",
            "title",
            "This field is required.",
        )

    def test_user_cannot_update_other_users_expense(self):
        self.login()

        response = self.client.get(
            reverse(
                "expense_edit",
                kwargs={"pk": self.other_expense.pk},
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_success_message_after_update(self):
        self.login()

        response = self.client.post(
            reverse(
                "expense_edit",
                kwargs={"pk": self.expense.pk},
            ),
            {
                "title": "Updated",
                "amount": "2500",
                "category": ExpenseCategory.BILLS,
                "payment_method": PaymentMethod.CASH,
                "date": timezone.localdate(),
            },
            follow=True,
        )

        messages = list(response.context["messages"])

        self.assertTrue(
            any(
                "Expense updated successfully."
                in str(message)
                for message in messages
            )
        )

    # -----------------------------------------------------
    # Delete View
    # -----------------------------------------------------

    def test_delete_expense(self):
        self.login()

        expense_id = self.expense.pk

        response = self.client.post(
            reverse(
                "expense_delete",
                kwargs={"pk": expense_id},
            ),
        )

        self.assertRedirects(
            response,
            reverse("expense_list"),
        )

        self.assertFalse(
            Expense.objects.filter(
                pk=expense_id
            ).exists()
        )

    def test_delete_other_users_expense(self):
        self.login()

        response = self.client.post(
            reverse(
                "expense_delete",
                kwargs={
                    "pk": self.other_expense.pk
                },
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    # -----------------------------------------------------
    # AJAX Delete
    # -----------------------------------------------------

    def test_ajax_delete_returns_json(self):
        self.login()

        expense = Expense.objects.create(
            user=self.user,
            title="Temporary",
            amount=100,
            category=ExpenseCategory.FOOD,
            payment_method=PaymentMethod.CASH,
            date=timezone.localdate(),
        )

        response = self.client.post(
            reverse(
                "expense_delete",
                kwargs={"pk": expense.pk},
            ),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {"success": True},
        )

    def test_ajax_delete_removes_record(self):
        self.login()

        expense = Expense.objects.create(
            user=self.user,
            title="Delete Me",
            amount=100,
            category=ExpenseCategory.FOOD,
            payment_method=PaymentMethod.CASH,
            date=timezone.localdate(),
        )

        self.client.post(
            reverse(
                "expense_delete",
                kwargs={"pk": expense.pk},
            ),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertFalse(
            Expense.objects.filter(
                pk=expense.pk
            ).exists()
        )

    def test_delete_requires_post(self):
        self.login()

        response = self.client.get(
            reverse(
                "expense_delete",
                kwargs={"pk": self.expense.pk},
            )
        )

        self.assertEqual(
            response.status_code,
            405,
        )
    
        # =====================================================
    # Expense List Filters
    # =====================================================

    def test_search_filter(self):
        self.login()

        response = self.client.get(
            reverse("expense_list"),
            {"search": "Internet"},
        )

        self.assertContains(response, "Internet Bill")
        self.assertNotContains(response, "Shopping")

    def test_category_filter(self):
        self.login()

        response = self.client.get(
            reverse("expense_list"),
            {
                "category": ExpenseCategory.BILLS,
            },
        )

        expenses = response.context["expenses"]

        self.assertEqual(expenses.count(), 1)

    def test_payment_method_filter(self):
        self.login()

        response = self.client.get(
            reverse("expense_list"),
            {
                "payment_method": PaymentMethod.CASH,
            },
        )

        expenses = response.context["expenses"]

        self.assertEqual(expenses.count(), 1)

    def test_min_amount_filter(self):
        self.login()

        response = self.client.get(
            reverse("expense_list"),
            {
                "min_amount": 2000,
            },
        )

        expenses = response.context["expenses"]

        self.assertEqual(expenses.count(), 1)

    def test_max_amount_filter(self):
        self.login()

        response = self.client.get(
            reverse("expense_list"),
            {
                "max_amount": 3000,
            },
        )

        expenses = response.context["expenses"]

        self.assertEqual(expenses.count(), 1)

    def test_period_today_filter(self):
        self.login()

        response = self.client.get(
            reverse("expense_list"),
            {
                "period": "today",
            },
        )

        expenses = response.context["expenses"]

        self.assertEqual(expenses.count(), 1)

    def test_sort_highest(self):
        self.login()

        Expense.objects.create(
            user=self.user,
            title="Laptop",
            amount=7000,
            category=ExpenseCategory.OTHER,
            payment_method=PaymentMethod.CASH,
            date=timezone.localdate(),
        )

        response = self.client.get(
            reverse("expense_list"),
            {
                "sort": "highest",
            },
        )

        expenses = list(response.context["expenses"])

        self.assertEqual(expenses[0].title, "Laptop")

    # =====================================================
    # Pagination
    # =====================================================

    def test_pagination(self):
        self.login()

        for i in range(20):
            Expense.objects.create(
                user=self.user,
                title=f"Expense {i}",
                amount=100,
                category=ExpenseCategory.FOOD,
                payment_method=PaymentMethod.CASH,
                date=timezone.localdate(),
            )

        response = self.client.get(
            reverse("expense_list")
        )

        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(
            len(response.context["expenses"]),
            15,
        )

    def test_second_page(self):
        self.login()

        for i in range(20):
            Expense.objects.create(
                user=self.user,
                title=f"Expense {i}",
                amount=100,
                category=ExpenseCategory.FOOD,
                payment_method=PaymentMethod.CASH,
                date=timezone.localdate(),
            )

        response = self.client.get(
            reverse("expense_list"),
            {
                "page": 2,
            },
        )

        self.assertEqual(
            response.context["page_obj"].number,
            2,
        )

    # =====================================================
    # AJAX
    # =====================================================

    def test_ajax_returns_json(self):
        self.login()

        response = self.client.get(
            reverse("expense_list"),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Type"],
            "application/json",
        )

        self.assertIn(
            "html",
            response.json(),
        )

    def test_ajax_contains_table(self):
        self.login()

        response = self.client.get(
            reverse("expense_list"),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        html = response.json()["html"]

        self.assertIn("<table", html)
        self.assertIn("Internet Bill", html)

    # =====================================================
    # Query String
    # =====================================================

    def test_query_string_preserved(self):
        self.login()

        response = self.client.get(
            reverse("expense_list"),
            {
                "category": ExpenseCategory.BILLS,
                "sort": "highest",
            },
        )

        self.assertIn(
            "query_string",
            response.context,
        )

    # =====================================================
    # Empty State
    # =====================================================

    def test_empty_expense_list(self):
        Expense.objects.all().delete()

        self.login()

        response = self.client.get(
            reverse("expense_list")
        )

        self.assertContains(
            response,
            "No expense records found",
        )