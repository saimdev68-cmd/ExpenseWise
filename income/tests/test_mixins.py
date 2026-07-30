from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.utils import timezone
from django.views.generic import CreateView

from income.mixins import IncomeFormMixin, IncomeQuerysetMixin
from income.forms import IncomeForm
from income.models import Income

User = get_user_model()


class DummyQuerysetView(IncomeQuerysetMixin):
    pass


class DummyCreateView(IncomeFormMixin, CreateView):
    model = Income
    form_class = IncomeForm


class IncomeQuerysetMixinTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.factory = RequestFactory()

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
            user=cls.user2,
            title="Business",
            amount=Decimal("90000"),
            category=Income.Category.BUSINESS,
            date=timezone.localdate(),
        )

    def test_queryset_returns_only_logged_in_user(self):
        request = self.factory.get("/")
        request.user = self.user1

        view = DummyQuerysetView()
        view.request = request

        queryset = view.get_queryset()

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first(), self.income1)

    def test_queryset_excludes_other_users(self):
        request = self.factory.get("/")
        request.user = self.user1

        view = DummyQuerysetView()
        view.request = request

        queryset = view.get_queryset()

        self.assertNotIn(self.income2, queryset)

    def test_queryset_uses_select_related(self):
        request = self.factory.get("/")
        request.user = self.user1

        view = DummyQuerysetView()
        view.request = request

        queryset = view.get_queryset()

        self.assertIn("user", queryset.query.select_related)


class IncomeFormMixinTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.factory = RequestFactory()

        cls.user = User.objects.create_user(
            name="user1",
            email="user1@example.com",
            password="password123",
        )

    def test_model(self):
        view = DummyCreateView()

        self.assertEqual(view.model, Income)

    def test_form_class(self):
        view = DummyCreateView()

        self.assertEqual(view.form_class, IncomeForm)

    def test_template_name(self):
        view = DummyCreateView()

        self.assertEqual(
            view.template_name,
            "income_form.html",
        )

    def test_form_valid_sets_logged_in_user(self):
        request = self.factory.post("/")
        request.user = self.user

        form = IncomeForm(
            data={
                "title": "Salary",
                "amount": 50000,
                "category": Income.Category.SALARY,
                "date": timezone.localdate(),
                "note": "",
            }
        )

        self.assertTrue(form.is_valid())

        view = DummyCreateView()
        view.request = request

        form.instance.user = None

        view.form_valid(form)

        self.assertEqual(
            form.instance.user,
            self.user,
        )