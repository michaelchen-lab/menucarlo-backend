import json
import requests
from datetime import datetime, timezone, timedelta
from dateutil import parser, tz
import pandas as pd

# import logging
# logging.basicConfig(level=logging.DEBUG)

def get_locations(token: str) -> dict:
    URL = "https://connect.squareup.com/v2/locations"
    headers = {
        "Square-Version": "2020-11-18",
        "Authorization": "Bearer {}".format(token),
        "Content-Type": "application/json"
    }
    res = requests.get(URL, headers=headers)

    return json.loads(res.text)

def get_orders(start_time: str, end_time: str,
               location_ids: list, token: str) -> dict:
    URL = "https://connect.squareup.com/v2/orders/search"
    headers = {
        "Square-Version": "2020-11-18",
        "Authorization": "Bearer {}".format(token),
        "Content-Type": "application/json"
    }
    data = {
        'query': {
            'filter': {
                'date_time_filter': {
                    'created_at': {
                        'end_at': end_time,
                        'start_at': start_time
                    }
                }
            }
        },
        'location_ids': location_ids,
        'return_entries': False,
        'limit': 100000
    }
    res = requests.post(URL, headers=headers, data=json.dumps(data))
    return json.loads(res.text)

def parse_orders(raw_orders: dict) -> pd.DataFrame:
    items_df = pd.DataFrame(columns=[
        'timestamp', 'order_id', 'total_order_price',
        'item_name', 'quantity',
        'item_price', 'total_item_price',
    ])
    for order in raw_orders['orders']:

        # timestamp = parser.parse(order['created_at']).astimezone(tz.gettz('Singapore'))
        timestamp = parser.parse(order['created_at'])
        order_id = order['id']
        total_order_price = order['total_money']['amount']

        if 'line_items' not in order:
            # logging.info('order error: {}', order)
            continue

        for item in order['line_items']:

            if 'name' not in item:
                # logging.info('item error: {}'.format(item))
                continue

            items_df = items_df.append({
                'timestamp': timestamp,
                'order_id': order_id,
                'total_order_price': total_order_price,
                'item_name': item['name'],
                'quantity': item['quantity'],
                'item_price': item['base_price_money']['amount']    ,
                'total_item_price': item['total_money']['amount'],
            }, ignore_index=True)

    items_df[[
        'total_order_price', 'item_price', 'total_item_price'
    ]] = items_df[['total_order_price', 'item_price', 'total_item_price']] / 100

    items_df['timestamp'] = pd.to_datetime(items_df.timestamp)
    return items_df

def get_catalog(token: str) -> dict:
    URL = "https://connect.squareup.com/v2/catalog/list"
    headers = {
        "Authorization": "Bearer {}".format(token),
        "Content-Type": "application/json"
    }
    res = requests.get(URL, headers=headers)

    return json.loads(res.text)

def parse_catalog(data: dict) -> pd.DataFrame:
    data = data['objects']
    cats = {d['id']:d['category_data']['name']
            for d in data if d['type'] == 'CATEGORY'}
    cats[None] = None
    items = [{
        'name': d['item_data']['name'],
        'category': cats[d['item_data'].get('category_id', None)]
    } for d in data if d['type'] == 'ITEM']

    return pd.DataFrame(items)

if __name__ == "__main__":

    ACCESS_TOKEN = "EAAAEA_ciYL5cAwc_qL-tVv2e1lOJTS-MtLuTVg_dvWAo95owSf_01ALemh8IlP-"

    locations = get_locations(ACCESS_TOKEN)
    loc_ids = [locs['id'] for locs in locations['locations']]

    start_time = (datetime.now(timezone.utc).astimezone() - timedelta(1.5)).isoformat()
    end_time = datetime.now(timezone.utc).astimezone().isoformat()
    orders = get_orders(start_time, end_time, loc_ids, ACCESS_TOKEN)

    items_df = parse_orders(orders)

##    data = get_catalog(ACCESS_TOKEN)
##    df = parse_catalog(data)
