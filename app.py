# packages for dash app
from dash import Dash, no_update, dash_table
from dash.dependencies import Input, Output, State
import pandas as pd
# packages for uploading data to dash app
import base64
import io
from layouts import *
# functions for webdriver (uploading data to LPE)
from webdriver import create_browser, login, upload_data
import asyncio

app = Dash(__name__,
           meta_tags=[{"name": "viewport", "content": "width=device-width"}],
           suppress_callback_exceptions=True)

server = app.server

# create asyncio loop for running pyppeteer browser
loop = asyncio.get_event_loop()
# create browser
browser, page = loop.run_until_complete(create_browser())
# create empty pandas DataFrame for storing Etsy sales orders
df_orders = pd.DataFrame()


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
    global df_orders
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df_orders = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            # Choose only specific columns
            df_orders = df_orders[['Item Name', 'Quantity', 'Price', 'Order Shipping', 'Date Shipped',
                                   'Ship Name', 'Ship Address1', 'Ship Address2', 'Ship City', 'Ship State',
                                   'Ship Zipcode', 'Ship Country', 'Variations']]
            # take only unsent data
            df_orders = df_orders.loc[df_orders['Date Shipped'].isna()].reset_index(drop=True)

    except Exception as e:
        print(e)
        return 'There was an error processing this file.'

    return f'{filename} successfully loaded.'


@app.callback([Output('output-data-upload', 'children'),
               Output('orders-table', 'children'),
               Output('tabs-collapse', 'is_open')],
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'))
def update_output(list_of_contents, list_of_names):
    global df_orders
    if list_of_contents is not None:
        msg = [parse_contents(c, n) for c, n in zip(list_of_contents, list_of_names)]
        # generate Dash table
        dtable = dash_table.DataTable(data=df_orders.to_dict('records'), page_size=50,
                                      style_table={'overflowX': 'auto'},
                                      columns=[{'name': i, 'id': i} for i in df_orders.columns])

        return msg, dtable, True
    return no_update


@app.callback(
    [Output('load-message', 'children'),
     Output('login-btn', 'children'),
     Output('login-btn', 'color'),
     Output('login-btn', 'disabled'),
     Output('upload-btn', 'children'),
     Output('upload-btn', 'disabled')],
    [Input('input-usr', 'value'),
     Input('input-psw', 'value'),
     Input('login-btn', 'n_clicks'),
     Input('upload-btn', 'disabled'),
     Input('upload-btn', 'n_clicks')],
)
def buttons_callback(usr, psw, n_login, cond, n_upload):
    global loop, page, browser
    if usr is None or psw is None:
        return no_update

    # login to LP-Express
    if n_login and cond:
        page, x = loop.run_until_complete(login(page, usr, psw))
        # check if login was successful
        if 'Pridėti siuntą' in x:
            return 'Sėkmingai prisijungta prie svetainės.', 'Prisijungta', "success", True, no_update, False
        else:
            msg = 'Nepavyko, perkraukite svetainę.\n' + x
            return msg, 'Nepavyko', "danger", True, no_update, True

    # upload data to LP-Express
    if n_upload:
        loop.run_until_complete(upload_data(page))
        # loop.run_until_complete(close_browser(browser))
        return 'Duomenys sėkmingai įkelti.', no_update, no_update, no_update, "Įkelta", True

    return no_update


# run app
if __name__ == '__main__':
    app.run_server(debug=True)
