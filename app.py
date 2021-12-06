from numpy import float32
import plotly.graph_objs as go
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import chart_studio.plotly as py
import os
import pandas as pd

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
MAPBOX_KEY = "pk.eyJ1Ijoid29sZnJhZ2U4OSIsImEiOiJja3Z4anRldTkwa3lwMm5wNGcwM2J0NnN4In0.jVBdev5Nty-sfsdpHyRZ6w"
server = app.server

# plotting data
hdb_coordinates_data = pd.read_csv(os.path.join("data","block_information_w_coordinates.csv"), index_col=0).reset_index(drop=True)
lat = hdb_coordinates_data['latitude']
lon = hdb_coordinates_data['longitude']
hover_text = "BLOCK: "+ hdb_coordinates_data['blk_no']+ " STREET: " +hdb_coordinates_data['street']

# recent sale information
recent_sale_df = pd.read_csv(os.path.join("data","recent_sale_df.csv"),index_col=0)

#predicted sale information
predicted_resale_df = pd.read_csv(os.path.join("data","predicted_resale_price.csv"))


#dashtable formatting
money = dash.dash_table.FormatTemplate.money(2)


data = go.Scattermapbox(
    lat=lat,
    lon=lon,
    mode='markers',
    marker=dict(
        size=14,
        color='red',
        opacity=0.5
    ),
    text=hover_text,
    hoverinfo='text',
    unselected = {
        "marker":{"opacity":0.4, "size":12}
    },
    selected = {
        "marker":{"opacity":0.4, "size":14, "color":"blue"}
    }
    )

layout = go.Layout(
    autosize=False,
    mapbox=dict(
        accesstoken=MAPBOX_KEY,
        bearing=0,
        pitch=45,
        zoom=15.8,
        center=dict(lat=1.336, lon=103.699),
        style="mapbox://styles/wolfrage89/ckwddcs3t1wc414mocxijeo6a"),
    width=1200,
    height=600,
    clickmode='event+select'
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
    ),
    dbc.Row(
        [
            html.H1("Predicted Sales in year 2022", id='predicted_resale_header'),
            html.Div(id="predicted_resale_table")
        ]
    ),
    dbc.Row(
        [   
            html.H1("Recent Sales", id='recent_sale_header'),
            html.Div(id='recent_sale_table')
        ]
    )
])

@app.callback([Output('recent_sale_table', 'children'), 
               Output("recent_sale_header", "children"),
               Output("predicted_resale_table", "children"),
               Output("predicted_resale_header", "children")
               ],
              [Input("map_3d", 'clickData')])
def map_click(clickData):
    if clickData is None:
        raise dash.exceptions.PreventUpdate
    else:
        index = clickData['points'][0]['pointIndex']
        address = hdb_coordinates_data.iloc[index]['address']
        table_df = recent_sale_df[recent_sale_df['address']==address].drop("address",axis=1)
        table_df['resale_price'] = table_df['resale_price'].astype(float32)
        columns = []
        for column in table_df.columns:
            if column == "resale_price":
                columns.append({"name":column, "id":column, "type":"numeric", "format":money})
            else:
                columns.append({"name":column, "id":column})

        recent_sale_table = dash_table.DataTable(data=table_df.to_dict('records'),
                                     columns= columns,
                                     style_cell={'textAlign': 'center'},
                                     style_header={
                                                    'backgroundColor': '#d7d8cc',
                                                    'fontWeight': 'bold'
                                                   },
                                     style_data_conditional=[
                                                    {
                                                        'if': {'row_index': 'odd'},
                                                        'backgroundColor': 'rgb(220, 220, 220)',
                                                    }
                                                ],)

        new_title = f"Recent Sale for {address}"

        #predicted sale
        predicted_resale_table_df = predicted_resale_df[predicted_resale_df['address']==address].copy()
        
        predicted_resale_table_df['predicted_resale_price'] = predicted_resale_table_df['predicted_resale_price'].astype(float32)
        remaining_lease_months = predicted_resale_table_df['remaining_lease_months']
        predicted_resale_table_df['approximate_remaining_lease'] = (remaining_lease_months//12).astype(str) +" years " + (remaining_lease_months%12).astype(str)+ " months"
        predicted_resale_table_df = predicted_resale_table_df[['storey_range','flat_type','flat_model','floor_area_sqm','predicted_resale_price','approximate_remaining_lease']]
        predicted_resale_table_df.columns = ['storey_range','flat_type','flat_model','avg_floor_area_sqm','predicted_resale_price','approximate_remaining_lease']

        columns = []
        for column in predicted_resale_table_df.columns:
            if column == "predicted_resale_price":
                columns.append({'id':column, "name":column, "type":"numeric", "format":money})
            else:
                columns.append({'id':column, "name":column})
        predicted_resale_table = dash_table.DataTable(data=predicted_resale_table_df.to_dict('records'),
                                                      columns=columns,
                                                      style_cell={'textAlign':'center'},
                                                      style_header={
                                                                    'backgroundColor': '#d7d8cc',
                                                                    'fontWeight': 'bold'
                                                                   },
                                                      style_data_conditional=[
                                                                    {
                                                                        'if': {'row_index': 'odd'},
                                                                        'backgroundColor': 'rgb(220, 220, 220)',
                                                                    }
                                                ])
        new_resale_title = f"Predicted Sales for {address} in year 2022"

        return recent_sale_table, new_title, predicted_resale_table, new_resale_title

if __name__ == "__main__":
    app.run_server()
