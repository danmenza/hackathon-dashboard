import pandas as pd

def nearest(items, myDate):
    return min(items, key=lambda x: abs(x - myDate))


def linkNews(news_df, price_df):
    '''
    Link Dataframe containing news to dataframe containing stock prices at closest point in time in market data
    Keys = marketTime in newsDF and datetime in stock price DF (both datetime type)
    '''
    news_df['marketTime'] = news_df['localTime'].apply(lambda x: nearest(price_df['datetime'], x))

    linked_df = pd.merge(news_df, price_df[['Open', 'datetime']], left_on='marketTime', right_on='datetime').drop(
        'datetime', axis=1)
    return linked_df