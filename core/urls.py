from django.urls import path

from .api import get_analytics, get_avail_periods, get_business_name

urlpatterns = [
    path("analytics/", get_analytics),
    path("periods/", get_avail_periods),
    path("name/", get_business_name)
]
