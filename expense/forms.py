from django.utils import timezone
from django import forms

from .models import Expense


class ExpenseForm(forms.ModelForm):
    """
    Expense model form.
    """
    use_required_attribute = False
    class Meta:
        model = Expense
        fields = ["title", "amount", "category","payment_method" ,"date", "note"]

        labels = {
            "amount": "Amount",
            'title':"Title",
            "category": "Category",
            "payment_method": "Payment Method",
            "date": "Expense Date",
            "note": "Note",
        }

        widgets = {
            "title":forms.TextInput(
                attrs={
                    "placeholder":"Enter title",
                    "class":"form-control",
                    "autofocus": True,
                }
            ),
            "amount": forms.NumberInput(
                attrs={
                    "placeholder": "Enter expense amount",
                    "step": "1",
                    "min": "1",
                    "class": "form-control",
                }
            ),
            "category": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "payment_method": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "date": forms.DateInput(
                attrs={
                    "type": "date",
                    "max":timezone.localdate().isoformat(),
                    "value":timezone.localdate().isoformat(),
                    "class": "form-control",
                }
            ),
            "note": forms.Textarea(
                attrs={
                    "placeholder": "Optional note...",
                    "rows": 4,
                    "class": "form-control",
                }
            ),
        }
