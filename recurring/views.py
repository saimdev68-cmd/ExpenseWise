from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from .mixins import RecurringTransactionQuerySetMixin, RecurringFormMixin
from .models import TransactionType, Frequency
from .selectors import recurring_filter
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import redirect


class RecurringTransactionListView(RecurringTransactionQuerySetMixin, ListView):
    template_name = "recurringtransaction_list.html"
    context_object_name = "transactions"
    paginate_by = 10

    def get_queryset(self):
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['transaction_types'] = TransactionType.choices
        context['frequencies'] = Frequency.choices
        context["selected_status"] = self.request.GET.get("status", "")
        context["selected_type"] = self.request.GET.get("type", "")
        context["selected_frequency"] = self.request.GET.get("frequency", "")
        params_query = self.request.GET.copy()
        params_query.pop('page', None)
        context["params_string"] = params_query.urlencode()
        return context
    
    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            html = render_to_string('partials/recurringtransaction_table.html', context, request=self.request)
            return JsonResponse({"html": html})
        return super().render_to_response(context, **response_kwargs)


class RecurringTransactionDetailView(RecurringTransactionQuerySetMixin, DetailView):
    template_name = "recurringtransaction_detail.html"
    context_object_name = "transaction"


class RecurringTransactionCreateView(LoginRequiredMixin, RecurringFormMixin, CreateView):
    success_url = reverse_lazy("recurring_list")


class RecurringTransactionUpdateView(RecurringTransactionQuerySetMixin, RecurringFormMixin, UpdateView):
    success_url = reverse_lazy("recurring_list")


class RecurringTransactionDeleteView(RecurringTransactionQuerySetMixin, DeleteView):
    success_url = reverse_lazy("recurring_list")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Get filtered queryset with all applied filters
            queryset = recurring_filter(self.get_queryset(), request.GET)
            
            # Get pagination parameters
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
        
        return redirect("recurring_list")