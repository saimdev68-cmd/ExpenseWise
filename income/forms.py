from django.utils import timezone
from django import forms

from .models import Income


class IncomeForm(forms.ModelForm):
    """
    Income model form.
    """
    use_required_attribute = False

    class Meta:
        model = Income
        fields = ["title", "amount", "category", "date", "note"]
        labels = {
            "title": "Title",
            "amount": "Amount",
            "category": "Category",
            "date": "Income Date",
            "note": "Note",
        }
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "placeholder": "Enter title",
                    "class":"form-control",
                    "autofocus": True,
                }
            ),
            "amount": forms.NumberInput(
                attrs={
                    "placeholder": "Enter amount",
                    "step": "1",
                    "min":"1",
                    "class": "form-control",
                }
            ),
            "category": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "date": forms.DateInput(
                attrs={
                    "type": "date",
                    "max": timezone.localdate().isoformat(),
                    "value": timezone.localdate().isoformat(),
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