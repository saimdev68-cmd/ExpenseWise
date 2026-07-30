from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin

from django.template.loader import render_to_string
from django.shortcuts import redirect
from django.http import JsonResponse
from django.urls import reverse_lazy

from .mixins import IncomeFormMixin, IncomeQuerysetMixin
from .selectors import filter_income
from .utils import calculate_total_income
from .models import Income


class IncomeListView(IncomeQuerysetMixin, ListView):
    template_name = "income_list.html"
    context_object_name = "incomes"
    paginate_by = 10

    def get_queryset(self):
        return filter_income(super().get_queryset(), self.request.GET)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query_params = self.request.GET.copy()
        query_params.pop("page", None)
        context["categories"] = Income.Category.choices
        context["query_string"] = query_params.urlencode()
        context["total_amount"] = calculate_total_income(self.get_queryset())
        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
            html = render_to_string(
                "partials/income_table.html",
                context,
                request=self.request,
            )
            return JsonResponse({"html": html})
        return super().render_to_response(context, **response_kwargs)


class IncomeDetailView(IncomeQuerysetMixin, DetailView):
    template_name = "income_detail.html"
    context_object_name = "income"


class IncomeCreateView(LoginRequiredMixin,SuccessMessageMixin,IncomeFormMixin,CreateView):
    success_url = reverse_lazy("income_list")
    success_message = "Income record added successfully."


class IncomeUpdateView(IncomeQuerysetMixin,SuccessMessageMixin,IncomeFormMixin,UpdateView):
    success_url = reverse_lazy("income_list")
    success_message = "Income record updated successfully."


class IncomeDeleteView(IncomeQuerysetMixin, DeleteView):
    success_url = reverse_lazy("income_list")

    def post(self, request, *args, **kwargs):
        self.get_object().delete()
        queryset = filter_income(self.get_queryset(), request.GET)
        
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