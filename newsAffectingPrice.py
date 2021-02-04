import pandas as pd

def trackChanges(linked_df, stock_df):
    '''
    Run this function after running linkNews to get percent change in price from news events
    '''
    # Get list of timestamps of all prices
    marketTimes = list(stock_df['datetime'])

    # Map timestamps to dict
    price_dict = dict(zip(stock_df.datetime, stock_df.Open))

    # Lookup marketTime index
    linked_df['currentIndex'] = linked_df['marketTime'].apply(lambda x: marketTimes.index(x))

    linked_df['nextOpen'] = linked_df['currentIndex'].apply(
        lambda x: price_dict[marketTimes[x + 1]] if x != len(marketTimes) - 1 else price_dict[marketTimes[x]])

    linked_df['pricePctChange'] = (linked_df['nextOpen'] - linked_df['Open']) / linked_df['Open']

    days_changes = pd.merge(stock_df, linked_df[['Title', 'URL', 'pricePctChange', 'marketTime', 'Origin']], left_on="datetime",
                            right_on="marketTime", how="left")

    days_changes = days_changes[['datetime', 'Title', 'URL', 'pricePctChange', 'Origin' ,'Open']]
    return days_changes
