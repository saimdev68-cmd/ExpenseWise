from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from income.models import Income

User = get_user_model()


class IncomeListViewTest(TestCase):

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
            note="Monthly salary",
        )

        cls.income2 = Income.objects.create(
            user=cls.user1,
            title="Freelancing",
            amount=Decimal("15000"),
            category=Income.Category.FREELANCING,
            date=timezone.localdate(),
            note="Website project",
        )

        cls.income3 = Income.objects.create(
            user=cls.user2,
            title="Business",
            amount=Decimal("90000"),
            category=Income.Category.BUSINESS,
            date=timezone.localdate(),
        )

    def setUp(self):
        self.client.login(
            email="user1@example.com",
            password="password123"
        )

    # --------------------------------------------------
    # Authentication
    # --------------------------------------------------

    def test_login_required(self):
        self.client.logout()

        response = self.client.get(reverse("income_list"))

        self.assertEqual(response.status_code, 302)

    # --------------------------------------------------
    # Template
    # --------------------------------------------------

    def test_uses_correct_template(self):
        response = self.client.get(reverse("income_list"))

        self.assertTemplateUsed(
            response,
            "income_list.html"
        )

    # --------------------------------------------------
    # Status
    # --------------------------------------------------

    def test_status_code(self):
        response = self.client.get(reverse("income_list"))

        self.assertEqual(response.status_code, 200)

    # --------------------------------------------------
    # Context
    # --------------------------------------------------

    def test_context_object_name(self):
        response = self.client.get(reverse("income_list"))

        self.assertIn("incomes", response.context)

    def test_categories_in_context(self):
        response = self.client.get(reverse("income_list"))

        self.assertIn("categories", response.context)

    def test_selected_sort_default(self):
        response = self.client.get(reverse("income_list"))

        self.assertEqual(
            response.context["selected_sort"],
            "newest"
        )

    def test_selected_category_default(self):
        response = self.client.get(reverse("income_list"))

        self.assertEqual(
            response.context["selected_category"],
            ""
        )

    def test_selected_period_default(self):
        response = self.client.get(reverse("income_list"))

        self.assertEqual(
            response.context["selected_period"],
            ""
        )

    # --------------------------------------------------
    # User Isolation
    # --------------------------------------------------

    def test_only_logged_in_user_records_returned(self):
        response = self.client.get(reverse("income_list"))

        incomes = response.context["incomes"]

        self.assertEqual(incomes.count(), 2)

        self.assertIn(self.income1, incomes)
        self.assertIn(self.income2, incomes)

        self.assertNotIn(self.income3, incomes)

    # --------------------------------------------------
    # Pagination
    # --------------------------------------------------

    def test_pagination_enabled(self):
        response = self.client.get(reverse("income_list"))

        self.assertTrue(response.context["is_paginated"] is False)

    # --------------------------------------------------
    # Query String
    # --------------------------------------------------

    def test_query_string_exists(self):
        response = self.client.get(reverse("income_list"))

        self.assertIn(
            "query_string",
            response.context
        )

    # --------------------------------------------------
    # AJAX
    # --------------------------------------------------

    def test_ajax_request_returns_json(self):
        response = self.client.get(
            reverse("income_list"),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Type"],
            "application/json"
        )

    def test_ajax_contains_html(self):
        response = self.client.get(
            reverse("income_list"),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )

        self.assertIn(
            "html",
            response.json()
        )

    # --------------------------------------------------
    # Search
    # --------------------------------------------------

    def test_search_by_title(self):
        response = self.client.get(
            reverse("income_list"),
            {
                "q": "Salary"
            }
        )

        incomes = response.context["incomes"]

        self.assertEqual(incomes.count(), 1)
        self.assertEqual(incomes.first(), self.income1)

    # --------------------------------------------------
    # Category
    # --------------------------------------------------

    def test_filter_category(self):
        response = self.client.get(
            reverse("income_list"),
            {
                "category": Income.Category.FREELANCING
            }
        )

        incomes = response.context["incomes"]

        self.assertEqual(incomes.count(), 1)
        self.assertEqual(incomes.first(), self.income2)

    # --------------------------------------------------
    # Empty State
    # --------------------------------------------------

    def test_empty_queryset(self):
        Income.objects.filter(user=self.user1).delete()

        response = self.client.get(
            reverse("income_list")
        )

        self.assertEqual(
            response.context["incomes"].count(),
            0
        )

    # --------------------------------------------------
    # Context Values
    # --------------------------------------------------

    def test_selected_category_context(self):
        response = self.client.get(
            reverse("income_list"),
            {
                "category": Income.Category.SALARY
            }
        )

        self.assertEqual(
            response.context["selected_category"],
            Income.Category.SALARY
        )

    def test_selected_sort_context(self):
        response = self.client.get(
            reverse("income_list"),
            {
                "sort": "highest"
            }
        )

        self.assertEqual(
            response.context["selected_sort"],
            "highest"
        )

    def test_selected_period_context(self):
        response = self.client.get(
            reverse("income_list"),
            {
                "period": "today"
            }
        )

        self.assertEqual(
            response.context["selected_period"],
            "today"
        )

