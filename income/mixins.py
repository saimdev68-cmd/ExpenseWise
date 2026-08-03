from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import IncomeForm
from .models import Income


class IncomeQuerysetMixin(LoginRequiredMixin):
    """
    Income QuerySet Mixin.
    """
    model = Income

    def get_queryset(self):
        return Income.objects.for_user(self.request.user).select_related("user")


class IncomeFormMixin:
    """
    Income Form Mixin.
    """
    model = Income
    form_class = IncomeForm
    template_name = "income_form.html"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)