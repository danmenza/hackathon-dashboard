import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.plotly as py
import plotly.graph_objs as go
from plotly import tools
import colorlover as cl
import json

from parsePrices import DataFile
from getNews import getNews
from linkNews import linkNews
from newsAffectingPrice import trackChanges
from getStockQuote import getStockQuote

stocks = DataFile.collect()

app = dash.Dash()

ryb = cl.scales['4']['seq']['Purples']

app.layout = html.Div(children=[
    html.H1(children='Team Lion'),

    dcc.Dropdown(
        id='stock-selector',
        options=[{'label':v.fullname, 'value':k} for k, v in stocks.items()
        ],
        value=['SYF'],
        multi=True
    ),

    html.Div(id='graphs')

])

@app.callback(
    dash.dependencies.Output('graphs','children'),
    [dash.dependencies.Input('stock-selector', 'value')]
)
def update_graph(tickers):
    graphs = []

    for ticker in tickers:
        df = stocks[ticker].df
        quoteDate, quoteTime, quotePrice = getStockQuote(ticker, df)

        graphs.append(html.H2(ticker))
        graphs.append(html.H3('Last quote: ${} at {} {}'.format(quotePrice,quoteDate,quoteTime)))

        high_trace = go.Scatter(
            x= df['datetime'],
            y= df['High'],
            name='High'
        )


        low_trace = go.Scatter(
            x= df['datetime'],
            y= df['Low'],
            name='Low'
        )

        news_df = getNews(ticker)
        linked_df = linkNews(news_df, df)
        mod_df = trackChanges(linked_df, df)

        mod_df_sec = mod_df[mod_df['Origin'] == 'SEC']
        mod_df_news = mod_df[mod_df['Origin'] != 'SEC']
        mod_df_event = mod_df[~mod_df['Title'].isnull()]

        # news_trace = go.Scatter(
        #     x = linked_df['marketTime'],
        #     y = linked_df['Open'],
        #     mode = 'markers',
        #     marker = dict(size=15, symbol='triangle-up'),
        #     text = linked_df['Title'],
        #     name = 'News'
        # )

        event_trace = go.Scatter(
            x = mod_df_event['datetime'],
            y = mod_df_event['Open'],
            mode = 'markers',
            marker = dict(size=10, color=ryb[1]),
            text = mod_df_event['Title'],
            name = 'Event'
        )


        news_trace = go.Bar(
            x = mod_df_news['datetime'],
            y = mod_df_news['pricePctChange'],
            text = mod_df_news['Title'],
            name = 'News',
            marker = dict(color = ryb[2])
        )

        sec_trace = go.Bar(
            x = mod_df_sec['datetime'],
            y = mod_df_sec['pricePctChange'],
            text = mod_df_sec['Title'],
            name = 'SEC',
            marker = dict(color = ryb[3])
        )

        fig = tools.make_subplots(rows=2, cols=1, shared_xaxes=True)
        fig.append_trace(high_trace, 1, 1)
        fig.append_trace(low_trace, 1, 1)
        fig.append_trace(event_trace, 1, 1)
        fig.append_trace(news_trace, 2, 1)
        fig.append_trace(sec_trace, 2, 1)
        fig.layout.xaxis1.type = 'category'
        fig.layout.title = stocks[ticker].fullname

        graphs.append(dcc.Graph(
            id=ticker,
            figure=fig
        ))

    return graphs


if __name__ == '__main__':
    app.run_server(debug=True)
