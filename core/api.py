from datetime import datetime

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .utils import get_dates_from_request

@api_view()
@permission_classes([IsAuthenticated])
def get_analytics(request):
    start_date, end_date = get_dates_from_request(request)
    if not start_date:
        return Response(
            {"Error": "Either (i) year or (ii) startdate & enddate parameters must be provided."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        analytics = request.user.analytics.get(start_date=start_date, end_date=end_date)
        return Response(analytics.data)
    except:
        return Response(
            {"Error": "The parameters you provided are invalid"},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view()
@permission_classes([IsAuthenticated])
def get_avail_periods(request):

    analytics_periods = [analytics.start_date.year for analytics in request.user.analytics.all()]
    simulation_periods = []

    return Response({
        "analytics": analytics_periods,
        "simulations": simulation_periods
    })
