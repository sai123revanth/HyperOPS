import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import textwrap # Essential for fixing HTML indentation issues

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Ecopay | Policy & Macro Alignment",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Shared "Eco-FinTech" Design System
st.markdown("""
<style>
    /* Global App Styling */
    .stApp {
        background: linear-gradient(160deg, #02040a 0%, #062c1b 45%, #0d5c3b 100%);
        background-attachment: fixed;
        color: #fafafa;
    }
    
    /* Headers */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        color: white;
    }
    
    h1 {
        font-size: 2.5rem;
        font-weight: 800;
        letter-spacing: -1px;
    }

    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
        transition: transform 0.3s ease;
    }
    .glass-card:hover {
        border-color: #00d26a;
        transform: translateY(-2px);
    }

    /* Highlight Metric Box */
    .metric-highlight {
        text-align: center;
        padding: 10px;
        border-radius: 12px;
        background: rgba(220, 53, 69, 0.15); /* Red tint for alert */
        border: 1px solid #dc3545;
        margin-bottom: 20px;
    }
    .metric-highlight.safe {
        background: rgba(25, 135, 84, 0.15); /* Green tint for safe */
        border: 1px solid #198754;
    }
    
    .big-number {
        font-size: 3rem;
        font-weight: 800;
        color: white;
        text-shadow: 0 0 10px rgba(255,255,255,0.2);
    }
    
    .sub-text {
        color: #b0b8c3;
        font-size: 1rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Policy Badges */
    .policy-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        background: rgba(13, 202, 240, 0.2);
        color: #3dd5f3;
        border: 1px solid #0dcaf0;
        margin-right: 8px;
    }

    /* Override Streamlit Metrics */
    div[data-testid="stMetric"] {
        background: rgba(17, 24, 39, 0.6);
        border: 1px solid rgba(255,255,255,0.1);
        padding: 15px;
        border-radius: 10px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. DATA & SCIENCE LOGIC
# -----------------------------------------------------------------------------

# Scientific Constants (Tons CO2e per capita per year)
GLOBAL_AVG = 4.7
TARGET_2030 = 2.3  # Required for 1.5°C pathway
TARGET_2050 = 0.7  # Net Zero requirement
EARTH_CAPACITY = 1.6 # Sustainable capacity per person

@st.cache_data
def calculate_alignment_metrics():
    """
    Simulates user footprint calculation based on financial data proxy.
    In a real app, this integrates with the Engine module.
    """
    # Simulate loading data
    try:
        df = pd.read_csv("Daily Household Transactions.csv")
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
        df = df[df['Income/Expense'] == 'Expense']
        total_spend = df['Amount'].sum()
        
        # Annualization Logic (Assuming data might not be exactly 1 year)
        # For demo, we treat the dataset total as "Year To Date" or estimate annual run rate
        # Using a simplistic intensity factor (0.12 kg/INR - slightly higher for 'Business As Usual' scenario)
        current_annual_footprint_kg = total_spend * 0.12
        current_annual_footprint_tons = current_annual_footprint_kg / 1000
        
        # Safety fallback if data is too small
        if current_annual_footprint_tons < 1: 
            current_annual_footprint_tons = 4.2 # Default to near average
            
    except:
        current_annual_footprint_tons = 4.2 # Fallback
        
    # Alignment Multiplier
    multiplier = current_annual_footprint_tons / TARGET_2030
    
    return current_annual_footprint_tons, multiplier

# -----------------------------------------------------------------------------
# 3. VISUALIZATION FUNCTIONS
# -----------------------------------------------------------------------------

def plot_paris_gauge(current_val):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = current_val,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Annual Footprint (Tons CO₂e)", 'font': {'size': 18, 'color': 'white'}},
        delta = {'reference': TARGET_2030, 'increasing': {'color': "#dc3545"}, 'decreasing': {'color': "#198754"}},
        gauge = {
            'axis': {'range': [None, 10], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': "#00d26a" if current_val <= TARGET_2030 else "#dc3545"},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 2,
            'bordercolor': "rgba(255,255,255,0.1)",
            'steps': [
                {'range': [0, TARGET_2050], 'color': 'rgba(25, 135, 84, 0.5)'}, # Net Zero
                {'range': [TARGET_2050, TARGET_2030], 'color': 'rgba(255, 193, 7, 0.5)'}, # 2030 Target
                {'range': [TARGET_2030, 10], 'color': 'rgba(220, 53, 69, 0.3)'} # Unsustainable
            ],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': TARGET_2030
            }
        }
    ))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"}, height=300, margin=dict(l=20,r=20,t=50,b=20))
    return fig

def plot_net_zero_pathway(current_val):
    years = list(range(2024, 2051))
    
    # Business As Usual (BAU) - Flat or slight increase
    bau = [current_val * (1.01 ** (y - 2024)) for y in years]
    
    # Paris 1.5C Pathway (Exponential decay to 0.7 by 2050)
    decay_rate = np.log(TARGET_2050 / current_val) / (2050 - 2024)
    paris_path = [current_val * np.exp(decay_rate * (y - 2024)) for y in years]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=years, y=bau, name='Business As Usual', line=dict(color='#dc3545', width=2, dash='dot')))
    fig.add_trace(go.Scatter(x=years, y=paris_path, name='Net-Zero Aligned', line=dict(color='#00d26a', width=4)))
    
    # Add constraint line
    fig.add_hline(y=TARGET_2030, line_dash="dash", line_color="#ffc107", annotation_text="2030 Limit", annotation_position="top right")
    fig.add_hline(y=TARGET_2050, line_dash="solid", line_color="#0dcaf0", annotation_text="2050 Net Zero", annotation_position="bottom right")

    fig.update_layout(
        title="Your Trajectory vs. Global Targets",
        xaxis_title="Year",
        yaxis_title="Carbon Intensity (Tons/Year)",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.05)",
        font=dict(color="white"),
        hovermode="x unified",
        height=350,
        legend=dict(orientation="h", y=1.1)
    )
    return fig

# -----------------------------------------------------------------------------
# 4. MAIN APPLICATION
# -----------------------------------------------------------------------------

def main():
    # Load Data
    user_footprint, multiplier = calculate_alignment_metrics()
    is_safe = user_footprint <= TARGET_2030
    
    # --- HEADER ---
    st.title("Policy Alignment & Macro Relevance")
    st.markdown("""
    Align your personal financial footprint with international climate accords. 
    Compare your consumption patterns against the **Paris Agreement (1.5°C)** and **Net-Zero 2050** pathways.
    """)
    st.markdown("---")

    # --- HERO SECTION: THE METRIC ---
    hero_col1, hero_col2 = st.columns([1, 2])
    
    with hero_col1:
        # Dynamic Class for styling
        alert_class = "safe" if is_safe else "alert"
        alert_color = "#00d26a" if is_safe else "#ff4b4b"
        
        # FIX: textwrap.dedent ensures proper HTML rendering by removing indentation
        st.markdown(textwrap.dedent(f"""
        <div class="glass-card">
            <h3 style="margin-top:0;">🌍 Planetary Status</h3>
            <div class="metric-highlight {alert_class}">
                <div class="big-number">{multiplier:.1f}x</div>
                <div class="sub-text">Above Sustainable Levels</div>
            </div>
            <p style="color:#e0e0e0; font-size:0.9rem;">
                Your current lifestyle requires <b>{multiplier:.1f} Earths</b> if everyone lived like you. 
                You are exceeding the <span style="color:#ffc107">2030 Carbon Budget</span>.
            </p>
        </div>
        """), unsafe_allow_html=True)
        
    with hero_col2:
        # FIX: textwrap.dedent ensures proper HTML rendering
        st.markdown(textwrap.dedent(f"""
        <div class="glass-card">
            <h3 style="margin-top:0;">📊 Strategic Analysis</h3>
            <p>To align with the <b>Paris Agreement</b>, your annual emissions must drop below <b>{TARGET_2030} tons</b> by 2030.</p>
            <div style="margin-top: 15px;">
                <span class="policy-badge">📜 Paris Agreement Art. 2</span>
                <span class="policy-badge">🇺🇳 UN SDG 13</span>
                <span class="policy-badge">📉 IPCC AR6 Report</span>
            </div>
        </div>
        """), unsafe_allow_html=True)
        
        # Key Comparison Metrics
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Your Footprint", f"{user_footprint:.1f} t", delta=f"{user_footprint - TARGET_2030:.1f} t excess", delta_color="inverse")
        with m2:
            st.metric("Global Average", f"{GLOBAL_AVG:.1f} t", delta=f"{user_footprint - GLOBAL_AVG:.1f} t vs avg", delta_color="inverse")
        with m3:
            st.metric("2030 Target", f"{TARGET_2030:.1f} t", help="Per capita limit to restrict warming to 1.5C")

    # --- VISUALIZATION SECTION ---
    st.markdown("<br>", unsafe_allow_html=True)
    
    viz_c1, viz_c2 = st.columns([1, 2])
    
    with viz_c1:
        st.markdown("### 🌡️ Carbon Gauge")
        st.plotly_chart(plot_paris_gauge(user_footprint), use_container_width=True)
        
    with viz_c2:
        st.markdown("### 📉 Decarbonization Pathway")
        st.plotly_chart(plot_net_zero_pathway(user_footprint), use_container_width=True)

    # --- SIMULATION & ACTION SECTION ---
    st.markdown("---")
    st.subheader("🛠️ Policy Impact Simulator")
    st.markdown("See how adopting specific high-impact policies adjusts your alignment score.")

    sim_col1, sim_col2 = st.columns([1, 2])

    with sim_col1:
        with st.container():
            st.markdown("#### Adopt Personal Policies")
            p_energy = st.checkbox("⚡ Switch to 100% Renewable Energy (-1.2t)")
            p_transport = st.checkbox("🚆 Public Transport / EV Only (-1.5t)")
            p_diet = st.checkbox("🥗 Plant-Based Diet (-0.8t)")
            p_circular = st.checkbox("♻️ Circular Economy (Second-hand) (-0.5t)")

    with sim_col2:
        # Calculate Simulated Footprint
        simulated_footprint = user_footprint
        if p_energy: simulated_footprint -= 1.2
        if p_transport: simulated_footprint -= 1.5
        if p_diet: simulated_footprint -= 0.8
        if p_circular: simulated_footprint -= 0.5
        
        # Clamp to 0
        simulated_footprint = max(0.5, simulated_footprint)
        sim_multiplier = simulated_footprint / TARGET_2030
        
        # Progress Bar Logic
        progress_val = min(1.0, simulated_footprint / user_footprint)
        
        # FIX: textwrap.dedent ensures proper HTML rendering
        st.markdown(textwrap.dedent(f"""
        <div style="background:rgba(255,255,255,0.05); padding:20px; border-radius:12px; border:1px solid rgba(255,255,255,0.1);">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h3>Projected Alignment</h3>
                <h2 style="color: {'#00d26a' if sim_multiplier <= 1 else '#ffc107'}; margin:0;">{sim_multiplier:.1f}x</h2>
            </div>
            <p style="color:#aaa;">New Annual Footprint: <b>{simulated_footprint:.1f} tons</b></p>
            
            <div style="background:#333; height:10px; border-radius:5px; overflow:hidden; margin-top:10px;">
                <div style="background:linear-gradient(90deg, #00d26a, #00b359); width:{progress_val*100}%; height:100%;"></div>
            </div>
            <p style="text-align:right; font-size:0.8rem; margin-top:5px; color:#00d26a;">
                Total Reduction: {(user_footprint - simulated_footprint):.1f} tons
            </p>
        </div>
        """), unsafe_allow_html=True)
        
        if sim_multiplier <= 1.0:
            st.success("✅ **Success:** This policy mix aligns you with the 2030 Paris Agreement targets!")
        elif sim_multiplier < 1.5:
            st.warning("⚠️ **Close:** You are approaching sustainable levels, but more aggressive action is needed.")
        else:
            st.error("❌ **Gap:** Significant structural changes are still required to reach alignment.")

    # --- FOOTER ---
    st.markdown("<br><br><br>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()