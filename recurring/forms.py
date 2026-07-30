from django import forms

from .models import RecurringTransaction, TransactionType


class DateInput(forms.DateInput):
    input_type = "date"
    

class RecurringTransactionForm(forms.ModelForm):
    """
    Recurring transaction model form.
    """
    use_required_attribute = False
    class Meta:
        model = RecurringTransaction
        exclude = ("user","last_generated_date","next_run","created_at","updated_at",)
        widgets = {
            "start_date": DateInput(),
            "end_date": DateInput(),
            "note": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Optional note...",
                }
            ),
            "title": forms.TextInput(
                attrs={
                    "placeholder": "Example: Netflix Subscription",
                }
            ),
            "amount": forms.NumberInput(
                attrs={
                    "step": "1",
                    "min": "1",
                }
            ),
        }

        labels = {
            "transaction_type": "Transaction Type",
            "income_category": "Income Category",
            "expense_category": "Expense Category",
            "payment_method": "Payment Method",
            "is_active": "Active",
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)

        super().__init__(*args, **kwargs)

        self.fields["end_date"].required = False
        self.fields["note"].required = False
        self.fields["payment_method"].required = False
        self.fields["income_category"].required = False
        self.fields["expense_category"].required = False

        self.toggle_fields()

    def toggle_fields(self):
        transaction_type = None

        if self.is_bound:
            transaction_type = self.data.get("transaction_type")

        elif self.instance.pk:
            transaction_type = self.instance.transaction_type

        if transaction_type == TransactionType.INCOME:
            self.fields["expense_category"].widget = forms.HiddenInput()
            self.fields["payment_method"].widget = forms.HiddenInput()

        elif transaction_type == TransactionType.EXPENSE:
            self.fields["income_category"].widget = forms.HiddenInput()

    def clean(self):
        cleaned_data = super().clean()

        transaction_type = cleaned_data.get("transaction_type")
        income_category = cleaned_data.get("income_category")
        expense_category = cleaned_data.get("expense_category")
        payment_method = cleaned_data.get("payment_method")

        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date:
            if end_date < start_date:
                self.add_error("end_date","End date cannot be before start date.")

        if transaction_type == TransactionType.INCOME:

            if not income_category:
                self.add_error("income_category","Please select an income category.")

            cleaned_data["expense_category"] = ""
            cleaned_data["payment_method"] = ""

        elif transaction_type == TransactionType.EXPENSE:

            if not expense_category:
                self.add_error("expense_category","Please select an expense category.")

            if not payment_method:
                self.add_error("payment_method","Please select a payment method.")
                
            cleaned_data["income_category"] = ""

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        if self.user is not None:
            instance.user = self.user

        if commit:
            instance.save()

        return instance