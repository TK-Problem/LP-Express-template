from dash import html
import dash_bootstrap_components as dbc


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