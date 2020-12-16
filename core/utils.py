from datetime import datetime

def get_dates_from_request(request):
    year = request.query_params.get("year", None)
    start_date = request.query_params.get("startdate", None)
    end_date = request.query_params.get("enddate", None)

    if year:
        return datetime(int(year), 1, 1), datetime(int(year), 12, 31)
    elif start_date and end_date:
        return datetime.strptime(start_date, "%Y%m%d"), datetime.strptime(end_date, "%Y%m%d")
    else:
        return None, None
