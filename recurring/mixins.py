from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse

from .models import RecurringTransaction
from .forms import RecurringTransactionForm


class RecurringTransactionQuerySetMixin(LoginRequiredMixin):
    """
    Recurring Transaction QuerySet Mixin.
    """
    model = RecurringTransaction

    def get_queryset(self):
        return RecurringTransaction.objects.filter(user=self.request.user).order_by("-created_at")
    

class RecurringFormMixin:
    """
    Recurring Form Mixin.
    """
    model = RecurringTransaction
    form_class = RecurringTransactionForm
    template_name = "recurringtransaction_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        self.object = form.save()

        if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({
                "success": True,
                "redirect_url": str(self.success_url),
            })

        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
            errors = {}
            for field, error_list in form.errors.items():
                errors[field] = [str(error) for error in error_list]
            
            return JsonResponse({
                "success": False,
                "errors": errors,
            }, status=400)

        return super().form_invalid(form)