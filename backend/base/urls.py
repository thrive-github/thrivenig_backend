from .views import ReportClaim
from django.urls import path


urlpatterns = [
    path("report-claim/", ReportClaim.as_view(), name="report-claim"),
]
