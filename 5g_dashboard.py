import pandas as pd
from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
import numpy as np
from datetime import timedelta
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from plotly.subplots import make_subplots

def load_data(filepath):
    df = pd.read_csv(filepath)
    df['date_time'] = pd.to_datetime(df['date_time'])
    return df

data = load_data('5G_NR_data.csv')

# Extract unique cell_ids, kpi_categories, and pis
cell_ids = data['cell_id'].unique()
kpi_categories = data['kpi_category'].unique()
pis = data['pi'].unique()

# Extract the minimum and maximum dates
min_date = data['date_time'].min()
max_date = data['date_time'].max()

def convert_rgb_to_hex(rgb_color):
    """Convert RGB color to hex color."""
    rgb_color = tuple(int(rgb*255) for rgb in rgb_color[:3])  # Scale RGB color
    return '#{:02x}{:02x}{:02x}'.format(*rgb_color)

# Create a color map
cmap = px.colors.qualitative.Plotly

# Create a list of hex colors from the color map
line_colors = cmap * (len(pis) // len(cmap)) + cmap[:len(pis) % len(cmap)]


def resample_data(selected_cell, selected_pis, date_range, frequency='D'):
    """Resample data for selected cell and PIs over specified date range."""
    start_date, end_date = date_range
    # Ensure selected_pis is a list
    if not isinstance(selected_pis, list):
        selected_pis = [selected_pis]
    # Now proceed with filtering and resampling
    resampled_data = data[
        (data['cell_id'] == selected_cell) &
        (data['pi'].isin(selected_pis)) &
        (data['date_time'] >= start_date) &
        (data['date_time'] <= end_date)
    ]
    resampled_data = resampled_data.set_index('date_time').groupby('pi').resample(frequency).mean(numeric_only=True).reset_index()
    return resampled_data


# Function to generate date marks for range slider
def get_date_marks(start_date, end_date):
    dates = pd.date_range(start_date, end_date, freq='MS')
    date_marks = {int((date - start_date).days): str(date.date()) for date in dates}
    date_marks[(end_date - start_date).days] = str(end_date.date())
    return date_marks

# Functions for the different chart types
def update_line_chart(selected_cell, selected_pis, date_range):
    """Updates the line chart"""
    resampled_data = resample_data(selected_cell, selected_pis, date_range)
    resampled_data = resampled_data.sort_values(by=['date_time'])
    fig = go.Figure()
    for i, pi in enumerate(selected_pis):
        pi_data = resampled_data[resampled_data['pi'] == pi]
        pi_data['date_time'] = pi_data['date_time'].dt.strftime('%Y-%m-%d')
        pi_data = pi_data.dropna()
        fig.add_trace(go.Scatter(x=pi_data['date_time'], y=pi_data['value'], mode='lines+markers+text', name=pi, line=dict(color=line_colors[i % len(line_colors)]),
                                 text=["{:.2f}".format(val) for val in pi_data['value']],
                                 textposition='top center',
                                 textfont=dict(color=line_colors[i % len(line_colors)], size=10)))
    fig.update_layout(
        title={
            'text': f'Time Series Line Chart for {selected_cell}',
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis_title='Time', 
        yaxis_title='Value',
        template='ggplot2',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    return fig


def update_bar_chart(selected_cell, selected_pis, date_range):
    """Updates the bar chart"""
    resampled_data = resample_data(selected_cell, selected_pis, date_range)
    fig = go.Figure()

    for i, pi in enumerate(selected_pis):
        pi_data = resampled_data[resampled_data['pi'] == pi]
        fig.add_trace(go.Bar(x=pi_data['date_time'], y=pi_data['value'], 
                             name=pi, marker=dict(color=line_colors[i % len(line_colors)]),
                             text=["{:.2f}".format(val) for val in pi_data['value']],
                             textposition='outside',
                             textfont=dict(color=line_colors[i % len(line_colors)], size=10)))
    
    fig.update_layout(
        title=f'Time Series Bar Chart for {selected_cell}', 
        xaxis_title='Time', 
        yaxis_title='Value',
        template='ggplot2',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        bargap=0.1, # change to desired value
        barmode='group'  # bars are placed beside each other
    )
    return fig

def update_scatter_chart(selected_cell, selected_pis, date_range):
    """Updates the scatter chart"""
    resampled_data = resample_data(selected_cell, selected_pis, date_range)
    fig = go.Figure()

    if len(selected_pis) < 2:
        fig.update_layout(title='Scatter Plot', template='ggplot2')
        return fig

    pi_data_x = resampled_data[resampled_data['pi'] == selected_pis[0]]
    pi_data_y = resampled_data[resampled_data['pi'] == selected_pis[1]]

    # Normalize the size data for better visualization
    size = (pi_data_y['value'] - pi_data_y['value'].min()) / (pi_data_y['value'].max() - pi_data_y['value'].min()) * 20

    fig.add_trace(go.Scatter(
        x=pi_data_x['value'], 
        y=pi_data_y['value'], 
        mode='markers',
        name=f'{selected_pis[0]} vs {selected_pis[1]}',
        marker=dict(
            size=size,  # Use normalized size
            color=pi_data_x['value'],  # Use the value of the first PI for color
            colorscale='Viridis',  # Set color scale
            colorbar=dict(title="Value of "+selected_pis[0]),  # Color bar to represent scale
            sizemode='diameter'
        )
    ))

    fig.update_layout(
        title=f'{selected_cell} Scatter Plot of {selected_pis[0]} and {selected_pis[1]}',
        xaxis_title=selected_pis[0],
        yaxis_title=selected_pis[1],
        template='ggplot2'
    )

    return fig

def update_heatmap_chart(selected_cell, selected_pis, date_range):
    """Updates the heatmap chart"""
    resampled_data = resample_data(selected_cell, selected_pis, date_range)
    pivot_table = resampled_data.pivot_table(index='date_time', columns='pi', values='value')
    fig = go.Figure(data=go.Heatmap(z=pivot_table.values, x=pivot_table.columns, y=pivot_table.index))
    fig.update_layout(title=f'{selected_cell} Heatmap', 
                      template='ggplot2')
    return fig

def update_box_plot(selected_cell, selected_pis, date_range):
    """Updates the box plot chart"""
    resampled_data = resample_data(selected_cell, selected_pis, date_range)
    fig = go.Figure()
    for i, pi in enumerate(selected_pis):
        pi_data = resampled_data[resampled_data['pi'] == pi]
        fig.add_trace(go.Box(y=pi_data['value'], name=pi))
    fig.update_layout(title=f'{selected_cell} Box Plot', 
                      yaxis_title='Value', template='ggplot2')
    return fig

def update_histogram_chart(selected_cell, selected_pis, date_range):
    """Updates the histogram chart"""
    resampled_data = resample_data(selected_cell, selected_pis, date_range)

    # Create subplots, using 'domain' type for x-axes
    fig = make_subplots(rows=1, cols=len(selected_pis), subplot_titles=selected_pis, 
                        shared_yaxes=True)

    for i, pi in enumerate(selected_pis):
        pi_data = resampled_data[resampled_data['pi'] == pi]
        fig.add_trace(go.Histogram(x=pi_data['value'], name=pi, nbinsx=20), row=1, col=i+1)
        fig.update_xaxes(title_text='Value', row=1, col=i+1)

    fig.update_layout(title=f'{selected_cell} Histogram for each PI', 
                      yaxis_title='Count', 
                      template='ggplot2')

    return fig

# Dictionary to map tab values to chart functions
chart_func_dict = {
    'tab-line': update_line_chart,
    'tab-bar': update_bar_chart,
    'tab-scatter': update_scatter_chart,
    'tab-heatmap': update_heatmap_chart,
    'tab-box': update_box_plot,
    'tab-hist': update_histogram_chart
}

# Initialize Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

# Define Dash app layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("5G Network Performance Dashboard", className="text-center my-4"),
        ], width=12),
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Control Panel", style={'font-size': '20px'}),
                dbc.CardBody([
                    html.H6("Select cell and performance indicators", className="mb-3"),
                    dcc.Dropdown(
                        id='cell_dropdown',
                        options=[{'label': cell, 'value': cell} for cell in cell_ids],
                        value=cell_ids[0],
                        className="mb-3",
                        multi=True, # allow multiple selection
                        clearable=False,
                        style={'font-size': '18px'}
                    ),

                    dcc.Dropdown(
                        id='pi_dropdown',
                        options=[{'label': pi, 'value': pi} for pi in pis],
                        value=pis[0],
                        multi=True,
                        className="mb-3",
                        clearable=False,
                        style={'font-size': '18px'}
                    ),
                    html.H6("Select time range", className="mb-3"),
                    dcc.DatePickerRange(
                        id='date_picker',
                        min_date_allowed=min_date,
                        max_date_allowed=max_date,
                        start_date=min_date,
                        end_date=max_date,
                        style={'font-size': '18px'}
                    ),
                ]),
            ], className="mb-4"),
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(
                    dcc.Tabs(id="tabs", value='tab-line', children=[
                        dcc.Tab(label='Line Chart', value='tab-line'),
                        dcc.Tab(label='Bar Chart', value='tab-bar'),
                        dcc.Tab(label='Scatter Chart', value='tab-scatter'),
                        dcc.Tab(label='Heatmap', value='tab-heatmap'),
                        dcc.Tab(label='Box Plot', value='tab-box'),
                        dcc.Tab(label='Histogram', value='tab-hist'),
                    ])
                ),
                dbc.CardBody([
                    html.Div(id='tabs-content', 
                            children=dcc.Graph(figure=update_line_chart(cell_ids[0], [pis[0]], (min_date, max_date))))
                ]),

            ]),
        ], width=9),
    ])
], fluid=True, className="p-3")

@app.callback(
    Output('tabs-content', 'children'),
    Input('tabs', 'value'),
    Input('cell_dropdown', 'value'),
    Input('pi_dropdown', 'value'),
    Input('date_picker', 'start_date'),
    Input('date_picker', 'end_date')
)
def render_tab_content(tab, selected_cells, selected_pis, start_date, end_date):
    # Convert date strings to datetime objects
    start_date = pd.to_datetime(start_date).replace(hour=0, minute=0)
    end_date = pd.to_datetime(end_date).replace(hour=23, minute=59)
    # Check if any selected item is None or if selected_pis is an empty list
    if None in (selected_cells, selected_pis, start_date, end_date) or not selected_pis:
        # If yes, return an empty figure
        return [dcc.Graph(figure=go.Figure())]
    else:
        # Ensure selected_cells is a list
        if not isinstance(selected_cells, list):
            selected_cells = [selected_cells]
        # Create a graph for each selected cell
        graphs = [dcc.Graph(figure=chart_func_dict[tab](selected_cell, selected_pis, (start_date, end_date))) for selected_cell in selected_cells]
        return graphs
    
# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)