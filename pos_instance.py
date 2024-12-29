import dash
from dash import dcc 
from dash import html
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sqlite3
import locale
import numpy as np
import plotly.express as px
import random


# Set the locale for formatting
locale.setlocale(locale.LC_ALL, '')


pos_dash_layout = html.Div(className='containernew', children=[
    html.Div(className='pie-chart-container', style={'border': '1px solid black'}, children=[
        dcc.Graph(id='sunburst-chart', style={"height": "1100px", "width": "100%"}, className='pie-chart')
    ]),
    html.Div(className='bar-chart-container', style={'border': '1px solid black'}, children=[
        dcc.Graph(id='us-map-2', style={"height": "1100px", "width": "100%"}, className='us-map-2')
    ]),

    html.Div(className='footer-container', id='footer-container', style={'border': '1px solid black'}, children=[
                    html.A([
                    html.Img(
                        src='assets/black.jpg',
                        className='footer-image'
                        )
            ], href='http://127.0.0.1:5000/')
        ]),
        html.Div(className='footer-container2', id='footer-container2', style={'border': '1px solid black'}, children=[
                    html.A([
                    html.Img(
                        src='assets/black.jpg',
                        className='footer-image'
                        )
            ], href='http://127.0.0.1:5000/')
        ]),
])

def create_pos_dashapp(pos_app, var_data):
    # Here, you can use var_data to create your Dash application
    # For this example, let's assume var_data is a dictionary with a 'categorical_variable' key
    category = var_data['categorical_variable']

    @pos_app.callback(
        Output('sunburst-chart', 'figure'),
        Input('sunburst-chart', 'id')
    )
    def update_sunburst_chart(_):
        try:
            # Open a new database connection
            conn = sqlite3.connect(r"C:\Users\yashu\OneDrive\Desktop\Github_Projects\Credit_Card_Data_Visulization_Platform\Final_Databases\POS2.db")
            # SQL query to retrieve the number of transactions for each 'POS_entrymode' and 'MerchantGroup'
            query = 'SELECT POS_entrymode, MerchantGroup, Status, COUNT(*) as count FROM transactions GROUP BY POS_entrymode, MerchantGroup, Status'
            # Execute the query and fetch the results into a DataFrame
            df = pd.read_sql(query, conn)
            # Close the database connection
            conn.close()
            # Total transactions
            total_transactions = 535908
            # Calculate the percentage
            df['percentage'] = df['count'] / total_transactions * 100
            # Generate the sunburst chart using Plotly Express
            fig = px.sunburst(df, path=['POS_entrymode', 'MerchantGroup', 'Status'],
                            values='percentage',
                            title='POS Entry Modes with Merchant Groups and Transaction Status',
                            color='Status',
                            color_discrete_map={'(?)':'','Approved': 'limegreen', 'Declined': 'red'},
                            hover_data={'percentage': True, 'count':True},  # Specify hover data
                            )

            # Update hover template to show count and percentage
            fig.update_traces(hovertemplate='<b>%{label}</b><br>Percentage: %{customdata[0]:.2f}%<br>Count: %{customdata[1]}<br>')

            fig.update_layout(
                template='plotly_dark',
                title_x=0.5,
                title_y=0.95,
                title_font=dict(size=26),
            )
            return fig

        except Exception as e:
            print(f"Error: {e}")
            return []
       
    @pos_app.callback(
    Output('us-map-2', 'figure'),
    [Input('sunburst-chart', 'clickData')]
    )

    def generate_mapnew(sunburst_chart_clickData):
        # if the sunburst chart hasn't been clicked, return an empty figure
        if sunburst_chart_clickData is None:
            return {
            'data': [],
            'layout': {
                'template': 'plotly_dark',
                'paper_bgcolor': 'rgba(0, 0, 0, 0)',  # Set the paper background color to transparent
                'plot_bgcolor': 'rgba(0, 0, 0, 0)',  # Set the plot background color to transparent
                'xaxis': {'visible': False},  # Hide x-axis
                'yaxis': {'visible': False},  # Hide y-axis
            }
        }

        try:
            path = sunburst_chart_clickData['points'][0]['id']
            # split the path into its components
            path_components = path.split('/')
            path_length = len(path_components)

            # Open a new database connection
            conn = sqlite3.connect(r"C:\Users\yashu\OneDrive\Desktop\Github_Projects\Credit_Card_Data_Visulization_Platform\Final_Databases\Final_database.db")

            color_scale = None  # We will update this based on the selected POS_entrymode or Status

            if path_length == 1:  # POS_entrymode
                selected_entrymode = path_components[0]

                # Choose color scale based on the selected POS_entrymode
                if selected_entrymode.lower() == 'online':
                    color_scale = 'Bluered_r'
                elif selected_entrymode.lower() == 'insert':
                    color_scale = 'speed'
                elif selected_entrymode.lower() == 'tap':
                    color_scale = 'YlOrRd'
                elif selected_entrymode.lower() == 'swipe':
                    color_scale = 'Purpor'
                else:
                    color_scale = 'turbo'  # Default color scale

                # SQL query to retrieve transaction data by city for the selected POS_entrymode
                query = '''
                    SELECT Sum(TransactionAmount) AS TotalAmount, CityName, COUNT(*) AS Transactions, Latitude, Longitude
                    FROM transactions
                    WHERE POS_entrymode = ?
                    GROUP BY CityName
                '''

                # Execute the query and fetch the results into a DataFrame
                city_data = pd.read_sql(query, conn, params=(selected_entrymode,))

            elif path_length == 2:  # MerchantGroup for a specific POS_entrymode
                selected_entrymode = path_components[0]  # grandparent
                selected_merchantGroup = path_components[1]  # parent

                # Replicating the logic for color_scale from path_length == 1
                if selected_entrymode.lower() == 'online':
                    color_scale = 'Bluered_r'
                elif selected_entrymode.lower() == 'insert':
                    color_scale = 'speed'
                elif selected_entrymode.lower() == 'tap':
                    color_scale = 'YlOrRd'
                elif selected_entrymode.lower() == 'swipe':
                    color_scale = 'Purpor'
                else:
                    color_scale = 'turbo'  # Default color scale

                # SQL query to retrieve transaction data by city for the selected MerchantGroup for a specific POS_entrymode
                query = '''
                    SELECT Sum(TransactionAmount) AS TotalAmount, CityName, COUNT(*) AS Transactions, Latitude, Longitude
                    FROM transactions
                    WHERE POS_entrymode = ? AND MerchantGroup = ?
                    GROUP BY CityName
                '''

                # Execute the query and fetch the results into a DataFrame
                city_data = pd.read_sql(query, conn, params=(selected_entrymode, selected_merchantGroup,))

            elif path_length == 3:  # Status for a specific MerchantGroup and POS_entrymode
                selected_entrymode = path_components[0]  # grandparent
                selected_merchantGroup = path_components[1]  # parent
                selected_status = path_components[2]  # label

                # Choose color scale based on the selected Status
                if selected_status.lower() == 'approved':
                    color_scale = 'Tealgrn'
                elif selected_status.lower() == 'declined':
                    color_scale = 'Redor'
                else:
                    color_scale = 'turbo'  # Default color scale

                # SQL query to retrieve transaction data by city for the selected subcategory and response code
                query = '''
                    SELECT Sum(TransactionAmount) AS TotalAmount, CityName, COUNT(*) AS Transactions, Latitude, Longitude
                    FROM transactions
                    WHERE POS_entrymode = ? AND MerchantGroup = ? AND Status = ?
                    GROUP BY CityName
                '''

                city_data = pd.read_sql(query, conn, params=(selected_entrymode, selected_merchantGroup, selected_status,))

            updated_df = city_data[['CityName', 'Transactions', 'Latitude', 'Longitude', 'TotalAmount']]

            all_data_diffq = (updated_df["Transactions"].max() - updated_df["Transactions"].min()) / 16
            updated_df["scale"] = (updated_df["Transactions"] - updated_df["Transactions"].min()) / all_data_diffq
            updated_df['TotalAmount'] = updated_df['TotalAmount'].apply(lambda x: locale.currency(x, grouping=True))

            #Create a Scatter mapbox plot using px.scatter_mapbox
            fig = px.scatter_mapbox(
                data_frame=updated_df,
                lat='Latitude',
                lon='Longitude',
                color='Transactions',
                size=updated_df["scale"],
                color_continuous_scale=color_scale,
                size_max=40, zoom=3, mapbox_style="open-street-map",
                hover_name='CityName',
                hover_data={'Transactions': True, 'TotalAmount': True, 'scale': False, 'Latitude': False, 'Longitude': False},
                labels={'Transactions': 'Transactions'},
                template='plotly_dark',
                custom_data=['Transactions', 'TotalAmount']
            )
            fig.update_traces(
                hovertemplate=
                f"<b style='font-size: 18px;'>City:</b> <span style='font-size: 18px;'>%{{hovertext}}</span><br>"
                f"<b style='font-size: 18px;'>Transactions:</b> <span style='font-size: 18px;'>%{{customdata[0]:,}}</span><br>"
                f"<b style='font-size: 18px;'>Total Transaction Amount:</b> <span style='font-size: 18px;'>%{{customdata[1]}}</span><br>"
            )

            # Add a title to the map based on the path length
            if path_length == 1:
                fig.update_layout(
                    title=f'Transactions by City for POS Entry Mode: {selected_entrymode}',
                    title_x=0.5,
                    margin=dict(t=110),
                )
            elif path_length == 2:
                fig.update_layout(
                    title=f'Transactions by City for Merchant Group: {selected_merchantGroup} with POS Entry Mode: {selected_entrymode}',
                    title_x=0.5,
                    margin=dict(t=110),
                )
            elif path_length == 3:
                fig.update_layout(
                    title=f'Transactions by City for {selected_entrymode} with Merchant Group: {selected_merchantGroup} AND Status: {selected_status}',
                    title_x=0.5,
                    margin=dict(t=110),
                )

            return fig

        except Exception as e:
            print(f"Error: {e}")
            return px.scatter_mapbox()