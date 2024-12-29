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


locale.setlocale(locale.LC_ALL, '')

dash_layout = html.Div(className= 'container', children=[
        html.Div(className='viewing-port', id='viewing-port',style={'border': '1px solid black'}, children=[
            dcc.Graph(id='base-plot', style={"height": "100%", "width": "100%"}),
            dcc.Graph(id='funnel-plot', style={"height": "100%", "width": "100%", "display": "none"}),
            dcc.Graph(id='us-map-graph', style={"height": "100%", "width": "100%", "display": "none"}),
            dcc.Graph(id='pie-plot', style={"height": "100%", "width": "100%", "display": "none"}),
            dcc.Interval(id='interval', interval=150, n_intervals=0)
        ]),

        html.Div(className='threejs-plot-container', id='threejs-plot-container', style={'border': '1px solid black'}, children=[
                    html.A([
                    html.Img(
                        src='assets/threejs.png',
                        style={
                            'height' : '100%',
                            'width' : '100%',
                            'position' : 'relative',
                            'object-fit' : 'cover',
                        })
            ], href='http://127.0.0.1:5000/')
        ]),

        html.Div(className='base-plot-container', id='base-plot-container', style={'border': '1px solid black'}, children=[
            dcc.Graph(id='base-plot-2', style={"height": "100%", "width": "100%"}),
        ]),

        html.Div(className='funnel-container', id='funnel-container', style={'border': '1px solid black'}, children=[
            dcc.Graph(id='funnel-plot-2', style={"height": "100%", "width": "100%"}),
        ]),

        html.Div(className='us-map-container', id='us-map-container', style={'border': '1px solid black'}, children=[
            dcc.Graph(id='us-map-graph-2', style={"height": "100%", "width": "100%"}),
        ]),

        html.Div(className='pie-container', id='pie-container', style={'border': '1px solid black'}, children=[
            dcc.Graph(id='pie-plot-2', style={"height": "100%", "width": "100%"}),
        ]),
])


