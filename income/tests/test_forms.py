from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from income.forms import IncomeForm
from income.models import Income


class IncomeFormTest(TestCase):

    def setUp(self):
        self.valid_data = {
            "title": "Monthly Salary",
            "amount": Decimal("50000.00"),
            "category": Income.Category.SALARY,
            "date": timezone.localdate(),
            "note": "Salary for this month",
        }

    # -------------------------------------------------
    # Valid Form
    # -------------------------------------------------

    def test_form_is_valid(self):
        form = IncomeForm(data=self.valid_data)

        self.assertTrue(form.is_valid())

    # -------------------------------------------------
    # Required Fields
    # -------------------------------------------------

    def test_title_is_required(self):
        data = self.valid_data.copy()
        data["title"] = ""

        form = IncomeForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_amount_is_required(self):
        data = self.valid_data.copy()
        data["amount"] = ""

        form = IncomeForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("amount", form.errors)

    def test_date_is_required(self):
        data = self.valid_data.copy()
        data["date"] = ""

        form = IncomeForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("date", form.errors)

    # -------------------------------------------------
    # Optional Field
    # -------------------------------------------------

    def test_note_is_optional(self):
        data = self.valid_data.copy()
        data["note"] = ""

        form = IncomeForm(data=data)

        self.assertTrue(form.is_valid())

    # -------------------------------------------------
    # Labels
    # -------------------------------------------------

    def test_field_labels(self):
        form = IncomeForm()

        self.assertEqual(form.fields["title"].label, "Title")
        self.assertEqual(form.fields["amount"].label, "Amount")
        self.assertEqual(form.fields["category"].label, "Category")
        self.assertEqual(form.fields["date"].label, "Income Date")
        self.assertEqual(form.fields["note"].label, "Note")

    # -------------------------------------------------
    # Included Fields
    # -------------------------------------------------

    def test_form_fields(self):
        form = IncomeForm()

        self.assertEqual(
            list(form.fields.keys()),
            [
                "title",
                "amount",
                "category",
                "date",
                "note",
            ]
        )

    # -------------------------------------------------
    # Widgets
    # -------------------------------------------------

    def test_title_placeholder(self):
        form = IncomeForm()

        self.assertEqual(
            form.fields["title"].widget.attrs["placeholder"],
            "Enter title"
        )

    def test_amount_placeholder(self):
        form = IncomeForm()

        self.assertEqual(
            form.fields["amount"].widget.attrs["placeholder"],
            "Enter amount"
        )

    def test_note_placeholder(self):
        form = IncomeForm()

        self.assertEqual(
            form.fields["note"].widget.attrs["placeholder"],
            "Optional note..."
        )

    def test_note_rows(self):
        form = IncomeForm()

        self.assertEqual(
            form.fields["note"].widget.attrs["rows"],
            4
        )

    def test_amount_min(self):
        form = IncomeForm()

        self.assertEqual(
            form.fields["amount"].widget.attrs["min"],
            "1"
        )

    def test_amount_step(self):
        form = IncomeForm()

        self.assertEqual(
            form.fields["amount"].widget.attrs["step"],
            "1"
        )

    def test_date_widget_type(self):
        form = IncomeForm()

        self.assertEqual(
            form.fields["date"].widget.attrs["type"],
            "date"
        )

    def test_date_max_attribute(self):
        form = IncomeForm()

        self.assertEqual(
            form.fields["date"].widget.attrs["max"],
            timezone.localdate().isoformat()
        )

    # -------------------------------------------------
    # Required Attribute
    # -------------------------------------------------

    def test_required_attribute_disabled(self):
        form = IncomeForm()

        self.assertFalse(form.use_required_attribute)

    # -------------------------------------------------
    # Invalid Amount
    # -------------------------------------------------

    def test_negative_amount_invalid(self):
        data = self.valid_data.copy()
        data["amount"] = -100

        form = IncomeForm(data=data)

        self.assertFalse(form.is_valid())

    def test_zero_amount_invalid(self):
        data = self.valid_data.copy()
        data["amount"] = 0

        form = IncomeForm(data=data)

        self.assertFalse(form.is_valid())

    # -------------------------------------------------
    # Future Date
    # -------------------------------------------------

    def test_future_date_invalid(self):
        data = self.valid_data.copy()
        data["date"] = timezone.localdate() + timezone.timedelta(days=1)

        form = IncomeForm(data=data)

        self.assertFalse(form.is_valid())