from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin

from django.template.loader  import render_to_string
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.http import JsonResponse

from .mixins import ExpenseQuerysetMixin , ExpenseFormMixin
from .selectors import expense_filter
from .utils import calculate_total_expense
from .models import Expense


class ExpenseListView(ExpenseQuerysetMixin, ListView):
    """
    User Expense List.
    """
    template_name = "expense_list.html"
    context_object_name = "expenses"
    paginate_by = 10

    def get_queryset(self):
        return expense_filter(super().get_queryset(),self.request.GET)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query_params = self.request.GET.copy()
        query_params.pop("page", None)
        context["total_amount"] = calculate_total_expense(self.get_queryset())
        context["payment_methods"] = Expense._meta.get_field("payment_method").choices
        context["categories"] = Expense._meta.get_field("category").choices
        context["query_string"] = query_params.urlencode()
        return context
    
    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            html = render_to_string(
                'partials/expense_table.html',
                context,
                request=self.request
            )
            return JsonResponse({"html":html})
        return super().render_to_response(context, **response_kwargs)
    

class ExpenseCreateView(LoginRequiredMixin, ExpenseFormMixin,SuccessMessageMixin,CreateView):
    """
    Create New Expense.
    """
    success_url = reverse_lazy("expense_list")
    success_message = "Expense added successfully."


class ExpenseDetailView(ExpenseQuerysetMixin, DetailView):
    """
    View Expense Detail.
    """
    template_name = "expense_detail.html"
    context_object_name = "expense"


class ExpenseUpdateView(ExpenseQuerysetMixin, ExpenseFormMixin,SuccessMessageMixin,UpdateView):
    """
    Edit Expense .
    """
    success_url = reverse_lazy("expense_list")
    success_message = "Expense updated successfully."


class ExpenseDeleteView(ExpenseQuerysetMixin, DeleteView):
    """
    Delete Expense.
    """
    success_url = reverse_lazy("expense_list")

    def post(self, request, *args, **kwargs):
        self.get_object().delete()
        queryset = expense_filter(self.get_queryset(), request.GET)
        
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            per_page = request.GET.get('per_page', 10)
            try:
                per_page = int(per_page)
            except (ValueError, TypeError):
                per_page = 10
            
            return JsonResponse({
                "success": True,
                "total_count": queryset.count(),
                "per_page": per_page,
            })
        return redirect(self.success_url)