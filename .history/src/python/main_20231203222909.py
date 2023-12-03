import pandas as pd
import numpy as np
import random
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
import nolds
import base64


def draw(content):
    # Set plotly default renderer to browser
    pio.renderers.default = 'browser'

    # Set plotly default template
    pio.templates.default = "simple_white"

    exams_per_day = 20  # radiologist mean throughput
    scans_per_day = 21  # MRI mean throughput
    forecast = pd.read_csv(StringIO(content))
    forecast = forecast.sort_values(by=['ds'])

    forecast_period = forecast[(forecast['ds'] >= forecast['ds'][151:].min()) & (
            forecast['ds'] <= forecast['ds'][151:].max())]


    # Forecast accuracy metrics
    def mean_absolute_percentage_error(y_true, y_pred):
        y_true, y_pred = np.array(y_true), np.array(y_pred)
        return np.mean(np.abs((y_true - y_pred) / y_true)) * 100


    def root_mean_squared_error(y_true, y_pred):
        y_true, y_pred = np.array(y_true), np.array(y_pred)
        return np.sqrt(np.mean((y_true - y_pred) ** 2))


    def calculate_sample_entropy(time_series, emb_dim=2, tolerance=None):
        if tolerance is None:
            tolerance = np.std(time_series)
        return nolds.sampen(time_series, emb_dim, tolerance)


    hist_data = forecast[:151]
    mape = mean_absolute_percentage_error(hist_data['y'], hist_data['yhat1'])
    rmse = root_mean_squared_error(hist_data['y'], hist_data['yhat1'])
    hist_time_series = hist_data['y'].values
    sample_entropy = calculate_sample_entropy(hist_time_series)

    # Combine charts as subplots
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    hist_data = forecast[:151]
    forecast_data = forecast[151:]

    fig = make_subplots(rows=4, cols=1, shared_xaxes=False,
                        vertical_spacing=0.08, row_heights=[0.62, 0.09, 0.09, 0.2])

    y_min = min(hist_data['y'].min(), forecast_data['yhat1'].min()) / exams_per_day
    y_max = max(hist_data['y'].max(), forecast_data['yhat1'].max()) / exams_per_day
    y_range = [0.9 * y_min, 1.1 * y_max]
    fig.update_yaxes(title_text="FTEs", secondary_y=False,
                    range=y_range, showgrid=True)
    fig.update_xaxes(title_text="")
    fig.update_yaxes(title_text="%", secondary_y=False,
                    range=y_range, showgrid=True)
    fig.update_xaxes(title_text="")

    # Add line chart for main time series
    fig.add_trace(
        go.Scatter(x=forecast['ds'], y=forecast['y'], name='Actuals',
                mode='lines+markers', marker=dict(color='#00a2ed', size=10),
                line=dict(color='#00a2ed', width=3),
                hoverlabel=dict(font=dict(size=15))),  # Add this line
        row=1, col=1,
    )

    fig.add_trace(
        go.Scatter(x=forecast_period['ds'], y=forecast_period['yhat1'], name='Forecast',
                line=dict(color='darkorange', width=3),
                hoverlabel=dict(font=dict(size=15))),
        row=1, col=1
    )
    forecast_period = forecast_period.sort_values(by=['ds'])
    fig.add_trace(
        go.Scatter(
            x=forecast_period['ds'].tolist() + forecast_period['ds'][::-1].tolist(),
            y=forecast_period['yhat1 95.0%'].tolist(
            ) + forecast_period['yhat1 5.0%'][::-1].tolist(),
            fill='toself', fillcolor='rgba(173, 216, 230, 0.5)', line=dict(color='lightblue', width=1), showlegend=True,
            name='Range of possible outcomes',
            mode='lines'),
        row=1, col=1
    )

    fig.update_xaxes(range=[hist_data['ds'].min(),
                            forecast_period['ds'].max()], row=1, col=1)

    fig.update_yaxes(title_text="Volume", showgrid=True,
                    range=[forecast['y'].min() * 0.9, forecast_period['yhat1'].max() * 1.1],
                    row=1, col=1)
    fig.update_xaxes(showgrid=False, row=1, col=1)

    error_annotation_text = f"Forecast Accuracy Metrics: MAPE: {mape:.2f}% | RMSE: {rmse:.2f}"

    # Add bar chart for human resources
    hist_data = forecast[:151]
    forecast_data = forecast[151:]

    fig.add_trace(
        go.Bar(x=hist_data['ds'], y=forecast['y'] / exams_per_day,
            name='Actuals', marker_color='#00a2ed', showlegend=False,
            hoverlabel=dict(font=dict(size=15))),
        row=2, col=1
    )

    fig.add_trace(
        go.Bar(
            x=forecast_data['ds'],
            y=forecast_data['yhat1'] / exams_per_day,
            name='Forecast',
            marker_color='darkorange',
            showlegend=False,
            hoverlabel=dict(font=dict(size=15)),
        ),
        row=2, col=1
    )

    # Add bar chart for equipment utilisation
    hist_data = forecast[:151]
    forecast_data = forecast[151:]

    utilization_data = forecast_data['yhat1'] / scans_per_day * 100
    y_min = utilization_data.min() * 0.5
    y_max = utilization_data.max() * 1.2

    fig.add_trace(
        go.Bar(x=hist_data['ds'], y=forecast['y'] / scans_per_day * 100,
            name='Actuals', marker_color='#00a2ed', showlegend=False, hoverlabel=dict(font=dict(size=15))),
        row=3, col=1
    )

    fig.add_trace(
        go.Bar(
            x=forecast_data['ds'],
            y=forecast_data['yhat1'] / scans_per_day * 100,
            name='Forecast',
            marker_color='darkorange',
            showlegend=False,
            hoverlabel=dict(font=dict(size=15)),
        ),
        row=3, col=1
    )

    fig.add_trace(
        go.Scatter(x=[forecast['ds'].min(), forecast['ds'].max()], y=[100, 100],
                mode='lines', line=dict(color='red', width=1), showlegend=False),
        row=3, col=1
    )

    # Constants for heatmap
    avg_daily_volume = 21
    avg_weekend_volume = 10
    busy_period_scale_factor = 1.25

    days = ['Mon', 'Tue', 'Wed',
            'Thu', 'Fri', 'Sat', 'Sun']
    hours = [f'{h:02d}00' for h in range(7, 18)]

    # Generating data
    np.random.seed(42)
    data = np.zeros((len(days), len(hours)))

    for i, day in enumerate(days):
        scale_factor = 1.1 if day in ['Mon', 'Wed'] else (
                avg_weekend_volume / avg_daily_volume) if day in ['Sat', 'Sun'] else 1

        for j, hour in enumerate(hours):
            is_weekend = day in ['Sat', 'Sun']
            is_busy_hour = hour in ['1000', '1100', '1300', '1400']

            if is_weekend and hour not in ['0700', '0800', '0900', '1000', '1100', '1200', '1300']:
                data[i, j] = 0
            else:
                base_demand = scale_factor * avg_daily_volume / \
                            (len(hours[:7]) if is_weekend else len(hours))
                demand_multiplier = busy_period_scale_factor if is_busy_hour else 1
                data[i, j] = base_demand * demand_multiplier * \
                            (1 + random.uniform(-0.1, 0.1))

    # Define the custom color scale
    custom_colors = [
        (0., 'purple'),
        (0.33, '#00a2ed'),
        (0.66, '#bada55'),
        (1.0, '#ffffff')]

    heatmap = go.Heatmap(
        z=data,
        x=hours,
        y=days,
        colorscale=custom_colors,
        reversescale=True,
        zmin=0,
        zmax=data.max(),
        colorbar=dict(
            ticklen=2.5,
            thickness=15,
            len=0.173,
            y=0.075,
            x=1.0,
            xanchor='left',
        ),
        hovertemplate='Hourly Demand: %{z:.2f}<extra></extra>',
        hoverlabel=dict(bgcolor='darkorange', font=dict(size=15)),
        name="Demand"
    )

    fig.add_trace(heatmap, row=4, col=1)

    fig.update_yaxes(title_text="", autorange='reversed', row=4, col=1)
    fig.update_xaxes(title_text="", row=4, col=1)

    # Update axes and titles
    page_height = 1110
    page_width = 2050

    # Update axes and titles
    fig.update_yaxes(title_text="FTEs", secondary_y=False,
                    range=y_range, showgrid=True, row=2, col=1)
    fig.update_xaxes(title_text="", row=2, col=1)

    fig.update_yaxes(title_text="%", secondary_y=False, range=[
        y_min, y_max], showgrid=True, row=3, col=1)
    fig.update_xaxes(title_text="", row=3, col=1)

    fig.update_layout(
        title="Time Series Viewer: Procedure Volume (MRI) - Harley Street Medical Imaging",
        font=dict(family="Helvetica Light", size=14, color="black"),
        legend=dict(
            orientation="h", yanchor="top", y=1.05, xanchor="right", x=1
        ),
        title_x=0.195,
        title_y=0.96,
        annotations=[
            dict(
                text="Staffing Requirements: Radiologists (MRI)",
                x=0,
                y=0.47,
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(family="Helvetica Light", size=18, color="black"),
            ),
            dict(
                text="Equipment Utilisation: MRI",
                x=0,
                y=0.3,
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(family="Helvetica Light", size=18, color="black"),
            ),
            dict(
                text="MRI Demand by Hour and Day of the Week",
                x=0,
                y=0.16,
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(family="Helvetica Light", size=18, color="black"),
            ),
            dict(
                text=error_annotation_text,
                x=0.99,
                y=1.02,
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(family="Helvetica Light", size=16, color="black"),
            ),
        ],

        margin=dict(t=80, l=400, r=5, b=5),
        height=page_height,
        width=page_width,
    )

    fig.update_layout(hovermode='x')

    #image_bytes = pio.to_image(fig, format='png', width=800, height=600)
    # Encode the image as base64
    #image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png')
    buffer.seek(0)
    # Encode the image as base64
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    return image_base64
draw