from django.urls import path

from . import views


urlpatterns = [
    path("monthly/",views.MonthlyReportView.as_view(),name="monthly_report",),
    path("yearly/",views.YearlyReportView.as_view(),name="yearly_report",),
    path("custom/",views.CustomReportView.as_view(),name="custom_report",),
    path("monthly/pdf/",views.MonthlyPDFView.as_view(),name="monthly_pdf",),
    path("yearly/pdf/",views.YearlyPDFView.as_view(),name="yearly_pdf",),
    path("custom/pdf/",views.CustomPDFView.as_view(),name="custom_pdf",),
]