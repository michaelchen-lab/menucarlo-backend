import pandas as pd
from datetime import datetime
import re

def get_analytics(df: pd.DataFrame) -> dict:
    """
    Generate basic analytics based on DataFrame input.
    """

    df['timestamp'] = pd.to_datetime(df['timestamp'])

    ## Get total revenue and number of transactions ##
    order_df = df[['order_id','total_order_price']].drop_duplicates(subset=['order_id'])
    total_revenue = order_df.total_order_price.sum()
    no_of_transactions = len(order_df)

    ## Get item popularity ##
    popularity_df = df[['item_name', 'quantity']].groupby('item_name').sum().sort_values(by=['quantity'], ascending=False)
    most_popular_item = popularity_df.iloc[0].name
    least_popular_item = popularity_df.iloc[-1].name

    ## Get revenue over month and hour ##
    revenue_df = df[['timestamp','order_id','total_order_price']].drop_duplicates(subset=['order_id'])
    revenue_df.set_index('timestamp', inplace=True)

    revenue_by_month = revenue_df['total_order_price'].resample('M').sum().to_dict()
    revenue_by_month = {ts.strftime("%b"): revenue for ts, revenue in revenue_by_month.items()}

    revenue_df.index = [ts.replace(year=2000, month=1, day=1) for ts in revenue_df.index.tolist()]

    revenue_by_hour = revenue_df['total_order_price'].resample('H').sum().to_dict()
    revenue_by_hour = {ts.strftime("%H:%M"): revenue for ts, revenue in revenue_by_hour.items()}

    ## Output stats ##
    data = {
        "text": {
            "Total Revenue": "${:,.2f}".format(total_revenue),
            "No. of Transactions": "{:,.2f}".format(no_of_transactions),
            "Most Popular Item": most_popular_item,
            "Least Popular Item": least_popular_item
        },
        "graph": {
            "Revenue By Month": revenue_by_month,
            "Revenue By Hour": revenue_by_hour
        }
    }
    return data

def get_item_props(orders_df: pd.DataFrame, items_df: pd.DataFrame) -> list:
    '''
    Applies menu engineering matrix by segmenting items based on
    profitability and popularity.

    Input:
        - orders_df: Same format as parsed_data. Note that ALL data will be used
        - items_df: Same format as menu_data
    Output: DataFrame containing popularity and profit index for each item
    '''

    ## Proprocessing
    orders_df['item_name'] = orders_df.item_name.str.replace('[^A-Za-z\s]+', '')
    cols = ['quantity', 'item_price', 'total_item_price', 'total_order_price']
    orders_df[cols] = orders_df[cols].apply(pd.to_numeric)

    items_df['name'] = items_df.name.str.replace('[^A-Za-z\s]+', '')

    ## Get item's total quantity and profit per item
    item_props = []
    for item, category, cost in items_df[['name','category', 'cost']].values:
        item_df = orders_df[orders_df.item_name == item]
        if item_df.empty:
            continue

        item_props.append({
            "name": item,
            "category": category,
            "quantity": item_df.quantity.sum(),
            "revenue": (item_df.quantity * item_df.item_price).sum(),
            "profit": (item_df.quantity * item_df.item_price).sum() - item_df.quantity.sum() * cost,
            "profit_per_item": (item_df.quantity * item_df.item_price).sum() / item_df.quantity.sum() - cost,
            "cost_per_item": cost
        })

    df = pd.DataFrame(item_props)

    ## Normalize quantity and profit to produce 2 indexes
    df['popularity_index'] = (df.quantity-df.quantity.min())/(df.quantity.max()-df.quantity.min())
    df['profit_index'] = (df.profit_per_item-df.profit_per_item.min())/(df.profit_per_item.max()-df.profit_per_item.min())

    ## Remove items without indexes
    df = df.dropna(subset=[col for col in df.columns if col != 'category'])

    return df.to_dict(orient='records')

if __name__ == "__main__":
    df = pd.read_csv('tpoly_data.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df = df.loc[(df['timestamp'] >= datetime(2019,1,1)) & (df['timestamp'] <= datetime(2019,12,31))]

    data = get_analytics(df)
