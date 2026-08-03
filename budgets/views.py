from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.loader import render_to_string
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.utils import timezone
from django.views import View

from .utils import calculate_total_budget, calculate_total_spend
from .mixins import BudgetQuerysetMixin, BudgetFormMixin
from .selectors import budget_filter
from .models import Budget
from django.contrib import messages

class BudgetListView(BudgetQuerysetMixin, ListView):
    """
    Budgets List View.
    """
    template_name = "budget_list.html"
    context_object_name = "budgets"
    paginate_by = 10
    current_year = timezone.now().year

    def get_queryset(self):
        return budget_filter(super().get_queryset(), self.request.GET)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        total_budget = calculate_total_budget(self.get_queryset())["total_budget"]
        total_spent = calculate_total_spend(self.get_queryset())
        query_params = self.request.GET.copy()
        query_params.pop('page', None)

        context['query_string'] = query_params.urlencode()
        context["total_budget"] = total_budget
        context["total_spent"] = total_spent
        context["total_remaining"] = total_budget - total_spent
        context["categories"] = Budget._meta.get_field("category").choices
        context["months"] = Budget.MONTH_CHOICES
        context["years"] = [year for year in range(self.current_year - 5, self.current_year + 6)]

        return context
    
    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            html = render_to_string('partials/budget_table.html', context, request=self.request)
            return JsonResponse({"html": html})
        return super().render_to_response(context, **response_kwargs)


class BudgetCreateView(LoginRequiredMixin,SuccessMessageMixin,BudgetFormMixin,CreateView):
    """
    Budget Create View.
    """
    success_url = reverse_lazy("budget_list")
    success_message = "Budget created successfully."


class BudgetDetailView(BudgetQuerysetMixin, DetailView):
    """
    Budget Detail View.
    """
    template_name = "budget_detail.html"
    context_object_name = "budget"


class BudgetUpdateView(BudgetQuerysetMixin,SuccessMessageMixin,BudgetFormMixin,UpdateView):
    """
    Budget Edit View.
    """
    success_url = reverse_lazy("budget_list")
    success_message = "Budget updated successfully."


class BudgetDeleteView(BudgetQuerysetMixin, DeleteView):
    """
    Budget Delete View.
    """
    success_url = reverse_lazy("budget_list")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            queryset = budget_filter(self.get_queryset(), request.GET)
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
        
        messages.success(request, "Budget deleted successfully.")
        return redirect("budget_list")


class CheckBudgetExistView(LoginRequiredMixin,View):
    """
    Check Budget Validation.
    """
    def get(self,request):
        if request.headers.get("X-Requested-With") != "XMLHttpRequest":
                return JsonResponse({"valid": False}, status=400)
        
        category = request.GET.get("category")
        month = request.GET.get("month")
        year = request.GET.get("year")
    
        qs = Budget.objects.filter(user=request.user,category=category,month=month,year=year)
        budget_id = request.GET.get("budget_id")
        if budget_id:
            qs = qs.exclude(pk=budget_id)
        return JsonResponse({"exists": qs.exists()})