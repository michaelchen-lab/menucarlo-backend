from django.urls import path

from .api import get_analytics

urlpatterns = [
    path("analytics/", get_analytics)
]
