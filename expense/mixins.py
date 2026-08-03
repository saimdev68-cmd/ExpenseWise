from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import ExpenseForm
from .models import Expense


class ExpenseQuerysetMixin(LoginRequiredMixin):
    """
    Expense QuerySet Mixin.
    """
    model = Expense

    def get_queryset(self):
        return Expense.objects.for_user(self.request.user).select_related("user")
    
    
class ExpenseFormMixin:
    """
    Expense Form Mixin.
    """
    model = Expense
    form_class = ExpenseForm
    template_name = "expense_form.html"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)