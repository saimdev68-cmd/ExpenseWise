from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse

from .forms import BudgetForm
from .models import Budget


class BudgetQuerysetMixin(LoginRequiredMixin):
    model = Budget

    def get_queryset(self):
        return Budget.objects.with_spent().filter(user=self.request.user).select_related("user")
    
class BudgetFormMixin:
    form_class = BudgetForm
    template_name = "budget_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)