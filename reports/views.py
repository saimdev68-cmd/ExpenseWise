from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.http import Http404, HttpResponse
from datetime import datetime
from django.views import View

from .utils import get_monthly_report ,get_yearly_report ,get_custom_report
from .forms import MonthlyReportForm,YearlyReportForm,CustomReportForm
from .pdf import generate_report_pdf

class MonthlyReportView(LoginRequiredMixin, TemplateView):
    template_name = "monthly_report.html"

    def get(self, request, *args, **kwargs):
        form = MonthlyReportForm(request.GET or None)
        report = None
        if form.is_valid():
            report = get_monthly_report(user=request.user,month=form.cleaned_data["month"],year=form.cleaned_data["year"])
        context = {"form": form,"report": report}
        return self.render_to_response(context)

class YearlyReportView(LoginRequiredMixin, TemplateView):
    template_name = "yearly_report.html"

    def get(self, request, *args, **kwargs):
        form = YearlyReportForm(request.GET or None)
        report = None
        if form.is_valid():
            report = get_yearly_report(user=request.user,year=form.cleaned_data["year"])
        context = {"form": form,"report": report}
        return self.render_to_response(context)


class CustomReportView(LoginRequiredMixin, TemplateView):
    template_name = "custom_report.html"

    def get(self, request, *args, **kwargs):
        form = CustomReportForm(request.GET or None)
        report = None
        if form.is_valid():
            report = get_custom_report(user=request.user,start_date=form.cleaned_data["start_date"],end_date=form.cleaned_data["end_date"])
        context = {"form": form,"report": report}
        return self.render_to_response(context)
    
class MonthlyPDFView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        month = request.GET.get("month")
        year = request.GET.get("year")
        if not month or not year:
            raise Http404("Invalid report parameters.")
        month = int(month)
        year = int(year)
        report = get_monthly_report(user=request.user,month=month,year=year)
        report_period = datetime(year, month, 1).strftime("%B %Y")
        pdf = generate_report_pdf(username=request.user.name,report_title="Monthly Financial Report",report_period=report_period,report=report)
        response = HttpResponse(pdf,content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="monthly_report_{year}_{month}.pdf"'
        return response
    
class YearlyPDFView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        year = request.GET.get("year")
        if not year:
            raise Http404("Invalid report parameters.")
        year = int(year)
        report = get_yearly_report(user=request.user,year=year)
        pdf = generate_report_pdf(username=request.user.name,report_title="Yearly Financial Report",report_period=str(year),report=report)
        response = HttpResponse(pdf,content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="yearly_report_{year}.pdf"'

        return response
    
class CustomPDFView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = CustomReportForm(request.GET)
        if not form.is_valid():
            return HttpResponse("Invalid report parameters.", status=400)
        start_date = form.cleaned_data["start_date"]
        end_date = form.cleaned_data["end_date"]
        report = get_custom_report(user=request.user,start_date=start_date,end_date=end_date,)
        pdf = generate_report_pdf(username=request.user.name,report_title="Custom Date Report",report_period=f"{start_date} to {end_date}",report=report)
        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="custom_report.pdf"'
        return response