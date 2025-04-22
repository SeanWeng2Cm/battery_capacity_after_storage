import streamlit as st
import numpy as np
import plotly.graph_objects as go

# Title
st.title("Battery Capacity Retention Over Time")

# Sidebar Inputs
initial_capacity = st.sidebar.slider("Initial Capacity (%)", 50, 100, 100)
input_months = st.sidebar.number_input("Storage Time (Months)", min_value=0, max_value=120, value=1)
input_days = st.sidebar.number_input("Additional Days", min_value=0, max_value=31, value=0)
input_hours = st.sidebar.number_input("Additional Hours", min_value=0, max_value=23, value=0)
min_temp = st.sidebar.slider("Min Temperature (°C)", -20, 25, -15)
max_temp = st.sidebar.slider("Max Temperature (°C)", 25, 60, 40)
temp_step = st.sidebar.slider("Temperature Step (°C)", 1, 10, 5)

# Constants
base_temp = 25
base_rate = 0.03  # 3% per month at 25°C
Q0 = initial_capacity

# Time Conversion: Total storage time in months
total_months = input_months + (input_days / 30.42) + (input_hours / 24 / 30.42)
x_months = np.arange(0, total_months + 0.1, 0.1)
x_days = x_months * 30.42
x_hours = x_days * 24

# Temperature range
temps = np.arange(min_temp, max_temp + 1, temp_step)

# Color palette and map
color_palette = ["#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#FFA15A", "#19D3F3", "#FF6692", "#B6E880"]
color_map = {temp: color_palette[i % len(color_palette)] for i, temp in enumerate(temps)}

# Create figure
fig = go.Figure()
curves = {}

for T in temps:
    k_T = base_rate * 2 ** ((T - base_temp) / 10)
    capacity = Q0 * ((1 - k_T) ** x_months)
    color = color_map[T]
    final_capacity = capacity[-1]
    curves[T] = capacity

    # Line curve
    fig.add_trace(go.Scatter(
        x=x_months,
        y=capacity,
        mode='lines',
        name=f"{T}°C — Final: {final_capacity:.1f}%",
        line=dict(color=color),
        hovertemplate='Month: %{x:.2f}<br>Capacity: %{y:.2f}%<extra></extra>'
    ))

    # Terminal dot (no value label)
    fig.add_trace(go.Scatter(
        x=[x_months[-1]],
        y=[final_capacity],
        mode='markers',
        marker=dict(size=8, color=color),
        showlegend=False,
        hovertemplate=f"<b>Temp:</b> {T}°C<br><b>Month:</b> {x_months[-1]:.2f}<br><b>Hour:</b> {x_hours[-1]:.0f}<br><b>Cap:</b> {final_capacity:.2f}%<extra></extra>"
    ))

# Highlight selection
highlight_start = st.sidebar.selectbox("Highlight Start Temp (°C)", temps, index=0)
highlight_end = st.sidebar.selectbox("Highlight End Temp (°C)", temps, index=min(1, len(temps)-1))

if highlight_start != highlight_end:
    lower_T = min(highlight_start, highlight_end)
    upper_T = max(highlight_start, highlight_end)
    y_lower = curves[lower_T]
    y_upper = curves[upper_T]

    fig.add_trace(go.Scatter(
        x=np.concatenate([x_months, x_months[::-1]]),
        y=np.concatenate([y_upper, y_lower[::-1]]),
        fill='toself',
        fillcolor='rgba(255, 215, 0, 0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo='skip',
        showlegend=False
    ))

# Layout
fig.update_layout(
    title="Battery Capacity Retention Over Time",
    xaxis_title="Storage Time (Months)",
    yaxis_title="Remaining Capacity (%)",
    hovermode='x unified',
    height=600
)

# Show plot
st.plotly_chart(fig, use_container_width=True)
