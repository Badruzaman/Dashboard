
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
from datetime import date


from app import app
from config import conn_tissue
from configuration.dropdown_mgt import show_divisions

today = date.today()
bl = 3

#
# sql = f'select * from DBWareHouse'
# df = pd.read_sql(sql, conn_tissue)

division_values = show_divisions()
for item in division_values[0].items():
    default_value = item[1]


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
                                options=division_values,
                                clearable=False,
                                value=default_value,
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
            html.Div([dash_table.DataTable(id='datatable',
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
                html.H4('Top 10 Party By Order Quantity', className='card-header bg-info'),
                dcc.Graph(id='bargraph_party', figure={})
            ], style={'text-align': 'center'})
        ], md=6),
        dbc.Col([
            html.Div([
                html.H4('Top 10 Executive By Order Quantity', className='card-header bg-info'),
                dcc.Graph(id='bargraph_executive', figure={})
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
            dash_table.DataTable(id='datatableParty',
                                 data=[],
                                 fixed_rows={'headers': True},
                                 style_table={'height': 400}
                                )
        ], md=6),
      dbc.Col([
            html.Div([
                html.H4('Details Table Executive', className='card-header bg-info'),
            ], style={'text-align': 'center'}),
            dash_table.DataTable(id='datatableExecutive',
                                 data=[],
                                 fixed_rows={'headers': True},
                                 style_table={'height': 400}
                                )
        ], md=6)
    ])
])

@app.callback(
    Output('bargraph_party', 'figure'),
    Output('bargraph_executive', 'figure'),
    Output('datatable', 'columns'),
    Output('datatable', 'data'),
    Output('datatableParty', 'columns'),
    Output('datatableParty', 'data'),
    Output('datatableExecutive', 'columns'),
    Output('datatableExecutive', 'data'),
    Input('division_dropdown', 'value'),
    Input('start_date', 'date'),
    Input('end_date', 'date'),
)
def update_salesorderoverview_graph(division_dropdown_value, start_date, end_date):
    figure_party = {}
    figure_executive = {}
    summary_data = []
    start_date = "'{}'".format(start_date)
    end_date = "'{}'".format(end_date)
    sql = f'SprSecondarySalesInfoDashboard @BusinessLineId = {bl}, @MarketChannel_Id = {division_dropdown_value}, @FromDate = {start_date}, @ToDate = {end_date}'
    df2 = pd.read_sql_query(sql, conn_tissue)
    if not df2.empty:
        df3 = df2.groupby(["PartyName"], as_index=False)["TotalOrderQty"].sum().sort_values("TotalOrderQty", ascending=False).head(10)
        figure_party = px.bar(df3, x='PartyName', y='TotalOrderQty', color='PartyName', height=300)

        df4 = df2.groupby(["ExecutiveName"], as_index=False)["TotalOrderQty"].sum().sort_values("TotalOrderQty", ascending=False).head(10)
        figure_executive = px.bar(df4, x='ExecutiveName', y='TotalOrderQty', color='ExecutiveName', height=300)

        order_count = df2["Code"].nunique()
        total_sales_amount = df2["TotalOrderPrice"].sum()
        total_order_qty = df2["TotalOrderQty"].sum()
        total_remaining_qty = df2["RemainingQty"].sum()

        summary_data.append({"Total Order": order_count,
                             "Total Sales Amount": '{0:.2f}'.format(total_sales_amount),
                             "Total Order Qty": '{0:.2f}'.format(total_order_qty),
                             "Total Remaining Qty": '{0:.2f}'.format(total_remaining_qty)
                             })
        df_table = pd.DataFrame(list(summary_data))
        df3 = df2.groupby(['PartyName'], as_index=False).sum()[["TotalOrderQty", "TotalDeliveredQty", "RemainingQty"]] #["TotalOrderQty", "TotalDeliveredQty", "RemainingQty"].apply(lambda x: x.sum())
        df4 = df2.groupby(['ExecutiveName'], as_index=False).sum()[["TotalOrderQty", "TotalDeliveredQty", "RemainingQty"]]

    return figure_party, figure_executive,[{"name": i, "id": i} for i in df_table.columns], df_table.to_dict('records'),[{"name": i, "id": i} for i in df3.columns], df3.to_dict('records'), [{"name": i, "id": i} for i in df4.columns], df4.to_dict('records')