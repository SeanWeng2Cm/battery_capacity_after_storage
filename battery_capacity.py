import streamlit as st
import numpy as np
import plotly.graph_objects as go

# Title and battery model
battery_model = "YUASA NPW45-12"
nominal_capacity_ah = 7.5  # 45Ah battery
st.title(f"Battery Capacity Retention Over Time — {battery_model}")

# Sidebar Inputs
initial_capacity = st.sidebar.slider("Initial Capacity (%)", 50, 100, 95)
input_months = st.sidebar.number_input("Storage Time (Months)", min_value=0, max_value=120, value=12)
input_days = st.sidebar.number_input("Additional Days", min_value=0, max_value=31, value=0)
input_hours = st.sidebar.number_input("Additional Hours", min_value=0, max_value=23, value=0)
min_temp = st.sidebar.slider("Min Temperature (°C)", -20, 25, -15)
max_temp = st.sidebar.slider("Max Temperature (°C)", 25, 60, 45)
temp_step = st.sidebar.slider("Temperature Step (°C)", 1, 10, 5)

# Constants specific to YUASA NPW45-12
base_temp = 25              # Reference temperature in °C
base_rate = 0.0342          # ~3.42% per month based on 80% remaining after 6 months
Q0 = initial_capacity

# Time Conversion: Total storage time in months
total_months = input_months + (input_days / 30.42) + (input_hours / 24 / 30.42)
x_months = np.arange(0, total_months + 0.1, 0.1)
x_days = x_months * 30.42
x_hours = x_days * 24

# Temperature range
temps = np.arange(min_temp, max_temp + 1, temp_step)
temps_list = [int(t) for t in temps]

# Color palette and map
color_palette = [
    "#636EFA", "#EF553B", "#00CC96", "#AB63FA",
    "#FFA15A", "#19D3F3", "#FF6692", "#B6E880"
]
color_map = {t: color_palette[i % len(color_palette)] for i, t in enumerate(temps_list)}

# Create figure
fig = go.Figure()
curves = {}

for T in temps_list:
    # Arrhenius-based temperature scaling
    k_T = base_rate * 2 ** ((T - base_temp) / 10)
    capacity = Q0 * ((1 - k_T) ** x_months)
    final_capacity = capacity[-1]
    curves[T] = capacity

    # Line curve
    fig.add_trace(go.Scatter(
        x=x_months,
        y=capacity,
        mode='lines',
        name=f"{T}°C — Final: {final_capacity:.1f}%",
        line=dict(color=color_map[T]),
        hovertemplate='Month: %{x:.2f}<br>Capacity: %{y:.2f}%<extra></extra>'
    ))

    # Terminal dot
    fig.add_trace(go.Scatter(
        x=[x_months[-1]],
        y=[final_capacity],
        mode='markers',
        marker=dict(size=8, color=color_map[T]),
        showlegend=False,
        hovertemplate=(f"<b>Temp:</b> {T}°C<br>"
                       f"<b>Month:</b> {x_months[-1]:.2f}<br>"
                       f"<b>Hour:</b> {x_hours[-1]:.0f}<br>"
                       f"<b>Cap:</b> {final_capacity:.2f}%<extra></extra>")
    ))

# Helper: find closest index in the original numpy array
def get_closest_index(array, value):
    return int((np.abs(array - value)).argmin())

highlight_start_idx = get_closest_index(temps, -5)
highlight_end_idx = get_closest_index(temps, 35)

highlight_start = st.sidebar.selectbox(
    "Highlight Start Temp (°C)", temps_list, index=highlight_start_idx
)
highlight_end = st.sidebar.selectbox(
    "Highlight End Temp (°C)", temps_list, index=highlight_end_idx
)

# Highlight range fill
if highlight_start != highlight_end:
    lower_T, upper_T = sorted((highlight_start, highlight_end))
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

# Final layout
fig.update_layout(
    title=f"{battery_model} — Capacity Retention vs. Time & Temperature",
    xaxis_title="Storage Time (Months)",
    yaxis_title="Remaining Capacity (%)",
    hovermode='x unified',
    height=600
)

st.plotly_chart(fig, use_container_width=True)

# === Self-Discharge Current Display ===
st.header("Estimated Self-Discharge Current")
rate_display = base_rate * 100  # %
current_base_a = base_rate * nominal_capacity_ah  # A
current_base_ma = current_base_a * 1000  # mA

st.markdown(f"""
- 📉 **Base self-discharge rate** at 25°C: **{rate_display:.2f}% per month**
- 🔋 **Nominal capacity**: {nominal_capacity_ah} Ah
- 🔌 **Estimated self-discharge current** at 25°C: **{current_base_ma:.0f} mA**
""")
