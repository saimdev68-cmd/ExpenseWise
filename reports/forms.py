from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date
from django import forms


def get_year_choices():
    current_year = date.today().year
    return [(year, year)for year in range(current_year - 5, current_year + 1 )]


MONTH_CHOICES = [
    (1, "January"),
    (2, "February"),
    (3, "March"),
    (4, "April"),
    (5, "May"),
    (6, "June"),
    (7, "July"),
    (8, "August"),
    (9, "September"),
    (10, "October"),
    (11, "November"),
    (12, "December"),
]


class MonthlyReportForm(forms.Form):
    """
    Monthly Report Form.
    """
    month = forms.ChoiceField(label="Month",choices=MONTH_CHOICES,)
    year = forms.ChoiceField(label="Year",choices=get_year_choices,)

    def clean_month(self):
        month = int(self.cleaned_data["month"])
        if month < 1 or month > 12:
            raise ValidationError("Please select a valid month.")
        return month

    def clean_year(self):
        year = int(self.cleaned_data["year"])
        if year < 1900:
            raise ValidationError("Please select a valid year.")
        return year


class YearlyReportForm(forms.Form):
    """
    Yearly Report Form.
    """
    year = forms.ChoiceField(label="Year",choices=get_year_choices)
    def clean_year(self):
        year = int(self.cleaned_data["year"])
        if year < 1900:
            raise ValidationError("Please select a valid year.")
        return year


class CustomReportForm(forms.Form):
    """
    Custom Date Range Form.
    """
    start_date = forms.DateField(
        label="Start Date",
        widget=forms.DateInput(
            attrs={"type": "date"},
        ),
    )

    end_date = forms.DateField(
        label="End Date",
        widget=forms.DateInput(
            attrs={"type": "date","max":timezone.localdate().isoformat()},
        ),
    )

    def clean(self):
        cleaned_data = super().clean()

        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date:
            if end_date < start_date:
                raise ValidationError(
                    "End date must be greater than or equal to start date."
                )

        return cleaned_data