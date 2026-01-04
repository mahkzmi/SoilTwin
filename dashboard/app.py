import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

from geopy.geocoders import Nominatim
from core.simulator import SoilTwinSimulator
from core.decision_engine import DecisionEngine
from domain.soil import SoilProfile, CropProfile
from core.weather_api import WeatherAPI

# ===== PAGE CONFIG =====
st.set_page_config(
    page_title="Soil Digital Twin | Smart Irrigation",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== MODERN MINIMAL CSS =====
st.markdown("""
<style>
    /* Modern minimal color palette */
    :root {
        --primary: #10B981;
        --primary-light: #D1FAE5;
        --secondary: #3B82F6;
        --accent: #F59E0B;
        --light: #F9FAFB;
        --dark: #111827;
        --gray-50: #F9FAFB;
        --gray-100: #F3F4F6;
        --gray-200: #E5E7EB;
        --gray-300: #D1D5DB;
        --gray-400: #9CA3AF;
        --gray-500: #6B7280;
        --gray-600: #4B5563;
        --gray-700: #374151;
        --gray-800: #1F2937;
        --success: #10B981;
        --warning: #F59E0B;
        --danger: #EF4444;
    }
    
    /* Base reset for cleaner look */
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1.5rem;
        max-width: 100% !important;
    }
    
    /* Clean typography */
    h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        font-weight: 600;
        letter-spacing: -0.025em;
    }
    
    h1 {
        font-size: 2.25rem;
        margin-bottom: 0.5rem;
    }
    
    h2 {
        font-size: 1.5rem;
        margin-bottom: 0.75rem;
    }
    
    h3 {
        font-size: 1.25rem;
        margin-bottom: 0.5rem;
    }
    
    /* Minimal cards */
    .stDataFrame, .stAlert, .stExpander, div[data-testid="stHorizontalBlock"] > div {
        border-radius: 12px;
    }
    
    /* Clean metric styling */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: var(--dark) !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.875rem !important;
        color: var(--gray-500) !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Clean progress bars */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--primary), #059669);
        border-radius: 4px;
    }
    
    /* Minimal tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid var(--gray-200);
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 12px 20px;
        border-radius: 8px 8px 0 0;
        font-weight: 500;
        color: var(--gray-500);
        background: transparent;
        border: none;
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: var(--gray-100);
        color: var(--gray-700);
    }
    
    .stTabs [aria-selected="true"] {
        background: white;
        color: var(--primary);
        border-bottom: 3px solid var(--primary);
    }
    
    /* Clean sidebar */
    section[data-testid="stSidebar"] {
        background: white;
        border-right: 1px solid var(--gray-200);
    }
    
    /* Minimal inputs */
    .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        border: 1px solid var(--gray-300) !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
    }
    
    .stNumberInput input:focus, .stSelectbox div[data-baseweb="select"]:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1) !important;
    }
    
    /* Minimal sliders */
    .stSlider > div {
        padding-top: 0.5rem;
    }
    
    /* Clean buttons */
    .stButton > button {
        background: var(--primary);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background: #059669;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
    }
    
    .stDownloadButton > button {
        background: white;
        color: var(--primary);
        border: 1px solid var(--primary);
    }
    
    .stDownloadButton > button:hover {
        background: var(--primary-light);
    }
    
    /* Status indicators */
    .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 500;
    }
    
    .status-optimal {
        background: #D1FAE5;
        color: #065F46;
    }
    
    .status-moderate {
        background: #FEF3C7;
        color: #92400E;
    }
    
    .status-critical {
        background: #FEE2E2;
        color: #991B1B;
    }
    
    /* Divider */
    hr {
        margin: 2rem 0;
        border: none;
        height: 1px;
        background: var(--gray-200);
    }
    
    /* Minimal data table */
    .dataframe {
        border: 1px solid var(--gray-200) !important;
        border-radius: 8px !important;
    }
    
    /* Clean radio buttons */
    .stRadio > div {
        background: var(--gray-50);
        padding: 12px;
        border-radius: 8px;
        border: 1px solid var(--gray-200);
    }
    
    /* Remove extra padding */
    .css-1d391kg {
        padding-top: 2rem;
    }
    
    /* Chart containers */
    [data-testid="stPlotlyChart"] {
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Subtle animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.3s ease-out;
    }
</style>
""", unsafe_allow_html=True)

# ===== DEFAULT PROFILES =====
SOIL_TYPES = {
    "Loam": SoilProfile(name="Loam", field_capacity_mm=150.0, wilting_point_mm=60.0),
    "Clay": SoilProfile(name="Clay", field_capacity_mm=200.0, wilting_point_mm=80.0),
    "Sand": SoilProfile(name="Sand", field_capacity_mm=100.0, wilting_point_mm=30.0),
}

CROP_TYPES = {
    "Wheat": CropProfile(name="Wheat", kc=1.05),
    "Corn": CropProfile(name="Corn", kc=1.15),
    "Rice": CropProfile(name="Rice", kc=1.20),
    "Tomato": CropProfile(name="Tomato", kc=1.10),
    "Potato": CropProfile(name="Potato", kc=1.00),
}

# ===== MINIMAL SIDEBAR =====
with st.sidebar:
    # Header
    st.markdown("""
    <div style='text-align: center; margin-bottom: 2rem; padding-bottom: 1.5rem; border-bottom: 1px solid #E5E7EB;'>
        <div style='font-size: 2rem; margin-bottom: 0.5rem;'>🌱</div>
        <h3 style='color: #111827; margin-bottom: 0.25rem;'>Soil Digital Twin</h3>
        <p style='color: #6B7280; font-size: 0.875rem; margin: 0;'>Smart Irrigation Simulator</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Configuration
    st.markdown("### Configuration")
    
    col1, col2 = st.columns(2)
    with col1:
        soil_choice = st.selectbox(
            "Soil Type",
            list(SOIL_TYPES.keys()),
            key="soil_select"
        )
    with col2:
        crop_choice = st.selectbox(
            "Crop Type",
            list(CROP_TYPES.keys()),
            key="crop_select"
        )
    
    # Initial Condition
    st.markdown("**Initial Condition**")
    initial_condition = st.radio(
        "",
        ["Dry", "Normal", "Wet"],
        horizontal=True,
        key="initial_condition"
    )
    
    # Location
    st.markdown("**Location**")
    col1, col2 = st.columns(2)
    with col1:
        latitude = st.number_input("Latitude", value=35.6892, format="%.6f", key="lat")
    with col2:
        longitude = st.number_input("Longitude", value=51.3890, format="%.6f", key="lon")
    
    # Simulation Days
    simulation_days = st.slider(
        "Simulation Days",
        3, 30, 10,
        key="sim_days"
    )
    
    # Get region name
    try:
        geolocator = Nominatim(user_agent="soil_dashboard_minimal")
        location = geolocator.reverse(f"{latitude}, {longitude}", language='en')
        region_name = location.raw.get('address', {}).get('city') or \
                     location.raw.get('address', {}).get('town') or \
                     location.raw.get('address', {}).get('village') or "Unknown Region"
    except:
        region_name = "Unknown Region"
    
    st.caption(f"📍 {region_name}")
    
    # Weather Info
    weather = WeatherAPI(latitude=latitude, longitude=longitude, days=simulation_days)
    current_temp = round(weather.current_temperature(), 1)
    current_conditions = weather.current_conditions()
    
    st.markdown("---")
    st.markdown("### Current Weather")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f"<div style='font-size: 2rem; font-weight: 600; color: #F59E0B;'>{current_temp}°C</div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"**{current_conditions}**")
        st.caption(f"Lat: {latitude:.4f}, Lon: {longitude:.4f}")
    
    st.markdown("---")
    st.caption("""
    **How it works:**
    1. Select soil & crop
    2. Set location
    3. Run simulation
    4. View recommendations
    """)

# ===== MAIN DASHBOARD =====
# Clean Header
st.markdown(f"# Smart Irrigation Simulation")
st.markdown(f"""
<div style='display: flex; gap: 1rem; color: #6B7280; font-size: 0.875rem; margin-bottom: 1.5rem;'>
    <span>📍 {region_name}</span>
    <span>•</span>
    <span>🌾 {crop_choice}</span>
    <span>•</span>
    <span>🏞️ {soil_choice}</span>
    <span>•</span>
    <span>📅 {simulation_days} days</span>
    <span style='margin-left: auto;'>{datetime.now().strftime('%b %d, %Y')}</span>
</div>
""", unsafe_allow_html=True)

# ===== SIMULATION EXECUTION =====
# Convert inputs
soil = SOIL_TYPES[soil_choice]
crop = CROP_TYPES[crop_choice]
INITIAL_MOISTURE_MAPPING = {"Dry": 0.4, "Normal": 0.6, "Wet": 0.8}
initial_moisture_mm = soil.field_capacity_mm * INITIAL_MOISTURE_MAPPING[initial_condition]

# Get weather data
weather = WeatherAPI(latitude=latitude, longitude=longitude, days=simulation_days)
et0_daily, rainfall_daily = weather.fetch()

# Initialize simulator
simulator = SoilTwinSimulator(soil=soil, crop=crop, initial_moisture_mm=initial_moisture_mm)
decision_engine = DecisionEngine(threshold_low=0.3, threshold_high=0.6, max_irrigation_mm=15.0)

# Run simulation
st.markdown("### Simulation Progress")
progress_bar = st.progress(0)
status_text = st.empty()

results = []
for day in range(simulation_days):
    progress_bar.progress((day + 1) / simulation_days)
    status_text.text(f"Processing day {day + 1} of {simulation_days}...")
    
    current_stress = max(0.0, min(1.0,
        1 - (simulator.soil_moisture_mm - soil.wilting_point_mm) / (soil.field_capacity_mm - soil.wilting_point_mm)
    ))

    decision = decision_engine.evaluate(
        stress_index=current_stress,
        soil_moisture_mm=simulator.soil_moisture_mm,
        field_capacity_mm=soil.field_capacity_mm
    )

    state = simulator.step(
        et0_mm=et0_daily[day] * crop.kc,
        rainfall_mm=rainfall_daily[day],
        irrigation_mm=decision.irrigation_mm
    )

    results.append({
        "Day": day + 1,
        "Soil Moisture (mm)": round(state.soil_moisture_mm, 1),
        "Stress Index": round(state.stress_index, 3),
        "Memory Factor": round(state.memory_factor, 3),
        "Soil Health Score": round(state.soil_health_score, 2),
        "Irrigation (mm)": decision.irrigation_mm,
        "ET0 (mm)": round(et0_daily[day] * crop.kc, 1),
        "Rainfall (mm)": rainfall_daily[day],
        "Status": "Optimal" if state.stress_index < 0.3 else "Moderate" if state.stress_index < 0.6 else "Critical"
    })

df = pd.DataFrame(results)
status_text.success("✅ Simulation completed")

# ===== KEY METRICS =====
st.markdown("### Key Metrics")

# Calculate metrics
final_moisture = df["Soil Moisture (mm)"].iloc[-1]
final_stress = df["Stress Index"].iloc[-1]
final_health = df["Soil Health Score"].iloc[-1]
total_irrigation = df["Irrigation (mm)"].sum()
total_rainfall = df["Rainfall (mm)"].sum()
total_et0 = df["ET0 (mm)"].sum()

# Display metrics
metric_cols = st.columns(4)
with metric_cols[0]:
    moisture_percent = (final_moisture / soil.field_capacity_mm) * 100
    st.metric(
        "Soil Moisture",
        f"{final_moisture:.1f} mm",
        f"{moisture_percent:.0f}% of capacity"
    )
    st.progress(min(moisture_percent / 100, 1.0))

with metric_cols[1]:
    # Determine stress level
    if final_stress < 0.3:
        stress_label = "Low"
        delta_color = "normal"
    elif final_stress < 0.6:
        stress_label = "Moderate"
        delta_color = "off"
    else:
        stress_label = "High"
        delta_color = "inverse"
    
    st.metric(
        "Stress Level",
        stress_label,
        f"Index: {final_stress:.3f}",
        delta_color=delta_color
    )

with metric_cols[2]:
    if final_health >= 80:
        health_status = "Excellent"
    elif final_health >= 60:
        health_status = "Good"
    else:
        health_status = "Needs Attention"
    
    st.metric(
        "Soil Health",
        f"{final_health:.1f}",
        health_status
    )

with metric_cols[3]:
    net_water = total_rainfall + total_irrigation - total_et0
    delta = f"+{net_water:.1f} mm" if net_water > 0 else f"{net_water:.1f} mm"
    delta_color = "normal" if net_water > 0 else "inverse"
    
    st.metric(
        "Water Balance",
        f"{total_irrigation:.1f} mm",
        delta,
        delta_color=delta_color
    )
    st.caption(f"Rain: {total_rainfall:.1f} mm | ET0: {total_et0:.1f} mm")

# ===== VISUALIZATION SECTION =====
st.markdown("### Analysis")

# Create tabs
tab1, tab2, tab3 = st.tabs(["Soil Dynamics", "Daily Data", "Recommendations"])

with tab1:
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Create plot
        fig = go.Figure()
        
        # Add soil moisture line
        fig.add_trace(go.Scatter(
            x=df["Day"],
            y=df["Soil Moisture (mm)"],
            name="Soil Moisture",
            line=dict(color="#10B981", width=3),
            mode="lines",
            hovertemplate="Day %{x}<br>%{y:.1f} mm<extra></extra>"
        ))
        
        # Add irrigation bars
        irrigation_df = df[df["Irrigation (mm)"] > 0]
        if not irrigation_df.empty:
            fig.add_trace(go.Bar(
                x=irrigation_df["Day"],
                y=irrigation_df["Irrigation (mm)"],
                name="Irrigation",
                marker_color="#3B82F6",
                opacity=0.8,
                hovertemplate="Day %{x}<br>Irrigation: %{y:.1f} mm<extra></extra>"
            ))
        
        # Add stress index
        fig.add_trace(go.Scatter(
            x=df["Day"],
            y=df["Stress Index"],
            name="Stress Index",
            line=dict(color="#F59E0B", width=2, dash="dash"),
            yaxis="y2",
            hovertemplate="Day %{x}<br>Stress: %{y:.3f}<extra></extra>"
        ))
        
        # Update layout
        fig.update_layout(
            height=400,
            plot_bgcolor="white",
            paper_bgcolor="white",
            hovermode="x unified",
            xaxis=dict(
                title="Day",
                gridcolor="#E5E7EB",
                showline=True,
                linecolor="#D1D5DB"
            ),
            yaxis=dict(
                title="Moisture/Irrigation (mm)",
                gridcolor="#E5E7EB",
                showline=True,
                linecolor="#D1D5DB"
            ),
            yaxis2=dict(
                title="Stress Index",
                overlaying="y",
                side="right",
                range=[0, 1],
                gridcolor="#E5E7EB"
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(t=30, b=60)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**Summary**")
        
        irrigation_days = len(df[df["Irrigation (mm)"] > 0])
        high_stress_days = len(df[df["Stress Index"] >= 0.6])
        
        st.metric("Irrigation Days", irrigation_days)
        st.metric("High Stress Days", high_stress_days)
        
        st.markdown("---")
        st.markdown("**Averages**")
        st.markdown(f"Moisture: {df['Soil Moisture (mm)'].mean():.1f} mm")
        st.markdown(f"Stress: {df['Stress Index'].mean():.3f}")
        
        if irrigation_days > 0:
            efficiency = (df["Soil Health Score"].mean() / total_irrigation) * 100 if total_irrigation > 0 else 0
            st.markdown(f"Efficiency: {efficiency:.1f}")

with tab2:
    # Format dataframe
    display_df = df.copy()
    
    # Color function for status
    def color_status(val):
        if val == "Optimal":
            return "background-color: #D1FAE5; color: #065F46;"
        elif val == "Moderate":
            return "background-color: #FEF3C7; color: #92400E;"
        else:
            return "background-color: #FEE2E2; color: #991B1B;"
    
    # Apply styling
    styled_df = display_df.style.applymap(color_status, subset=['Status'])
    
    st.dataframe(
        styled_df,
        use_container_width=True,
        height=400
    )
    
    # Export options
    col1, col2 = st.columns(2)
    with col1:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"soil_simulation_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    with col2:
        if st.button("Generate Report", use_container_width=True):
            st.success("Report will be available shortly")

with tab3:
    # Analyze irrigation patterns
    irrigation_days = df[df["Irrigation (mm)"] > 0]
    
    if not irrigation_days.empty:
        # Calculate pattern
        days_between = []
        prev_day = irrigation_days["Day"].iloc[0]
        for day in irrigation_days["Day"].iloc[1:]:
            days_between.append(day - prev_day)
            prev_day = day
        
        if days_between:
            avg_interval = sum(days_between) / len(days_between)
            st.markdown("**Recommended Schedule**")
            st.markdown(f"Irrigate every **{avg_interval:.1f} days**")
            st.markdown(f"Average dose: **{irrigation_days['Irrigation (mm)'].mean():.1f} mm**")
        
        # Next irrigation
        last_irrigation_day = irrigation_days["Day"].iloc[-1]
        next_irrigation = last_irrigation_day + avg_interval if 'avg_interval' in locals() else last_irrigation_day + 3
        
        st.markdown("---")
        st.markdown(f"**Next irrigation:** Day {int(next_irrigation)}")
        
        st.markdown("---")
        st.markdown("**Water Saving Tips**")
        tips = [
            "🌅 Irrigate early morning",
            "📱 Use soil moisture sensors",
            "🌧️ Check rainfall forecasts",
            "💧 Consider drip irrigation",
            "🌱 Apply mulch for retention"
        ]
        
        for tip in tips:
            st.markdown(f"• {tip}")
    else:
        st.markdown("**No irrigation needed**")
        st.markdown("Soil moisture levels are adequate with natural rainfall.")
    
    # High stress alerts
    high_stress = df[df["Stress Index"] >= 0.6]
    if not high_stress.empty:
        st.markdown("---")
        st.markdown("⚠️ **Attention Required**")
        st.markdown(f"High stress on {len(high_stress)} days")
        stress_days = ", ".join([str(d) for d in high_stress["Day"].tolist()])
        st.caption(f"Days: {stress_days}")

# ===== WATER BALANCE =====
st.markdown("### Water Balance")

col1, col2 = st.columns([2, 1])
with col1:
    # Water balance chart
    water_data = pd.DataFrame({
        "Category": ["Rainfall", "Irrigation", "ET0"],
        "Amount (mm)": [total_rainfall, total_irrigation, total_et0],
        "Type": ["Input", "Input", "Output"]
    })
    
    chart = alt.Chart(water_data).mark_bar().encode(
        x=alt.X("Category:N", title="", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("Amount (mm):Q", title="mm"),
        color=alt.Color("Type:N", 
            scale=alt.Scale(
                domain=["Input", "Output"],
                range=["#10B981", "#F59E0B"]
            ),
            legend=None
        ),
        tooltip=["Category", "Amount (mm)"]
    ).properties(height=250)
    
    st.altair_chart(chart, use_container_width=True)
    
    # Net water
    net_water = total_rainfall + total_irrigation - total_et0
    if net_water > 0:
        st.success(f"Water surplus: +{net_water:.1f} mm")
    else:
        st.error(f"Water deficit: {net_water:.1f} mm")

with col2:
    # Performance metrics
    st.markdown("**Performance**")
    
    moisture_range = df["Soil Moisture (mm)"].max() - df["Soil Moisture (mm)"].min()
    stability_score = 100 - (moisture_range / soil.field_capacity_mm * 100)
    
    cols = st.columns(2)
    with cols[0]:
        st.metric("Stability", f"{stability_score:.0f}%")
    with cols[1]:
        stress_free = len(df[df["Stress Index"] < 0.3])
        st.metric("Stress-Free", f"{stress_free}/{simulation_days}")
    
    st.markdown("---")
    
    health_change = final_health - df["Soil Health Score"].iloc[0]
    if health_change > 0:
        st.metric("Health Change", f"+{health_change:.1f}")
    else:
        st.metric("Health Change", f"{health_change:.1f}")

# ===== FOOTER =====
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6B7280; font-size: 0.875rem; padding: 1rem;'>
    🌱 Soil Digital Twin • Smart Irrigation • v2.5.1
</div>
""", unsafe_allow_html=True)