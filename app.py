import plotly.graph_objs as go
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State
import chart_studio.plotly as py

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

data = go.Scattermapbox(
    lat=["1.336"],
    lon=["103.699"],
    mode='markers',
    marker=dict(
        size=4,
        color='red',
        opacity=0.8
    )
)
layout = go.Layout(
    autosize=False,
    mapbox=dict(
        accesstoken="pk.eyJ1Ijoid29sZnJhZ2U4OSIsImEiOiJja3Z4anRldTkwa3lwMm5wNGcwM2J0NnN4In0.jVBdev5Nty-sfsdpHyRZ6w",
        bearing=10,
        pitch=60,
        zoom=16,
        center=dict(lat=1.336, lon=103.699),
        style="mapbox://styles/wolfrage89/ckwddcs3t1wc414mocxijeo6a"),
    width=1200,
    height=800
)

main_figure = go.Figure(data=data, layout=layout)

app.layout = dbc.Container([
    dbc.Row(
        [
            dbc.Col([
                html.H1("HDB resale price prediction",
                        className="text-center"),
                dcc.Graph(id='map_3d', figure=main_figure)
            ])
        ]
    )
])

if __name__ == "__main__":
    app.run_server(debug=True)
