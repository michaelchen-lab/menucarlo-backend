import pandas as pd
from datetime import datetime

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

if __name__ == "__main__":
    df = pd.read_csv('tpoly_data.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df = df.loc[(df['timestamp'] >= datetime(2019,1,1)) & (df['timestamp'] <= datetime(2019,12,31))]

    data = get_analytics(df)
