from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from expense.forms import ExpenseForm
from expense.models import ExpenseCategory, PaymentMethod


class ExpenseFormTest(TestCase):

    def setUp(self):
        self.valid_data = {
            "title": "Internet Bill",
            "amount": Decimal("2500.00"),
            "category": ExpenseCategory.BILLS,
            "payment_method": PaymentMethod.CASH,
            "date": timezone.localdate(),
            "note": "Monthly internet bill",
        }

    # ---------------------------------------------------------
    # Valid Form
    # ---------------------------------------------------------

    def test_form_is_valid_with_correct_data(self):
        form = ExpenseForm(data=self.valid_data)

        self.assertTrue(form.is_valid())

    # ---------------------------------------------------------
    # Required Fields
    # ---------------------------------------------------------

    def test_title_is_required(self):
        data = self.valid_data.copy()
        data["title"] = ""

        form = ExpenseForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_amount_is_required(self):
        data = self.valid_data.copy()
        data["amount"] = ""

        form = ExpenseForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("amount", form.errors)

    def test_category_is_required(self):
        data = self.valid_data.copy()
        data["category"] = ""

        form = ExpenseForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("category", form.errors)

    def test_payment_method_is_required(self):
        data = self.valid_data.copy()
        data["payment_method"] = ""

        form = ExpenseForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("payment_method", form.errors)

    def test_date_is_required(self):
        data = self.valid_data.copy()
        data["date"] = ""

        form = ExpenseForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("date", form.errors)

    # ---------------------------------------------------------
    # Optional Field
    # ---------------------------------------------------------

    def test_note_is_optional(self):
        data = self.valid_data.copy()
        data["note"] = ""

        form = ExpenseForm(data=data)

        self.assertTrue(form.is_valid())

    # ---------------------------------------------------------
    # Model Validation
    # ---------------------------------------------------------

    def test_negative_amount_invalid(self):
        data = self.valid_data.copy()
        data["amount"] = -100

        form = ExpenseForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("amount", form.errors)

    def test_zero_amount_invalid(self):
        data = self.valid_data.copy()
        data["amount"] = 0

        form = ExpenseForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("amount", form.errors)

    def test_future_date_invalid(self):
        data = self.valid_data.copy()
        data["date"] = timezone.localdate() + timedelta(days=1)

        form = ExpenseForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("date", form.errors)

    # ---------------------------------------------------------
    # Labels
    # ---------------------------------------------------------

    def test_labels(self):
        form = ExpenseForm()

        self.assertEqual(form.fields["title"].label, "Title")
        self.assertEqual(form.fields["amount"].label, "Amount")
        self.assertEqual(form.fields["category"].label, "Category")
        self.assertEqual(form.fields["payment_method"].label, "Payment Method")
        self.assertEqual(form.fields["date"].label, "Expense Date")
        self.assertEqual(form.fields["note"].label, "Note")

    # ---------------------------------------------------------
    # Widgets
    # ---------------------------------------------------------

    def test_title_widget(self):
        field = ExpenseForm().fields["title"]

        self.assertEqual(field.widget.attrs["placeholder"], "Enter title")
        self.assertEqual(field.widget.attrs["class"], "form-control")
        self.assertTrue(field.widget.attrs["autofocus"])

    def test_amount_widget(self):
        field = ExpenseForm().fields["amount"]

        self.assertEqual(field.widget.attrs["class"], "form-control")
        self.assertEqual(field.widget.attrs["step"], "1")
        self.assertEqual(field.widget.attrs["min"], "1")

    def test_category_widget(self):
        field = ExpenseForm().fields["category"]

        self.assertEqual(field.widget.attrs["class"], "form-select")

    def test_payment_method_widget(self):
        field = ExpenseForm().fields["payment_method"]

        self.assertEqual(field.widget.attrs["class"], "form-select")

    def test_date_widget(self):
        field = ExpenseForm().fields["date"]

        self.assertEqual(field.widget.attrs["type"], "date")
        self.assertEqual(field.widget.attrs["class"], "form-control")
        self.assertEqual(
            field.widget.attrs["max"],
            timezone.localdate().isoformat(),
        )

    def test_note_widget(self):
        field = ExpenseForm().fields["note"]

        self.assertEqual(field.widget.attrs["rows"], 4)
        self.assertEqual(field.widget.attrs["class"], "form-control")

    # ---------------------------------------------------------
    # Fields
    # ---------------------------------------------------------

    def test_form_contains_expected_fields(self):
        form = ExpenseForm()

        self.assertEqual(
            list(form.fields.keys()),
            [
                "title",
                "amount",
                "category",
                "payment_method",
                "date",
                "note",
            ],
        )

    def test_required_attribute_disabled(self):
        form = ExpenseForm()

        self.assertFalse(form.use_required_attribute)