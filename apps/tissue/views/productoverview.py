
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from datetime import date
# import dash_table
from dash import Dash, callback, html, dcc, dash_table, Input, Output, State, MATCH, ALL

from app import app
from config import conn_tissue
from dropdown_mgt import show_divisions, division_wise_areas, area_wise_territory, area_wise_parties

today = date.today()
bl = 3

sql = f'SprSecondarySalesInfoDashboard @BusinessLineId = {bl}'
df = pd.read_sql(sql, conn_tissue)

layout = html.Div([
    # html.Br(),
    dbc.Row([
        # dbc.Col([
        # ], md=1),
        dbc.Col([
            html.Div([
                html.H4('Sales Order Summary', className='card-header bg-success'),
                html.Div([
                    dbc.Row([
                        dbc.Col([], md=3),
                        dbc.Col([
                            dbc.Label('Division: '),
                            dcc.Dropdown(
                                id='division_dropdown',
                                style={
                                    'width': '90%'
                                },
                                options=show_divisions(),
                                clearable=False,
                                placeholder="ALL"
                            )], md=2),

                        dbc.Col([
                            dbc.Label('Start Date: '),
                            html.Div(style={'fontSize': 10},
                                     children=dcc.DatePickerSingle(
                                         id='start_date',
                                         date=date(2016, 1, 1)
                                     ),
                                     )
                        ], md=2),
                        dbc.Col([
                            dbc.Label('End Date: '),
                            html.Div(style={'fontSize': 10},
                                     children=dcc.DatePickerSingle(
                                         id='end_date',
                                         date=today
                                     ),
                                     )
                        ], md=2),
                        dbc.Col([

                        ], md=1),
                    ]),
                ], className='card-body')
            ], className='card bg-light mb-3', style={'text-align': 'center'})
        ], md=12),
        # dbc.Col([
        # ], md=1),
    ]),

    dbc.Row([
        dbc.Col([
            html.Div([
                html.H4('Overall Sales Order', className='card-header bg-info'),
            ], style={'text-align': 'center'}),
            html.Div([dash_table.DataTable(id='datatablesummary',
                                           # columns=[ {"name": i, "id": i} for i in sorted(df8.columns)],
                                           data=[],
                                           )], style={'font-weight': 'bold'})
        ])
    ]),

    dbc.Row([
        # dbc.Col([
        # ], md=1),
        dbc.Col([
            html.Div([
                html.H4('Category Wise Top 10 Sales product', className='card-header bg-info'),
                dcc.Graph(id='bargraph_category', figure={})
            ], style={'text-align': 'center'})
        ], md=6),
        dbc.Col([
            html.Div([
                html.H4('Proudct Wise Top 10 Sales', className='card-header bg-info'),
                dcc.Graph(id='bargraph_product', figure={})
            ], style={'text-align': 'center'})
        ], md=6),
        # dbc.Col([
        # ], md=1),
    ]),
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H4('Details Table Party', className='card-header bg-info'),
            ], style={'text-align': 'center'}),
            dash_table.DataTable(id='datatableCategory',
                                 data=[],
                                 fixed_rows={'headers': True},
                                 style_table={'height': 400}
                                 )
        ], md=6),
        dbc.Col([
            html.Div([
                html.H4('Details Table Executive', className='card-header bg-info'),
            ], style={'text-align': 'center'}),
            dash_table.DataTable(id='datatableProduct',
                                 data=[],
                                 fixed_rows={'headers': True},
                                 style_table={'height': 400}
                                 )
        ], md=6)
    ])
])


@app.callback(
    Output('datatablesummary', 'columns'),
    Output('datatablesummary', 'data'),
    Output('datatableCategory', 'columns'),
    Output('datatableCategory', 'data'),
    Output('datatableProduct', 'columns'),
    Output('datatableProduct', 'data'),
    Input('division_dropdown', 'value'),
    Input('start_date', 'date'),
    Input('end_date', 'date'),
)
def update_summary_data(division_dropdown_value, start_date, end_date):
    summary_data = []
    df_table = pd.DataFrame()
    df1 = df.loc[(df['OrderDate'] >= start_date) & (df['OrderDate'] <= end_date)]
    if division_dropdown_value:
        df2 = df1.loc[df['MarketChannel_Id'] == division_dropdown_value]
    else:
        df2 = df1

    if not df2.empty:
        order_count = df2["Code"].nunique()
        total_sales_amount = df2["TotalOrderPrice"].sum()
        total_order_qty = df2["TotalOrderQty"].sum()
        total_remaining_qty = df2["RemainingQty"].sum()

        summary_data.append({"Total Order": order_count,
                             "Total Sales Amount": '{0:.2f}'.format(total_sales_amount),
                             "Total Order Qty": '{0:.2f}'.format(total_order_qty),
                             "Total Remaining Qty": '{0:.2f}'.format(total_remaining_qty)
                             })
        df_table = pd.DataFrame(summary_data)
        df3 = df2.groupby(['ProductCategoryName'], as_index=False)["TotalOrderQty", "TotalDeliveredQty", "RemainingQty"].apply( lambda x: x.sum())
        df4 = df2.groupby(['ProductName'], as_index=False)["TotalOrderQty", "TotalDeliveredQty", "RemainingQty"].apply(lambda x: x.sum())

    return [{"name": i, "id": i} for i in df_table.columns], df_table.to_dict('records'), [{"name": i, "id": i} for i in df3.columns], df3.to_dict('records'), [{"name": i, "id": i} for i in df4.columns], df4.to_dict('records')


@app.callback(
    Output('bargraph_category', 'figure'),
    Output('bargraph_product', 'figure'),
    Input('division_dropdown', 'value'),
    Input('start_date', 'date'),
    Input('end_date', 'date'),
)
def update_salesorder_graph(division_dropdown_value, start_date, end_date):
    figure_category = {}
    figure_product = {}
    df1 = df.loc[(df['OrderDate'] >= start_date) & (df['OrderDate'] <= end_date)]
    if division_dropdown_value:
        df2 = df1.loc[df['MarketChannel_Id'] == division_dropdown_value]
    else:
        df2 = df1
    if not df2.empty:
        df3 = df2.groupby(["ProductCategoryName"], as_index=False)["TotalOrderPrice"].sum()
        figure_category = px.bar(df3, x='ProductCategoryName', y='TotalOrderPrice', color="ProductCategoryName", height=300)

        df4 = df2.groupby(["ProductName"], as_index=False)["TotalOrderPrice"].sum().sort_values("TotalOrderPrice", ascending=False).head(10)
        figure_product = px.bar(df4, x='ProductName', y='TotalOrderPrice', color="ProductName", height=300)

    return figure_category, figure_product