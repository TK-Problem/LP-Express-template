from dash import html, dcc
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
                    html.A('Select Files')
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
            html.P(id='output-data-upload'),
        ]
    ),
    className="mt-3",
)

tab2_content = dbc.Card(
    dbc.CardBody(
        [
            html.H4("Antraštė (modifikuoti duomenys)", className="card-title"),
            html.P("Laikinas tekstas (PLACEHOLDER)", className="card-text")
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
        dbc.Button("Prisijungti", id="login-btn", n_clicks=0,
                   disabled=False, color="primary", className="me-1"),
        dbc.Button("Demo siuntinys", id="upload-btn", color="primary", disabled=True, className="me-1"),
    ]
)

email_input = dbc.Card(
    dbc.CardBody(
        [
            html.H4("LP-Express prisijungimas", className="card-title"),
            dbc.FormFloating(
                [
                    dbc.Input(type="text", id='input-usr', placeholder="email"),
                    dbc.Label("El. paštas"),
                ]
            ),
            dbc.FormFloating(
                [
                    dbc.Input(type="text", id='input-psw', placeholder="password"),
                    dbc.Label("Slaptažodis"),
                ]
            ),
            dbc.FormText(children="Įvedus duomenis paspauskite TAB klavišą.", id='form-msg'),
            buttons,
        ],
    ),
    className="mt-3"
)
