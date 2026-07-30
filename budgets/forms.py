from django.core.exceptions import ValidationError
from django.utils import timezone
from django import forms

from .models import Budget


class BudgetForm(forms.ModelForm):
    """
    Budget model form.
    """
    use_required_attribute = False

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        current_year = timezone.now().year

        self.fields["month"].choices = Budget.MONTH_CHOICES
        self.fields["year"] = forms.TypedChoiceField(
            choices=[
                (year, year)
                for year in range(current_year - 5, current_year + 6)
            ],
            coerce=int,
            widget=forms.Select(attrs={"class": "form-control"}),
        )

        self.fields["category"].widget.attrs.update({"class": "form-control"})
        self.fields["amount"].widget.attrs.update(
            {
                "type": "number",
                "step": "1",
                "min": "1",
                "placeholder": "Enter budget amount",
                "class": "form-control",
            }
        )

        self.fields["month"].widget.attrs.update({"class": "form-control"})
        self.fields["year"].widget.attrs.update({"class": "form-control"})

    class Meta:
        model = Budget

        fields = ("category","amount","month","year")
        widgets = {
            "category": forms.Select(),
            "month": forms.Select(),
            "year": forms.Select(),
            "amount": forms.NumberInput(),
        }


    def clean(self):
        cleaned_data = super().clean()

        if not self.user:
            return cleaned_data

        category = cleaned_data.get("category")
        month = cleaned_data.get("month")
        year = cleaned_data.get("year")

        if not all([category, month, year]):
            return cleaned_data

        queryset = Budget.objects.filter(user=self.user,category=category,month=month,year=year)

        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise ValidationError("A budget already exists for this category, month, and year.")

        return cleaned_data