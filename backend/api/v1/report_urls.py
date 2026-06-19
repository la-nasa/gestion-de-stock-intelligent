from django.urls import path
from api.v1.views.report_views import ReportGenerateView, ReportHistoryView

urlpatterns = [
    path('reports/generate/', ReportGenerateView.as_view(), name='reports-generate'),
    path('reports/history/', ReportHistoryView.as_view(), name='reports-history'),
]