def create_dashapp(app, var_data):
    print(app)
    print(var_data)
    category = var_data.get("categorical_variable")
    numerical_feature = var_data.get("numerical_variable")
    print(category)
    print(numerical_feature)


    def update_base_plot(_):
        try:
            # Open a new database connection
            conn = sqlite3.connect(r"C:\Users\yashu\OneDrive\Desktop\Github_Projects\Credit_Card_Data_Visulization_Platform\Final_Databases\scatterplot.db")


            # SQL query to retrieve aggregated data based on selected category and numerical feature
            query = f'''
                SELECT {category}, WeekOfMonth, SUM({numerical_feature}) AS TotalAmount
                FROM transactions
                GROUP BY {category}, WeekOfMonth
                ORDER BY TotalAmount DESC
            '''

            # Fetch the data from the database
            df_base = pd.read_sql(query, conn)

            # Close the database connection
            conn.close()

            # Formatting the Total column
            df_base['TotalAmount'] = df_base['TotalAmount'].apply(lambda x: locale.currency(x, grouping=True))

            # Creating 3D scatter plot with sphere markers
            fig = go.Figure()

            # Define colorscale for WeekOfMonth values
            colorscale = [
                [0, 'blue'],        # Week 1: Blue
                [0.25, 'purple'],   # Week 2: Purple
                [0.5, 'darkorange'],   # Week 3: Dark Orange
                [0.75, 'yellow'],   # Week 4: Yellow
                [1, 'pink']         # Week 5: Pink
            ]

            # Add the scatter plot trace
            fig.add_trace(
                go.Scatter3d(
                    x=df_base[category],
                    y=df_base['WeekOfMonth'].astype(int),
                    z=df_base['TotalAmount'],
                    mode='markers+text',
                    marker=dict(
                        size=15,  # Adjust the size of markers to make them smaller
                        symbol='circle',  # Use 'circle' symbol for spheres
                        color=df_base['WeekOfMonth'],
                        colorscale=colorscale,
                    ),
                    textposition='top center',
                    hovertemplate=(
                        f"<b style='font-size: 18px;'>{category}</b>: "
                        "<span style='font-size: 18px;'>%{x}</span><br>"
                        f"<b style='font-size: 18px;'>{numerical_feature}</b>: "
                        "<span style='font-size: 18px;'>%{z}</span><br>"
                        "<b style='font-size: 18px;'>WeekOfMonth</b>: "
                        "<span style='font-size: 18px;'>%{y}</span><br>"
                    )
                )
            )

            fig.update_layout(
                title=f'Total {numerical_feature} by {category} and Week of Month',
                title_font=dict(size=26),  # Increased the font size
                title_x=0.5,
                title_y=0.95,
                scene=dict(
                    xaxis=dict(
                        title=category,
                        title_font=dict(size=28, color='white'),
                        showticklabels=True, # Hide tick labels
                        showgrid=True,       # Hide grid lines
                        showline=False,   # Hide the x-axis
                        zeroline=False,
                    ),
                    yaxis=dict(
                        title='Week of Month',
                        title_font=dict(size=28, color='white'),
                        tickmode='array',
                        tickvals=[0.5, 1.5, 2.5, 3.5, 4.5, 5.5],
                        ticktext=['1', '2', '3', '4', '5'],  # Display tick labels as 1, 2, 3, 4, 5],
                        showticklabels=True, # Hide tick labels
                        showgrid=True,       # Hide grid lines
                        showline=False,   # Hide the y-axis
                        zeroline=False,
                    ),
                    zaxis=dict(
                        title=f'Total {numerical_feature} ($)',
                        title_font=dict(size=28, color='white'),
                        autorange='reversed',
                        showticklabels=False, # Hide tick labels
                        showgrid=True,       # Hide grid lines
                        showline=False,   # Hide the z-axis
                        zeroline=False,
                    ),
                    aspectratio=dict(x=0.9, y=0.9, z=0.9),  # Adjust the aspect ratio of the plot
                ),
                margin=dict(l=10, r=10, t=90, b=10),  # Increase the b value to enlarge the viewing window
                template='plotly_dark',
            )

            return fig

        except Exception as e:
            print(f"Error: {e}")
            return go.Figure()
       

    def update_second_container(base_plot_click_data):
        try:
            # Get the selected subcategory from base_plot_click_data
            selected_subcategory = base_plot_click_data['points'][0]['x']

            # Open a new database connection
            conn = sqlite3.connect(r"C:\Users\yashu\OneDrive\Desktop\Github_Projects\Credit_Card_Data_Visulization_Platform\Final_Databases\Final_database.db")

            # SQL query to retrieve the number of approvals and declines for each PhysicalSource in the selected city
            query = f'''
                SELECT {category}, StateCode, SUM({numerical_feature}) as TotalAmount,
                    SUM(CASE WHEN (Status = 'Approved') THEN {numerical_feature} ELSE 0 END) AS TotalNumericalApprovals,
                    SUM(CASE WHEN (Status = 'Declined') THEN {numerical_feature} ELSE 0 END) AS TotalNumericalDeclines,
                    COUNT(CASE WHEN (Status = 'Approved') THEN 1 ELSE NULL END) AS Approvals,
                    COUNT(CASE WHEN (Status = 'Declined') THEN 1 ELSE NULL END) AS Declines
                FROM transactions
                WHERE {category} = ?
                GROUP BY StateCode, {category}
            '''

            # Execute the query and fetch the results into a DataFrame
            df = pd.read_sql(query, conn, params=(selected_subcategory,))

            # Close the database connection
            conn.close()

            # Add a total column to the DataFrame
            df['Total'] = df['Approvals'] + df['Declines']

            # Sort the DataFrame by the total column in descending order
            df = df.sort_values('Total', ascending=False)
            # df['Total'] = df['Total'].apply(lambda x: locale.currency(x, grouping=True))
            # df['Declines'] = df['Declines'].apply(lambda x: locale.currency(x, grouping=True))
            df['TotalNumericalApprovals'] = df['TotalNumericalApprovals'].apply(lambda x: locale.currency(x, grouping=True))
            df['TotalNumericalDeclines'] = df['TotalNumericalDeclines'].apply(lambda x: locale.currency(x, grouping=True))                                                                           

            # Create a stacked funnel chart using Plotly Graph Objects
            fig = go.Figure()

            fig.add_trace(go.Funnel(
                name='Approvals',
                y=df['StateCode'],
                x=df['Approvals'],  # Apply the square root transformation
                text=df['Approvals'],  # Display the actual numbers of approvals
                # textinfo="text",  # Use the text attribute for the labels
                hovertemplate=(
                    f"<b style='font-size: 18px;'>Count:</b> "
                    f"<span style='font-size: 18px;'>%{{x:,.0f}}</span><br>"
                    f"<b style='font-size: 18px;'>Total {numerical_feature} for Approvals = </b> "
                    f"<span style='font-size: 18px;'>%{{customdata}}</span><br>"
                ),
                customdata=df['TotalNumericalApprovals']
            ))

            fig.add_trace(go.Funnel(
                name='Declines',
                y=df['StateCode'],
                x=df['Declines'],  # Apply the square root transformation
                text=df['Declines'],  # Display the actual numbers of declines
                # textinfo="text",  # Use the text attribute for the labels
                hovertemplate=(
                    f"<b style='font-size: 18px; color: white'>Count:</b> "
                    f"<span style='font-size: 18px; color: white'>%{{x:,.0f}}</span><br>"
                    f"<b style='font-size: 18px; color: white'>Total {numerical_feature} for Declines = </b> "
                    f"<span style='font-size: 18px; color: white'>%{{customdata}}</span><br>"
                ),
                customdata=df['TotalNumericalDeclines']
            ))


            # Update the layout
            fig.update_layout(
                title=f'Approved and Declined Transactions by State Code in {category} : {selected_subcategory} <br>from January 11, 2021 to February 7, 2021',
                title_x=0.5,
                title_y=0.95,
                title_font=dict(size=20),
                funnelmode="stack",
                template='plotly_dark'
            )

            # Return a dcc.Graph with the funnel chart
            return fig

        except Exception as e:
            print(f"Error: {e}")
            return []
       
    def generate_map(base_plot_click_data, funnel_plot_click_data):
        try:
            # Get the selected subcategory from base_plot_click_data
            selected_subcategory = base_plot_click_data['points'][0]['x']
            # Get the selected state from funnel_plot_click_data
            selected_state = funnel_plot_click_data['points'][0]['y']

            # Open a new database connection
            conn = sqlite3.connect(r"C:\Users\yashu\OneDrive\Desktop\Github_Projects\Credit_Card_Data_Visulization_Platform\Final_Databases\Final_database.db")

            # SQL query to retrieve transaction data by city for the selected subcategory and response code
            query = f'''
                SELECT StateCode, SUM({numerical_feature}) AS TotalAmount, CityName, SUM(CASE WHEN (IResponseCode != 0) THEN 1 ELSE 0 END) AS Transactions, Latitude, Longitude
                FROM transactions
                WHERE {category} = ? AND StateCode = ?
                GROUP BY CityName, StateCode
            '''

            # Execute the query and fetch the results into a DataFrame
            city_data = pd.read_sql(query, conn, params=(selected_subcategory, selected_state))
            updated_df = city_data[['CityName', 'Transactions', 'Latitude', 'Longitude', 'TotalAmount']]
            updated_df['TotalAmount'] = updated_df['TotalAmount'].apply(lambda x: locale.currency(x, grouping=True))
           
            # Close the database connection
            conn.close()

            # Find the center latitude and longitude for the selected state code
            statecode_data = pd.read_excel(r"C:\Users\yashu\OneDrive\Desktop\Github_Projects\Credit_Card_Data_Visulization_Platform\Final_Databases\statecode_data.xlsx")
            state_center = statecode_data[statecode_data['State'] == selected_state]

            # Create a Scatter mapbox plot using px.scatter_mapbox
            fig = px.scatter_mapbox(
                data_frame=updated_df,
                lat='Latitude',
                lon='Longitude',
                color='Transactions',
                size='Transactions',
                size_max=40,
                zoom=4,  # Set a default zoom level for the US map
                center={"lat": state_center['Latitude'].values[0], "lon": state_center['Longitude'].values[0]},  # Set the center of the map
                hover_name='CityName',
                hover_data={'Transactions': True, 'TotalAmount': True, 'Latitude': False, 'Longitude': False},
                labels={'Transactions': 'Transactions'},
                template='plotly_dark',
                mapbox_style='carto-positron',
                color_continuous_scale='Rainbow',
                custom_data=['Transactions', 'TotalAmount']  # Added this line
            )
            fig.update_traces(
                hovertemplate=
                f"<b style='font-size: 18px;'>City:</b> <span style='font-size: 18px;'>%{{hovertext}}</span><br>"
                f"<b style='font-size: 18px;'>Transactions:</b> <span style='font-size: 18px;'>%{{customdata[0]:,}}</span><br>"
                f"<b style='font-size: 18px;'>Total {numerical_feature}:</b> <span style='font-size: 18px;'>%{{customdata[1]}}</span><br>"
            )


            # Add a title to the map
            fig.update_layout(
                title=f'Declined Transactions: by City for {category} : {selected_subcategory} within {selected_state}',
                title_x=0.5,
                title_y=0.95,
                title_font=dict(size=26),
                margin=dict(t=110),
            )
            return fig

        except Exception as e:
            print(f"Error: {e}")
            return dash.no_update

    def update_pie_container(base_plot_click_data, us_map_click_data):
        try:
            # Get the selected subcategory from base_plot_click_data
            selected_subcategory = base_plot_click_data['points'][0]['x']
            # Get the selected city from the click data on the US map
            selected_city = us_map_click_data['points'][0]['hovertext']

            # Open a new database connection
            conn = sqlite3.connect(r"C:\Users\yashu\OneDrive\Desktop\Github_Projects\Credit_Card_Data_Visulization_Platform\Final_Databases\new_datab.db")
            # SQL query to retrieve the number of approvals and declines for each 'IResponseCode' in the selected city and subcategory
            query = f'''
                SELECT {category}, SUM({numerical_feature}) AS TotalAmount, IRC_Description, COUNT(*) AS Count
                FROM transactions
                WHERE CityName = ? AND {category} = ? AND IRC_Description NOT IN ('Successful approval')
                GROUP BY IRC_Description, {category}
            '''
            # Execute the query and fetch the results into a DataFrame
            df = pd.read_sql(query, conn, params=(selected_city, selected_subcategory,))
            # Close the database connection
            conn.close()

            # Calculate the total count of transactions in the selected city
            total_count = df['Count'].sum()
            # Calculate the percentage for each 'IResponseCode'
            df['Percentage'] = df['Count'] / total_count * 100

            # Round off the 'Percentage' to 2 decimals
            df['Percentage'] = df['Percentage'].round(2)

            df['TotalAmount'] = df['TotalAmount'].apply(lambda x: locale.currency(x, grouping=True))
            # Combine 'Count' and 'TotalAmount' into a string
            custom_data = [f"<b style='font-size: 18px;'>Count: </b> <span style='font-size: 18px;'>{count}</span><br> <b style='font-size: 18px;'>Total {numerical_feature}: </b> <span style='font-size: 18px;'>{total_amount}</span><br>"
            for count, total_amount in zip(df['Count'], df['TotalAmount'])]

            fig = go.Figure(data=[go.Pie(labels=df['IRC_Description'], values=df['Percentage'],
                                        hole=0.4, customdata=custom_data,
                                        hovertemplate=(
                                                f"<b style='font-size: 18px;'>IRC_Description:</b> <span style='font-size: 18px;'>%{{label}}</span><br>"
                                                f"<b style='font-size: 18px;'>Percentage:</b> <span style='font-size: 18px;'>%{{percent}}</span><br>"
                                                f"<b style='font-size: 18px;'></b> <span style='font-size: 18px;'>%{{customdata}}</span><br>"
                                                # f"<b style='font-size: 18px;'>Total {numerical_feature}:</b> <span style='font-size: 18px;'>%{{customdata[1]}}</span><br>"
                                            ))])

            fig.update_traces(textinfo='label+percent', insidetextorientation='radial', textfont=dict(color='white', size=14))

            fig.update_layout(
                title=f'Percentage of declines in {selected_city} for {category} : {selected_subcategory}',
                title_x=0.5,
                title_y=0.95,
                title_font=dict(size=26),
                template='plotly_dark',
                hoverlabel=dict(
                    font=dict(color='white', size=18)
                )
            )

            return fig
        except Exception as e:
            print(f"Error: {e}")
            return []

    @app.callback(
    Output('base-plot', 'figure'),
    Output('base-plot', 'style'),
    Input('base-plot', 'id')
    )
    def generate_base_plot(_):
        return update_base_plot(_), {"display": "block"}
   
    @app.callback(
        Output('funnel-plot', 'figure'),
        Output('funnel-plot', 'style'),
        Input('base-plot', 'clickData'),
        State('funnel-plot', 'style'),
    )

    def update_funnel_plot(clickData, current_style):
        if clickData is None:
            return dash.no_update, current_style
        return update_second_container(clickData), {"display": "block"}
   
    # Modify the callback to include click data from funnel plot
    @app.callback(
        Output('us-map-graph', 'figure'),
        Output('us-map-graph', 'style'),
        State('base-plot', 'clickData'),  # Selected subcategory from base plot
        Input('funnel-plot', 'clickData'),  # Number of declines from funnel plot
        State('us-map-graph', 'style'),
    )
    def display_map_container(base_plot_clickData, funnel_plot_clickData, current_style):
        if base_plot_clickData is None or funnel_plot_clickData is None:
            return dash.no_update, current_style
        fig = generate_map(base_plot_clickData, funnel_plot_clickData)
        return fig, {"display": "block"}
   
    @app.callback(
        Output('pie-plot', 'figure'),
        Output('pie-plot', 'style'),
        Input('us-map-graph', 'clickData'),
        State('base-plot', 'clickData'),
        State('pie-plot', 'style'),
    )

    def update_pie_plot(us_map_clickData, base_plot_clickData, current_style):
        if us_map_clickData is None or base_plot_clickData is None:
            return dash.no_update, current_style
        return update_pie_container(base_plot_clickData, us_map_clickData), {"display": "block"}
   
    def update_base_plot_2(_):
        try:
            # Open a new database connection
            conn = sqlite3.connect(r"C:\Users\yashu\OneDrive\Desktop\Github_Projects\Credit_Card_Data_Visulization_Platform\Final_Databases\scatterplot.db")


            # SQL query to retrieve aggregated data based on selected category and numerical feature
            query = f'''
                SELECT {category}, WeekOfMonth, SUM({numerical_feature}) AS TotalAmount
                FROM transactions
                GROUP BY {category}, WeekOfMonth
                ORDER BY TotalAmount DESC
            '''

            # Fetch the data from the database
            df_base = pd.read_sql(query, conn)

            # Close the database connection
            conn.close()

            # Formatting the Total column
            df_base['TotalAmount'] = df_base['TotalAmount'].apply(lambda x: locale.currency(x, grouping=True))

            # Creating 3D scatter plot with sphere markers
            fig = go.Figure()

            # Define colorscale for WeekOfMonth values
            colorscale = [
                [0, 'blue'],        # Week 1: Blue
                [0.25, 'purple'],   # Week 2: Purple
                [0.5, 'darkorange'],   # Week 3: Dark Orange
                [0.75, 'yellow'],   # Week 4: Yellow
                [1, 'pink']         # Week 5: Pink
            ]

            # Add the scatter plot trace
            fig.add_trace(
                go.Scatter3d(
                    x=df_base[category],
                    y=df_base['WeekOfMonth'].astype(int),
                    z=df_base['TotalAmount'],
                    mode='markers+text',
                    marker=dict(
                        size=5,  # Adjust the size of markers to make them smaller
                        symbol='circle',  # Use 'circle' symbol for spheres
                        color=df_base['WeekOfMonth'],
                        colorscale=colorscale,
                    ),
                    textposition='top center',
                    hovertemplate=(
                        f"<b style='font-size: 18px;'>{category}</b>: "
                        "<span style='font-size: 18px;'>%{x}</span><br>"
                        f"<b style='font-size: 18px;'>{numerical_feature}</b>: "
                        "<span style='font-size: 18px;'>%{z}</span><br>"
                        "<b style='font-size: 18px;'>WeekOfMonth</b>: "
                        "<span style='font-size: 18px;'>%{y}</span><br>"
                    )
                )
            )

            fig.update_layout(
                title=f'Total {numerical_feature} by <br>{category} and Week of Month',
                scene=dict(
                    xaxis=dict(
                        title=category,
                        title_font=dict(size=15, color='white'),
                        showticklabels=True, # Hide tick labels
                        showgrid=True,       # Hide grid lines
                        showline=False,   # Hide the x-axis
                        zeroline=False,
                    ),
                    yaxis=dict(
                        title='Week of Month',
                        title_font=dict(size=15, color='white'),
                        tickmode='array',
                        tickvals=[0.5, 1.5, 2.5, 3.5, 4.5, 5.5],
                        ticktext=['1', '2', '3', '4', '5'],  # Display tick labels as 1, 2, 3, 4, 5],
                        showticklabels=True, # Hide tick labels
                        showgrid=True,       # Hide grid lines
                        showline=False,   # Hide the y-axis
                        zeroline=False,
                    ),
                    zaxis=dict(
                        title=f'Total {numerical_feature} ($)',
                        title_font=dict(size=15, color='white'),
                        autorange='reversed',
                        showticklabels=False, # Hide tick labels
                        showgrid=True,       # Hide grid lines
                        showline=False,   # Hide the z-axis
                        zeroline=False,
                    ),
                    aspectratio=dict(x=0.7, y=0.7, z=0.7),  # Adjust the aspect ratio of the plot
                ),
                margin=dict(l=10, r=10, t=90, b=10),  # Increase the b value to enlarge the viewing window
                template='plotly_dark',
            )

            return fig

        except Exception as e:
            print(f"Error: {e}")
            return go.Figure()

    def update_second_container_2(base_plot_click_data):
        try:
            # Get the selected subcategory from base_plot_click_data
            selected_subcategory = base_plot_click_data['points'][0]['x']

            # Open a new database connection
            conn = sqlite3.connect(r"C:\Users\yashu\OneDrive\Desktop\Github_Projects\Credit_Card_Data_Visulization_Platform\Final_Databases\Final_database.db")

            # SQL query to retrieve the number of approvals and declines for each PhysicalSource in the selected city
            query = f'''
                SELECT {category}, StateCode, SUM({numerical_feature}) as TotalAmount,
                    SUM(CASE WHEN (Status = 'Approved') THEN {numerical_feature} ELSE 0 END) AS TotalNumericalApprovals,
                    SUM(CASE WHEN (Status = 'Declined') THEN {numerical_feature} ELSE 0 END) AS TotalNumericalDeclines,
                    COUNT(CASE WHEN (Status = 'Approved') THEN 1 ELSE NULL END) AS Approvals,
                    COUNT(CASE WHEN (Status = 'Declined') THEN 1 ELSE NULL END) AS Declines
                FROM transactions
                WHERE {category} = ?
                GROUP BY StateCode, {category}
            '''

            # Execute the query and fetch the results into a DataFrame
            df = pd.read_sql(query, conn, params=(selected_subcategory,))

            # Close the database connection
            conn.close()

            # Add a total column to the DataFrame
            df['Total'] = df['Approvals'] + df['Declines']

            # Sort the DataFrame by the total column in descending order
            df = df.sort_values('Total', ascending=False)
            # df['Total'] = df['Total'].apply(lambda x: locale.currency(x, grouping=True))
            # df['Declines'] = df['Declines'].apply(lambda x: locale.currency(x, grouping=True))
            df['TotalNumericalApprovals'] = df['TotalNumericalApprovals'].apply(lambda x: locale.currency(x, grouping=True))
            df['TotalNumericalDeclines'] = df['TotalNumericalDeclines'].apply(lambda x: locale.currency(x, grouping=True))
                                                                            
            # Create a stacked funnel chart using Plotly Graph Objects
            fig = go.Figure()

            fig.add_trace(go.Funnel(
                name='Approvals',
                y=df['StateCode'],
                x=df['Approvals'],  # Apply the square root transformation
                text=df['Approvals'],  # Display the actual numbers of approvals
                # textinfo="text",  # Use the text attribute for the labels
                hovertemplate=(
                    f"<b style='font-size: 18px;'>Count:</b> "
                    f"<span style='font-size: 18px;'>%{{x:,.0f}}</span><br>"
                    f"<b style='font-size: 18px;'>Total {numerical_feature} for Approvals = </b> "
                    f"<span style='font-size: 18px;'>%{{customdata}}</span><br>"
                ),
                customdata=df['TotalNumericalApprovals']
            ))

            fig.add_trace(go.Funnel(
                name='Declines',
                y=df['StateCode'],
                x=df['Declines'],  # Apply the square root transformation
                text=df['Declines'],  # Display the actual numbers of declines
                # textinfo="text",  # Use the text attribute for the labels
                hovertemplate=(
                    f"<b style='font-size: 18px; color: white'>Count:</b> "
                    f"<span style='font-size: 18px; color: white'>%{{x:,.0f}}</span><br>"
                    f"<b style='font-size: 18px; color: white'>Total {numerical_feature} for Declines = </b> "
                    f"<span style='font-size: 18px; color: white'>%{{customdata}}</span><br>"
                ),
                customdata=df['TotalNumericalDeclines']
            ))


            # Update the layout
            fig.update_layout(
                title=f'Approved and Declined Trans by <br>State Code in {category} : {selected_subcategory}',
                funnelmode="stack",
                template='plotly_dark'
            )

            # Return a dcc.Graph with the funnel chart
            return fig

        except Exception as e:
            print(f"Error: {e}")
            return []
        
    def generate_map_2(base_plot_click_data, funnel_plot_click_data):
        try:
            # Get the selected subcategory from base_plot_click_data
            selected_subcategory = base_plot_click_data['points'][0]['x']
            # Get the selected state from funnel_plot_click_data
            selected_state = funnel_plot_click_data['points'][0]['y']

            # Open a new database connection
            conn = sqlite3.connect(r"C:\Users\yashu\OneDrive\Desktop\Github_Projects\Credit_Card_Data_Visulization_Platform\Final_Databases\Final_database.db")

            # SQL query to retrieve transaction data by city for the selected subcategory and response code
            query = f'''
                SELECT StateCode, SUM({numerical_feature}) AS TotalAmount, CityName, SUM(CASE WHEN (IResponseCode != 0) THEN 1 ELSE 0 END) AS Transactions, Latitude, Longitude
                FROM transactions
                WHERE {category} = ? AND StateCode = ?
                GROUP BY CityName, StateCode
            '''

            # Execute the query and fetch the results into a DataFrame
            city_data = pd.read_sql(query, conn, params=(selected_subcategory, selected_state))
            updated_df = city_data[['CityName', 'Transactions', 'Latitude', 'Longitude', 'TotalAmount']]
            updated_df['TotalAmount'] = updated_df['TotalAmount'].apply(lambda x: locale.currency(x, grouping=True))
           
            # Close the database connection
            conn.close()

            # Find the center latitude and longitude for the selected state code
            statecode_data = pd.read_excel(r"C:\Users\yashu\OneDrive\Desktop\Github_Projects\Credit_Card_Data_Visulization_Platform\Final_Databases\statecode_data.xlsx")
            state_center = statecode_data[statecode_data['State'] == selected_state]

            # Create a Scatter mapbox plot using px.scatter_mapbox
            fig = px.scatter_mapbox(
                data_frame=updated_df,
                lat='Latitude',
                lon='Longitude',
                #color='Transactions',
                size='Transactions',
                size_max=40,
                zoom=4,  # Set a default zoom level for the US map
                center={"lat": state_center['Latitude'].values[0], "lon": state_center['Longitude'].values[0]},  # Set the center of the map
                hover_name='CityName',
                hover_data={'Transactions': True, 'TotalAmount': True, 'Latitude': False, 'Longitude': False},
                labels={'Transactions': 'Transactions'},
                template='plotly_dark',
                mapbox_style='carto-positron',
                color_continuous_scale='Rainbow',
                custom_data=['Transactions', 'TotalAmount']  # Added this line
            )
            fig.update_traces(
                hovertemplate=
                f"<b style='font-size: 18px;'>City:</b> <span style='font-size: 18px;'>%{{hovertext}}</span><br>"
                f"<b style='font-size: 18px;'>Transactions:</b> <span style='font-size: 18px;'>%{{customdata[0]:,}}</span><br>"
                f"<b style='font-size: 18px;'>Total {numerical_feature}:</b> <span style='font-size: 18px;'>%{{customdata[1]}}</span><br>"
            )


            # Add a title to the map
            fig.update_layout(
                title=f'Declined Tran by City for {category}<br> : {selected_subcategory} within {selected_state}',
                margin=dict(t=85, l=10, r=10, b=2)
            )
            return fig

        except Exception as e:
            print(f"Error: {e}")
            return dash.no_update
           
    def update_pie_container_2(base_plot_click_data, us_map_click_data):
        try:
            # Get the selected subcategory from base_plot_click_data
            selected_subcategory = base_plot_click_data['points'][0]['x']
            # Get the selected city from the click data on the US map
            selected_city = us_map_click_data['points'][0]['hovertext']

            # Open a new database connection
            conn = sqlite3.connect(r"C:\Users\yashu\OneDrive\Desktop\Github_Projects\Credit_Card_Data_Visulization_Platform\Final_Databases\datab.db")
            # SQL query to retrieve the number of approvals and declines for each 'IResponseCode' in the selected city and subcategory
            query = f'''
                SELECT {category}, IResponseCode, COUNT(*) AS Count
                FROM transactions
                WHERE CityName = ? AND {category} = ? AND IResponseCode NOT IN (0)
                GROUP BY IResponseCode, {category}
            '''
            # Execute the query and fetch the results into a DataFrame
            df = pd.read_sql(query, conn, params=(selected_city, selected_subcategory,))
            # Close the database connection
            conn.close()

            # Calculate the total count of transactions in the selected city
            total_count = df['Count'].sum()
            # Calculate the percentage for each 'IResponseCode'
            df['Percentage'] = df['Count'] / total_count * 100
            # Create the pie chart using Plotly Express
            fig = px.pie(df, values='Percentage', names='IResponseCode', hole=0.4)
            fig.update_traces(textinfo='label+percent', textposition='inside', insidetextorientation='radial', textfont=dict(color='white', size=15))
            # Update the layout
            fig.update_layout(
                title=f'Percentage of declines in <br>{selected_city} for <br>{category} : {selected_subcategory}',
                template='plotly_dark',
            )
            # Return a dcc.Graph with the pie chart
            return fig
        except Exception as e:
            print(f"Error: {e}")
            return []

    @app.callback(
    Output('base-plot-2', 'figure'),
    Input('base-plot', 'id'),
    # prevent_initial_call=True
    )
    def generate_base_plot_2(_):
        return update_base_plot_2(_)
   
    @app.callback(
        Output('funnel-plot-2', 'figure'),
        Input('funnel-plot', 'clickData'),
        Input('base-plot', 'clickData'),
    )

    def update_funnel_plot_2(clickData, base_plot_click_data):
        if clickData is None:
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
        return update_second_container_2(base_plot_click_data)
   
    # Modify the callback to include click data from funnel plot
    @app.callback(
        Output('us-map-graph-2', 'figure'),
        State('base-plot', 'clickData'),  # Selected subcategory from base plot
        State('funnel-plot', 'clickData'),  # Number of declines from funnel plot
        Input('us-map-graph', 'clickData')
    )
    def display_map_container_2(base_plot_clickData, funnel_plot_clickData, us_map_clickData):
        if base_plot_clickData is None or funnel_plot_clickData is None or us_map_clickData is None:
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
        fig = generate_map_2(base_plot_clickData, funnel_plot_clickData)
        return fig
   
    @app.callback(
        Output('pie-plot-2', 'figure'),
        State('us-map-graph', 'clickData'),
        State('base-plot', 'clickData'),
        Input('pie-plot', 'clickData')
    )

    def update_pie_plot_2(us_map_clickData, base_plot_clickData, pie_plot_clickData):
        if us_map_clickData is None or base_plot_clickData is None or pie_plot_clickData is None:
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
        return update_pie_container_2(base_plot_clickData, us_map_clickData)