# packages for dash app
from dash import Dash, no_update
from dash.dependencies import Input, Output, State
# packages for uploading data to dash app
import base64
import io
from layouts import *
# functions for webdriver (uploading data to LPE)
from webdriver import create_browser, login_to_lpe, upload_parcel, upload_all_parcel
import asyncio
# packages and functions for data manipulation
import pandas as pd
from utils import calculate_order_props, find_parcels

app = Dash(__name__,
           meta_tags=[{"name": "viewport", "content": "width=device-width"}],
           suppress_callback_exceptions=True)

server = app.server

# create asyncio loop for running pyppeteer browser
LOOP = asyncio.get_event_loop()
# create browser
BROWSER, PAGE = LOOP.run_until_complete(create_browser())
# create empty pandas DataFrame for storing Etsy sales orders
DF_ORDERS = pd.DataFrame()
# create empty pandas DataFrame for storing LPE parcel information
DF_PARCELS = pd.DataFrame()

app.layout = html.Div(
    [
        header,
        dbc.Container(
            [
                html.Div(
                    [
                        data_input,
                        tabs_layout,
                        email_input,
                        html.Br(),
                        html.Div("Informacija vartotojui", id="load-message", style={'textAlign': 'center'}),
                        html.Br(),
                    ]
                )
            ]
        ),
        footer
    ]
)


def parse_contents(contents, filename):
    global DF_ORDERS
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            DF_ORDERS = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

            # count all rows
            before = len(DF_ORDERS)

            # take only unshiped orders
            DF_ORDERS = DF_ORDERS.loc[DF_ORDERS['Date Shipped'].isna()].reset_index(drop=True)

            # Choose only specific columns
            DF_ORDERS = DF_ORDERS[['Sale Date', 'Item Name', 'Variations', 'Quantity', 'Price', 'Order Shipping',
                                   'Ship Name', 'Ship Address1', 'Ship Address2', 'Ship City', 'Ship State',
                                   'Ship Zipcode', 'Ship Country']]

            # fill missing variations with string
            DF_ORDERS.Variations = DF_ORDERS.Variations.fillna('Nothing')

            # count not shipped orders
            after = len(DF_ORDERS)

            # generate message for app user
            msg = f"{filename} sėkmingai įkeltas. "
            msg += f"Rasta {before} užsakymai, iš kurių {after} dar neįvykdyti (neišsiųsti)."
        else:
            msg = f'{filename} failo tipas yra ne .csv.'

    except Exception as e:
        return f'There was an error processing this {filename} file. Error message: {e}'
    else:
        return msg


@app.callback([Output('output-data-upload', 'children'),
               Output('orders-table', 'children'),
               Output('tabs-collapse', 'is_open')],
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'))
def upload_csv(list_of_contents, list_of_names):
    global DF_ORDERS
    if list_of_contents is not None:
        msg = [parse_contents(c, n) for c, n in zip(list_of_contents, list_of_names)]

        # calculate properties only if file was correctly uploaded
        if msg[:5] != 'There':
            msg = [html.Div(msg)]
            # calculate table properties (order weights and volumes)
            DF_ORDERS = calculate_order_props(DF_ORDERS)
            # calculate how many orders have unknown weight
            msg.append(html.Div(f"{DF_ORDERS['Item Weight'].isna().sum()} užsakymai turi nežinomą svorį."))
            msg.append(html.Div(f"{DF_ORDERS['Item Volume'].isna().sum()} užsakymai turi nežinomą tūrį."))

        # generate Dash table
        dtable = dash_table.DataTable(data=DF_ORDERS.to_dict('records'), page_size=30,
                                      style_table={'overflowX': 'auto'},
                                      style_data_conditional=[
                                          {
                                              'if': {'filter_query': '{Item Volume} is blank',
                                                     'column_id': 'Item Name'},
                                              'backgroundColor': 'tomato',
                                              'color': 'white'
                                          },
                                          {
                                              'if': {'filter_query': '{Item Volume} is blank',
                                                     'column_id': 'Item Volume'},
                                              'backgroundColor': 'tomato',
                                              'color': 'white'
                                          },
                                          {
                                              'if': {'filter_query': '{Item Weight} is blank',
                                                     'column_id': 'Item Weight'},
                                              'backgroundColor': 'tomato',
                                              'color': 'white'
                                          },
                                      ],
                                      columns=[{'name': i, 'id': i} for i in DF_ORDERS.columns])

        return msg, dtable, True
    return no_update


@app.callback(
    [Output('parcels-table', 'data'),
     Output('parcels-table', 'columns')],
    Input('calculate-btn', 'n_clicks'),
)
def process_parcels(n_clicks):
    global DF_ORDERS, DF_PARCELS
    if n_clicks:
        DF_PARCELS = find_parcels(DF_ORDERS)

        # generate data for Dash table
        columns = [{'name': i, 'id': i} for i in DF_PARCELS.columns]
        table_data = DF_PARCELS.to_dict('records')

        return table_data, columns
    return no_update


@app.callback(
    [Output('load-message', 'children'),
     Output('login-btn', 'children'),
     Output('login-btn', 'color'),
     Output('login-btn', 'disabled'),
     Output('demo-btn', 'children'),
     Output('demo-btn', 'color'),
     Output('demo-btn', 'disabled'),
     Output('upload-all-btn', 'disabled')],
    [Input('login-btn', 'n_clicks'),
     Input('demo-btn', 'disabled'),
     Input('demo-btn', 'n_clicks'),
     Input('upload-all-btn', 'n_clicks')],
    [State('input-usr', 'value'),
     State('input-psw', 'value'),
     State('parcels-table', 'data')]
)
def btns_callback(n_login, cond, n_demo, n_upload, usr, psw, table_data):
    global LOOP, PAGE, BROWSER

    if usr is None or psw is None:
        return no_update

    # login to LP-Express
    if n_login and cond:
        PAGE, x = LOOP.run_until_complete(login_to_lpe(PAGE, usr, psw))
        # check if login was successful
        if 'Pridėti siuntą' in x:
            msg = 'Sėkmingai prisijungta prie svetainės.'
            return msg, 'Prisijungta', "success", True, no_update, no_update, False, False
        else:
            msg = 'Nepavyko, perkraukite svetainę.\n' + x
            return msg, 'Nepavyko', "danger", True, no_update, no_update, True, True

    # upload data to LP-Express
    if n_demo:
        PAGE, _ = LOOP.run_until_complete(upload_parcel(PAGE, 'demo'))
        return 'Demo siuntinys sėkmingai įkeltas.', no_update, no_update, no_update, "Įkelta", "success", True, no_update

    # upload all data to LP-Express
    if n_upload:
        # temp. DataFrame to read current data
        df_parcels = pd.DataFrame(table_data)

        if len(df_parcels):
            PAGE, _ = LOOP.run_until_complete(upload_all_parcel(PAGE, df_parcels))
            args = (no_update, no_update, no_update, no_update, no_update, no_update, no_update)
            return f'Sėkmingai įkelta {len(df_parcels)} užsakymų', *args
        return f'Nėra sugeneruotų užsakymų', no_update, no_update, no_update, no_update, no_update, no_update, no_update

    return no_update


# run app
if __name__ == '__main__':
    app.run_server(debug=True)
