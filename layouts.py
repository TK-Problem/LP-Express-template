from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc


"""
FOOTER and HEADER
"""

header = html.Header(
    dbc.Row(
        [
            dbc.Col(
                [
                    html.Img(id="logo-image", src='assets/app-logo.svg', height='100px'),
                ],
                width={"size": 3},
            ),
        ],
    ),
    className='card text-white bg-dark mb-3'
)

footer = html.Footer(
    dbc.Row(
        dbc.Col(
            [
                html.Br(),
                html.Div("Setainės šablonas", style={'textAlign': 'center'}),
                html.Br(),
            ],
            width={"size": 6, "offset": 3},

        ),
    ),
    className='card text-white bg-dark mb-3'
)

"""
SECTION 1

DATA UPLOAD- upload .csv file to dash app
"""

data_input = dbc.Card(
    dbc.CardBody(
        [
            html.H4("Duomenų įkėlimas", className="card-title"),
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files',
                           title='Paspaudus leis įkelti failą iš kompiuterio',
                           style={"color": "#4582ec"})
                ]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px'
                },
                # Allow multiple files to be uploaded
                multiple=True
            ),
        ],
    ),
    className="mt-3"
)


"""
SECTION 2

TABS- data manupulation
"""

tab1_content = dbc.Card(
    dbc.CardBody(
        [
            html.Div(id='orders-table'),
            html.Hr(),
            html.P(id='output-data-upload', className="card-text"),
            html.Br(),
            dbc.Button("Skaičiuoti užsakymus", id="calculate-btn", n_clicks=0, color="primary", className="me-1"),
        ]
    ),
    className="mt-3",
)

tab2_content = dbc.Card(
    dbc.CardBody(
        [
            html.Div(
                [
                    dash_table.DataTable(data=[], page_size=30,
                                         style_cell_conditional=[
                                             {
                                                 'if': {'column_id': c},
                                                 'textAlign': 'left'
                                                 } for c in ['Date', 'Region']
                                             ],
                                         style_data={
                                             'color': 'black',
                                             'backgroundColor': 'white'
                                             },
                                         style_data_conditional=[
                                             {
                                                 'if': {'row_index': 'odd'},
                                                 'backgroundColor': 'rgb(220, 220, 220)',
                                                },
                                             {
                                                 'if': {'filter_query': '{Siuntinio vertė} > 50',
                                                        'column_id': 'Siuntinio vertė'},
                                                 'backgroundColor': 'tomato',
                                                 'color': 'white'
                                                 },
                                             {
                                                 'if': {'filter_query': '{Prioritetas} = 1',
                                                        'column_id': 'Prioritetas'},
                                                 'backgroundColor': 'dodgerblue',
                                                 'color': 'white'
                                                },
                                             ],
                                         style_header={
                                             'backgroundColor': 'rgb(210, 210, 210)',
                                             'color': 'black',
                                             'fontWeight': 'bold'
                                             },
                                         style_table={'overflowX': 'auto'},
                                         editable=True,
                                         row_deletable=True,
                                         columns=[],
                                         id='parcels-table')
                    ]),
            html.Hr(),
            html.Br(),
            dbc.Button("Atsisiųsti .csv", id="download-btn", n_clicks=0, color="primary", className="me-1"),
            dcc.Download(id="download-dataframe-csv"),
        ]
    ),
    className="mt-3",
)

tabs_layout = dbc.Collapse(
    html.Div(
        [
            dcc.Tabs(id="tabs",
                     value='tab-1',
                     children=[dcc.Tab(label='Etsy užsakymai',
                                       children=[tab1_content],
                                       value='tab-1'),
                               dcc.Tab(label='LP siuntiniai',
                                       children=[tab2_content],
                                       value='tab-2'),
                               ]
                     ),
            html.Br(),
        ]
    ), id="tabs-collapse", is_open=False)

"""
SECTION 3

UPLOAD DATA- imports data to LPE
"""

buttons = html.Div(
    [
        dbc.Button("Prisijungti", id="login-btn", n_clicks=0, disabled=False, color="primary", className="me-1"),
        dbc.Button("Demo siuntinys", id="demo-btn", color="primary", disabled=True, className="me-1"),
        dbc.Button("Siųsti siuntinius", id="upload-all-btn", color="primary", disabled=True, className="me-1"),
    ]
)

email_input = dbc.Card(
    dbc.CardBody(
        [
            html.H4("LP-Express prisijungimas", className="card-title"),
            dbc.FormFloating(
                [
                    dbc.Input(type="email", id='input-usr', placeholder="email"),
                    dbc.Label("El. paštas"),
                ]
            ),
            dbc.FormFloating(
                [
                    dbc.Input(type="password", id='input-psw', placeholder="password"),
                    dbc.Label("Slaptažodis"),
                ]
            ),
            dbc.FormText(children="Įvedus duomenis paspauskite TAB klavišą.", id='form-msg'),
            buttons,
            html.Br(),
            dcc.Interval(id='interval-progress', interval=10 * 1000, n_intervals=0),
            dbc.Progress(id="progress-bar", style={"height": "25px"}),
        ],
    ),
    className="mt-3"
)
