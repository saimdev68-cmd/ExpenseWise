from django.urls import path

from . import views


urlpatterns = [
    path("",views.RecurringTransactionListView.as_view(),name="recurring_list"),
    path("add/",views.RecurringTransactionCreateView.as_view(),name="recurring_add"),
    path("<int:pk>/",views.RecurringTransactionDetailView.as_view(),name="recurring_detail"),
    path("<int:pk>/edit/",views.RecurringTransactionUpdateView.as_view(),name="recurring_edit"),
    path("<int:pk>/delete/",views.RecurringTransactionDeleteView.as_view(),name="recurring_delete"),
]