class IncomeDetailViewTest(TestCase):

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

        cls.income = Income.objects.create(
            user=cls.user1,
            title="Salary",
            amount=Decimal("50000"),
            category=Income.Category.SALARY,
            date=timezone.localdate(),
            note="Monthly salary",
        )

        cls.other_income = Income.objects.create(
            user=cls.user2,
            title="Business",
            amount=Decimal("80000"),
            category=Income.Category.BUSINESS,
            date=timezone.localdate(),
        )

    def setUp(self):
        self.client.login(
            email="user1@example.com",
            password="password123",
        )

    # -------------------------------------------------
    # Authentication
    # -------------------------------------------------

    def test_login_required(self):
        self.client.logout()

        response = self.client.get(
            reverse("income_detail", kwargs={"pk": self.income.pk})
        )

        self.assertEqual(response.status_code, 302)

    # -------------------------------------------------
    # Status
    # -------------------------------------------------

    def test_status_code(self):
        response = self.client.get(
            reverse("income_detail", kwargs={"pk": self.income.pk})
        )

        self.assertEqual(response.status_code, 200)

    # -------------------------------------------------
    # Template
    # -------------------------------------------------

    def test_correct_template_used(self):
        response = self.client.get(
            reverse("income_detail", kwargs={"pk": self.income.pk})
        )

        self.assertTemplateUsed(
            response,
            "income_detail.html"
        )

    # -------------------------------------------------
    # Context
    # -------------------------------------------------

    def test_context_object_name(self):
        response = self.client.get(
            reverse("income_detail", kwargs={"pk": self.income.pk})
        )

        self.assertEqual(
            response.context["income"],
            self.income,
        )

    # -------------------------------------------------
    # User Ownership
    # -------------------------------------------------

    def test_user_cannot_view_other_users_income(self):
        response = self.client.get(
            reverse(
                "income_detail",
                kwargs={"pk": self.other_income.pk},
            )
        )

        self.assertEqual(response.status_code, 404)

    # -------------------------------------------------
    # Invalid PK
    # -------------------------------------------------

    def test_invalid_pk_returns_404(self):
        response = self.client.get(
            reverse(
                "income_detail",
                kwargs={"pk": 99999},
            )
        )

        self.assertEqual(response.status_code, 404)

    # -------------------------------------------------
    # Object Values
    # -------------------------------------------------

    def test_correct_income_loaded(self):
        response = self.client.get(
            reverse("income_detail", kwargs={"pk": self.income.pk})
        )

        income = response.context["income"]

        self.assertEqual(income.title, "Salary")
        self.assertEqual(income.amount, Decimal("50000"))
        self.assertEqual(
            income.category,
            Income.Category.SALARY,
        )

    # -------------------------------------------------
    # URL
    # -------------------------------------------------

    def test_detail_url(self):
        url = reverse(
            "income_detail",
            kwargs={"pk": self.income.pk},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    # -------------------------------------------------
    # Queryset Security
    # -------------------------------------------------

    def test_queryset_returns_only_logged_in_user_objects(self):
        response = self.client.get(
            reverse(
                "income_detail",
                kwargs={"pk": self.other_income.pk},
            )
        )

        self.assertEqual(response.status_code, 404)

class IncomeCreateViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            name="user1",
            email="user1@example.com",
            password="password123",
        )

        cls.other_user = User.objects.create_user(
            name="user2",
            email="user2@example.com",
            password="password123",
        )

    def setUp(self):
        self.client.login(
            email="user1@example.com",
            password="password123",
        )

        self.url = reverse("income_add")

        self.valid_data = {
            "title": "Monthly Salary",
            "amount": "50000",
            "category": Income.Category.SALARY,
            "date": timezone.localdate(),
            "note": "Salary received",
        }

    # -------------------------------------------------
    # Authentication
    # -------------------------------------------------

    def test_login_required(self):
        self.client.logout()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)

    # -------------------------------------------------
    # GET
    # -------------------------------------------------

    def test_get_request(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "income_form.html")

    def test_form_exists(self):
        response = self.client.get(self.url)

        self.assertIn("form", response.context)

    # -------------------------------------------------
    # POST
    # -------------------------------------------------

    def test_create_income(self):
        count = Income.objects.count()

        response = self.client.post(
            self.url,
            self.valid_data,
            follow=True,
        )

        self.assertRedirects(
            response,
            reverse("income_list"),
        )

        self.assertEqual(
            Income.objects.count(),
            count + 1,
        )

    def test_created_income_belongs_to_logged_in_user(self):
        self.client.post(
            self.url,
            self.valid_data,
        )

        income = Income.objects.latest("id")

        self.assertEqual(
            income.user,
            self.user,
        )

    def test_user_field_cannot_be_spoofed(self):
        data = self.valid_data.copy()

        data["user"] = self.other_user.pk

        self.client.post(
            self.url,
            data,
        )

        income = Income.objects.latest("id")

        self.assertEqual(
            income.user,
            self.user,
        )

        self.assertNotEqual(
            income.user,
            self.other_user,
        )

    # -------------------------------------------------
    # Data
    # -------------------------------------------------

    def test_income_data_saved_correctly(self):
        self.client.post(
            self.url,
            self.valid_data,
        )

        income = Income.objects.latest("id")

        self.assertEqual(
            income.title,
            "Monthly Salary",
        )

        self.assertEqual(
            income.amount,
            Decimal("50000"),
        )

        self.assertEqual(
            income.category,
            Income.Category.SALARY,
        )

        self.assertEqual(
            income.note,
            "Salary received",
        )

    # -------------------------------------------------
    # Invalid Form
    # -------------------------------------------------

    def test_invalid_post(self):
        response = self.client.post(
            self.url,
            {
                "title": "",
                "amount": "",
            },
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            Income.objects.count(),
            0,
        )

    def test_future_date_not_created(self):
        response = self.client.post(
            self.url,
            {
                "title": "Salary",
                "amount": 500,
                "category": Income.Category.SALARY,
                "date": timezone.localdate() + timezone.timedelta(days=1),
            },
        )

        self.assertFormError(
            response.context["form"],
            "date",
            "Income date cannot be in the future.",
        )

    def test_negative_amount_not_created(self):
        response = self.client.post(
            self.url,
            {
                "title": "Salary",
                "amount": -100,
                "category": Income.Category.SALARY,
                "date": timezone.localdate(),
            },
        )

        self.assertFalse(
            response.context["form"].is_valid()
        )

    # -------------------------------------------------
    # Redirect
    # -------------------------------------------------

    def test_redirect_after_success(self):
        response = self.client.post(
            self.url,
            self.valid_data,
        )

        self.assertRedirects(
            response,
            reverse("income_list"),
            fetch_redirect_response=False,
        )

    # -------------------------------------------------
    # Success Message
    # -------------------------------------------------

    def test_success_message(self):
        response = self.client.post(
            self.url,
            self.valid_data,
            follow=True,
        )

        messages = list(response.context["messages"])

        self.assertEqual(
            str(messages[0]),
            "Income record added successfully.",
        )

