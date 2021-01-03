from django.urls import path

from .api import get_analytics, get_avail_periods

urlpatterns = [
    path("analytics/", get_analytics),
    path("periods/", get_avail_periods)
]
