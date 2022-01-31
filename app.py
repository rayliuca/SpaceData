import os
import dash
from dash import dcc
from dash import html
from dash import dash_table
from dash.dependencies import Input, Output

import plotly.express as px
import pandas as pd

# external CSS stylesheets
external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    {
        'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO',
        'crossorigin': 'anonymous'
    }
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
# data = pd.read_csv("https://github.com/rayliuca/SpaceData/raw/main/spacebot_public_marketplace.csv")
data = pd.read_csv("spacebot_public_marketplace.csv")
data["goods"] = data["location"] + "-" + data["symbol"]
data['timestamp'] = pd.to_datetime(data['timestamp'])
data['time'] = data['timestamp'].values.view('<i8') / 10 ** 9
data['time_diff'] = data.groupby(['location', 'symbol'])['time'].diff()
data['q_diff'] = data['quantityavailable'].diff()
data['price_diff'] = data['priceperunit'].diff()
data.dropna(inplace=True)

loc_df = data[['location']].drop_duplicates()

loc_filter_table = dash_table.DataTable(
    id='location_filter',
    columns=[
        {"name": i, "id": i, "deletable": False, "selectable": True} for i in loc_df.columns
    ],
    data=loc_df.to_dict('records'),
    editable=True,
    filter_action="native",
    sort_action="native",
    sort_mode="multi",
    column_selectable="single",
    row_selectable="multi",
    row_deletable=False,
    selected_columns=[],
    selected_rows=[0],
    page_action="native",
    page_current=0,
    page_size=10,
)

symbol_df = data[['symbol']].drop_duplicates()

symbol_filter_table = dash_table.DataTable(
    id='symbol_filter',
    columns=[
        {"name": i, "id": i, "deletable": False, "selectable": True} for i in symbol_df.columns
    ],
    data=symbol_df.to_dict('records'),
    editable=True,
    filter_action="native",
    sort_action="native",
    sort_mode="multi",
    column_selectable="single",
    row_selectable="multi",
    row_deletable=False,
    selected_columns=[],
    selected_rows=[0],
    page_action="native",
    page_current=0,
    page_size=10,
)

fig_data = data[(data['location'] == loc_df.iloc[0, 0]) & (data['symbol'] == symbol_df.iloc[0, 0])]


def gen_q_v_p_fig(data):
    fig = px.scatter(data, x="quantityavailable", y="priceperunit", color="goods", trendline="ols")
    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0
    ))
    return fig


def gen_q_vs_q_diff_fig(data):
    fig = px.scatter(data, x="quantityavailable", y="q_diff",
                     color="goods",
                     trendline="ols"
                     )

    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0
    ))
    return fig


def gen_q_diff_dist_fig(data):
    fig = px.histogram(data, y="q_diff", color="goods", marginal="box")

    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0
    ))
    return fig


def gen_q_v_spread_fig(data):
    fig = px.scatter(data, x="quantityavailable", y="spread", color="goods")
    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0
    ))
    return fig


app.layout = html.Div(children=[
    # All elements from the top of the page
    html.Div([
        html.H1(children='SpaceTrader Market Data Exploration'),
        html.Hr()
    ],
        style={
            'textAlign': 'center',
        },
    ),
    html.Div([
        html.Div([
            # First fig
            html.Div([
                html.H3(children='Quantity Available vs Price Per Unit'),

                html.Div(children='''
                    The price of the goods seems to depend on the quantity at a location
                '''),

                dcc.Graph(
                    id='q_vs_price_plot',
                    figure=gen_q_v_p_fig(fig_data)
                ),
            ]
            ),

            # second fig
            html.Div([
                html.H3(children='Quantity Available vs Change in Quantity'),

                html.Div(children='''
                        Here are the changes in quantity (q_diff) between market data thats within 10 seconds. 
                        Did not apply any filter
                    '''),

                dcc.Graph(
                    id='q_vs_q_diff_fig',
                    figure=gen_q_vs_q_diff_fig(fig_data)
                ),
            ]),

            # another fig
            html.Div([
                html.H3(children='Change in Quantity Distribution'),

                html.Div(children='''
                        Here are the changes in quantity (q_diff) between market data thats within 10 seconds. 
                        Did not apply any filter
                    '''),

                dcc.Graph(
                    id='q_diff_dist_fig',
                    figure=gen_q_diff_dist_fig(fig_data)
                ),
            ]),

            # # another fig
            # html.Div([
            #     html.H3(children='Price Spread vs Quantity Available'),
            #
            #     html.Div(children='''
            #             Is there any relation?
            #         '''),
            #
            #     dcc.Graph(
            #         id='q_v_spread_fig',
            #         figure=gen_q_v_spread_fig(fig_data)
            #     ),
            # ])
        ],
            className="eight columns",
            style={
                'margin-left': '4%',
                'font-size': '1.5em'
            }),

        html.Div([
            html.H3(children='Location Filter'),
            html.Div(children='''
                    Select Locations to include data
                '''),
            html.Div(
                [loc_filter_table],
                style={
                    'padding-top': '25px',
                    'padding-bottom': '25px'
                }),

            html.H3(children='Symbol Filter'),
            html.Div(children='''
                    Select Locations to include data
                '''),
            html.Div(
                [symbol_filter_table],
                style={
                    'padding-top': '25px',
                })

        ],
            className="three columns",
            style={
                'margin-left': '4%',
                'font-size': '1.5em'
            }, )
    ])
])


@app.callback(
    Output('q_vs_price_plot', "figure"),
    Output('q_vs_q_diff_fig', "figure"),
    Output('q_diff_dist_fig', "figure"),
    # Output('q_v_spread_fig', "figure"),
    Input('location_filter', "derived_virtual_selected_rows"),
    Input('symbol_filter', "derived_virtual_selected_rows"))
def update_plots_by_filter(selected_location_rows, selected_symbol_rows):
    # When the table is first rendered, `derived_virtual_data` and
    # `derived_virtual_selected_rows` will be `None`. This is due to an
    # idiosyncrasy in Dash (unsupplied properties are always None and Dash
    # calls the dependent callbacks when the component is first rendered).
    # So, if `rows` is `None`, then the component was just rendered
    # and its value will be the same as the component's dataframe.
    # Instead of setting `None` in here, you could also set
    # `derived_virtual_data=df.to_rows('dict')` when you initialize
    # the component.
    if selected_location_rows is None:

        loc_filter_list = ['OE-PM-TR']
    else:
        loc_filter_list = list(loc_df.iloc[selected_location_rows].values.flatten())

    if selected_symbol_rows is None:
        symbol_filter_list = ['FUEL']
    else:
        symbol_filter_list = list(symbol_df.iloc[selected_symbol_rows].values.flatten())

    fig_data = data[data['location'].isin(loc_filter_list)]
    fig_data = fig_data[fig_data['symbol'].isin(symbol_filter_list)]

    return gen_q_v_p_fig(fig_data), \
        gen_q_vs_q_diff_fig(fig_data), \
        gen_q_diff_dist_fig(fig_data), \
        # gen_q_v_spread_fig(fig_data)


if __name__ == '__main__':
    from waitress import serve
    # app.run_server(debug=False, host='0.0.0.0', port=8080, threaded=True)
    serve(app.server, host="0.0.0.0", port=8080)