class IncomeUpdateViewTest(TestCase):

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

        cls.income = Income.objects.create(
            user=cls.user1,
            title="Salary",
            amount=Decimal("50000"),
            category=Income.Category.SALARY,
            date=timezone.localdate(),
            note="Old note",
        )

        cls.other_income = Income.objects.create(
            user=cls.user2,
            title="Business",
            amount=Decimal("90000"),
            category=Income.Category.BUSINESS,
            date=timezone.localdate(),
        )

    def setUp(self):
        self.client.login(
            email="user1@example.com",
            password="password123",
        )

        self.url = reverse(
            "income_edit",
            kwargs={"pk": self.income.pk},
        )

    # -------------------------------------------------
    # Authentication
    # -------------------------------------------------

    def test_login_required(self):
        self.client.logout()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)

    # -------------------------------------------------
    # GET
    # -------------------------------------------------

    def test_get_request(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "income_form.html")

    def test_form_contains_existing_object(self):
        response = self.client.get(self.url)

        self.assertEqual(
            response.context["object"],
            self.income,
        )

    # -------------------------------------------------
    # Update
    # -------------------------------------------------

    def test_update_income(self):
        response = self.client.post(
            self.url,
            {
                "title": "Updated Salary",
                "amount": "65000",
                "category": Income.Category.SALARY,
                "date": timezone.localdate(),
                "note": "Updated note",
            },
            follow=True,
        )

        self.assertRedirects(
            response,
            reverse("income_list"),
        )

        self.income.refresh_from_db()

        self.assertEqual(
            self.income.title,
            "Updated Salary",
        )

        self.assertEqual(
            self.income.amount,
            Decimal("65000"),
        )

        self.assertEqual(
            self.income.note,
            "Updated note",
        )

    # -------------------------------------------------
    # User Ownership
    # -------------------------------------------------

    def test_user_cannot_edit_other_users_income(self):
        response = self.client.get(
            reverse(
                "income_edit",
                kwargs={"pk": self.other_income.pk},
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_post_other_users_income_returns_404(self):
        response = self.client.post(
            reverse(
                "income_edit",
                kwargs={"pk": self.other_income.pk},
            ),
            {
                "title": "Hack",
                "amount": 100,
                "category": Income.Category.OTHER,
                "date": timezone.localdate(),
            },
        )

        self.assertEqual(response.status_code, 404)

    # -------------------------------------------------
    # Invalid Data
    # -------------------------------------------------

    def test_invalid_update(self):
        response = self.client.post(
            self.url,
            {
                "title": "",
                "amount": "",
                "category": Income.Category.SALARY,
                "date": "",
            },
        )

        self.assertEqual(response.status_code, 200)

        self.income.refresh_from_db()

        self.assertEqual(
            self.income.title,
            "Salary",
        )

    def test_future_date_invalid(self):
        response = self.client.post(
            self.url,
            {
                "title": "Salary",
                "amount": 100,
                "category": Income.Category.SALARY,
                "date": timezone.localdate() + timezone.timedelta(days=1),
            },
        )

        self.assertFalse(
            response.context["form"].is_valid()
        )

    # -------------------------------------------------
    # User cannot change owner
    # -------------------------------------------------

    def test_user_field_cannot_be_changed(self):
        self.client.post(
            self.url,
            {
                "user": self.user2.pk,
                "title": "Salary",
                "amount": 50000,
                "category": Income.Category.SALARY,
                "date": timezone.localdate(),
            },
        )

        self.income.refresh_from_db()

        self.assertEqual(
            self.income.user,
            self.user1,
        )

    # -------------------------------------------------
    # Success Message
    # -------------------------------------------------

    def test_success_message(self):
        response = self.client.post(
            self.url,
            {
                "title": "Updated Salary",
                "amount": "65000",
                "category": Income.Category.SALARY,
                "date": timezone.localdate(),
                "note": "",
            },
            follow=True,
        )

        messages = list(response.context["messages"])

        self.assertEqual(
            str(messages[0]),
            "Income record updated successfully.",
        )

class IncomeDeleteViewTest(TestCase):

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

        cls.income = Income.objects.create(
            user=cls.user1,
            title="Salary",
            amount=Decimal("50000"),
            category=Income.Category.SALARY,
            date=timezone.localdate(),
        )

        cls.other_income = Income.objects.create(
            user=cls.user2,
            title="Business",
            amount=Decimal("90000"),
            category=Income.Category.BUSINESS,
            date=timezone.localdate(),
        )

    def setUp(self):
        self.client.login(
            email="user1@example.com",
            password="password123",
        )

        self.url = reverse(
            "income_delete",
            kwargs={"pk": self.income.pk},
        )

    # -------------------------------------------------
    # Authentication
    # -------------------------------------------------

    def test_login_required(self):
        self.client.logout()

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 302)

    # -------------------------------------------------
    # Delete
    # -------------------------------------------------

    def test_delete_income(self):
        count = Income.objects.count()

        response = self.client.post(
            self.url,
            follow=True,
        )

        self.assertRedirects(
            response,
            reverse("income_list"),
        )

        self.assertEqual(
            Income.objects.count(),
            count - 1,
        )

        self.assertFalse(
            Income.objects.filter(
                pk=self.income.pk
            ).exists()
        )

    # -------------------------------------------------
    # AJAX Delete
    # -------------------------------------------------

    def test_ajax_delete(self):
        response = self.client.post(
            self.url,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)

        self.assertJSONEqual(
            response.content,
            {"success": True},
        )

        self.assertFalse(
            Income.objects.filter(
                pk=self.income.pk
            ).exists()
        )

    # -------------------------------------------------
    # Ownership
    # -------------------------------------------------

    def test_user_cannot_delete_other_users_income(self):
        response = self.client.post(
            reverse(
                "income_delete",
                kwargs={"pk": self.other_income.pk},
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

        self.assertTrue(
            Income.objects.filter(
                pk=self.other_income.pk
            ).exists()
        )

    # -------------------------------------------------
    # Invalid PK
    # -------------------------------------------------

    def test_invalid_pk_returns_404(self):
        response = self.client.post(
            reverse(
                "income_delete",
                kwargs={"pk": 999999},
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    # -------------------------------------------------
    # GET Request
    # -------------------------------------------------

    def test_get_request_not_allowed(self):
        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            405,
        )

    # -------------------------------------------------
    # Redirect
    # -------------------------------------------------

    def test_redirect_after_delete(self):
        response = self.client.post(self.url)

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertEqual(
            response.url,
            reverse("income_list"),
        )

    # -------------------------------------------------
    # Deleted Object
    # -------------------------------------------------

    def test_deleted_object_no_longer_exists(self):
        self.client.post(self.url)

        self.assertEqual(
            Income.objects.filter(
                pk=self.income.pk
            ).count(),
            0,
        )

    # -------------------------------------------------
    # Remaining Records
    # -------------------------------------------------

    def test_other_records_not_deleted(self):
        self.client.post(self.url)

        self.assertTrue(
            Income.objects.filter(
                pk=self.other_income.pk
            ).exists()
        )