import pandas as pd
from datetime import datetime, timezone, timedelta
from celery import shared_task
from django.contrib.auth.models import User

from core.analytics_utils import get_analytics, get_item_props
from core.square_api_utils import get_locations, get_orders, parse_orders

@shared_task
def sample_task():
    print("My task has run")
    return None

@shared_task
def update_user_info(
    user_pks: list = None,
    pull_data: bool = True,
    update_analytics: bool = True,
    years_to_update: list = None
):
    '''
    1. Data Extraction
       - Pull new transactions data from Square API
       - Update raw_data and parsed_data
    2. Run Analytics
       - Update user's analytics based on parsed_data
    '''
    if user_pks == None:
        users = User.objects.all()
    else:
        users = User.objects.filter(pk__in=user_pks)

    for user in users:
        orders_df = user.data.read_parsed_data()
        orders_df['timestamp'] = pd.to_datetime(orders_df.timestamp, utc=True)
        items_df = user.data.read_parsed_data(field="menu_data")
        raw_orders = user.data.read_raw_data()

        YEARS_TO_UPDATE = orders_df.timestamp.dt.year.unique()

        if user.data.source == 'Square' and pull_data == True:
            ## Run function to extract Square data
            print('extracting square data...')

            ACCESS_TOKEN = user.data.access_key
            locations = get_locations(ACCESS_TOKEN)
            loc_ids = [locs['id'] for locs in locations['locations']]
            start_time = (datetime.now(timezone.utc).astimezone() - timedelta(1.5)).isoformat()
            end_time = datetime.now(timezone.utc).astimezone().isoformat()
            orders = get_orders(start_time, end_time, loc_ids, ACCESS_TOKEN)
            new_orders_df = parse_orders(orders)

            ## Create new raw_orders list and remove duplicates
            ## Note that set() does not work because the list contains dicts, which are unhashable
            raw_orders = raw_orders + orders['orders']
            raw_orders = [i for n, i in enumerate(raw_orders) if i not in raw_orders[n + 1:]]
            user.data.save_raw_data(raw_orders)

            ## Create new orders_df and drop duplicates
            orders_df = pd.concat([orders_df, new_orders_df]).drop_duplicates()
            user.data.save_parsed_data(orders_df)

            YEARS_TO_UPDATE = new_orders_df.timestamp.dt.year.unique()
            print('square data extracted')

        if update_analytics == True:
            orders_df['timestamp'] = pd.to_datetime(orders_df.timestamp, utc=True)

            if years_to_update != None:
                YEARS_TO_UPDATE = years_to_update
            for year in YEARS_TO_UPDATE:
                print('updating for {}'.format(year))
                period_df = orders_df[orders_df.timestamp.dt.year == year].copy()
                analytics = user.analytics.get(start_date=datetime(year,1,1))

                new_analytics_data = get_analytics(period_df)
                new_analytics_data['items'] = get_item_props(period_df, items_df)

                analytics.data = new_analytics_data
                analytics.save()

    return True
