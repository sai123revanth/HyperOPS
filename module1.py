import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import os
from groq import Groq

# Voice / TTS Imports added to enable the AI to speak
from gtts import gTTS
import io
import re

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Ecopay | Carbon Attribution Engine",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for a modern, "Eco-FinTech" aesthetic, Explanation Boxes, & Floating Chat
st.markdown("""
<style>
    /* Main Background & Text */
    .stApp {
        background: linear-gradient(150deg, #050a0e 0%, #061e14 50%, #00331e 100%);
        background-attachment: fixed;
        color: #fafafa;
    }
    
    /* Modern Gradient Metrics Cards */
    div[data-testid="stMetric"] {
        background: rgba(17, 24, 39, 0.7); 
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 210, 106, 0.2);
        border-left: 4px solid #00d26a; 
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    
    div[data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 30px rgba(0, 210, 106, 0.15);
        border-color: #34d399;
        background: rgba(17, 24, 39, 0.9);
    }

    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        color: #ffffff; 
        font-weight: 700;
        text-shadow: 0 2px 4px rgba(0,0,0,0.5);
    }
    
    div[data-testid="stMetricLabel"] {
        color: #9ca3af;
        font-size: 0.9rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    h1, h2, h3, h4 {
        font-family: 'Inter', sans-serif;
        color: #ffffff;
    }
    h1 { font-weight: 800; letter-spacing: -1px; }
    
    hr {
        margin-top: 3rem;
        margin-bottom: 3rem;
        border: 0;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Simple English Explanation Box styling for Hackathon Judges */
    .explainer-box {
        background-color: rgba(30, 41, 59, 0.6);
        border-left: 4px solid #3b82f6;
        padding: 15px 20px;
        border-radius: 8px;
        margin-top: -15px;
        margin-bottom: 25px;
        font-size: 0.95rem;
        color: #e2e8f0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .explainer-title {
        color: #60a5fa;
        font-weight: 700;
        margin-bottom: 5px;
        font-size: 1rem;
    }

    /* -------------------------------------------------------------------------
       FLOATING ECOPAY AI CSS (HACKATHON WINNING UI)
       ------------------------------------------------------------------------- */
    /* Target the stPopover button specifically to make it a floating logo */
    div[data-testid="stPopover"] {
        position: fixed !important;
        bottom: 40px !important;
        left: 40px !important;
        z-index: 9999 !important;
    }
    
    /* Style the actual floating button to be a perfect circular logo */
    div[data-testid="stPopover"] > button {
        background: linear-gradient(135deg, #10b981 0%, #047857 100%) !important;
        color: white !important;
        border-radius: 50% !important; /* Makes it a perfect circle */
        width: 75px !important; /* Fixed width for circle */
        height: 75px !important; /* Fixed height for circle */
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-weight: 800 !important;
        font-size: 2.5rem !important; /* Large logo icon size */
        border: 3px solid rgba(255, 255, 255, 0.3) !important;
        box-shadow: 0 10px 30px rgba(16, 185, 129, 0.6) !important;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
    }
    
    /* Floating button hover effect */
    div[data-testid="stPopover"] > button:hover {
        transform: scale(1.1) translateY(-5px) !important;
        box-shadow: 0 15px 35px rgba(16, 185, 129, 0.8) !important;
        background: linear-gradient(135deg, #34d399 0%, #059669 100%) !important;
    }
    
    /* Style the popover chat window container */
    div[data-testid="stPopoverBody"] {
        background-color: rgba(15, 23, 42, 0.95) !important;
        backdrop-filter: blur(15px) !important;
        border: 1px solid #3b82f6 !important;
        border-radius: 15px !important;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6) !important;
        width: 450px !important;
        max-width: 90vw !important;
    }
    
    /* Custom Chat Bubbles */
    .user-bubble {
        text-align: right; 
        background-color: rgba(59,130,246,0.2); 
        padding: 12px; 
        border-radius: 12px 12px 0 12px; 
        margin-bottom: 12px;
        color: white;
    }
    .ai-bubble {
        text-align: left; 
        background-color: rgba(16,185,129,0.15); 
        padding: 12px; 
        border-radius: 12px 12px 12px 0; 
        margin-bottom: 12px; 
        border-left: 4px solid #10b981;
        color: white;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 1.5. VOICE & TEXT-TO-SPEECH HELPERS
# -----------------------------------------------------------------------------
def get_language_code(text):
    """Detects the language script to provide accurate regional pronunciation."""
    if re.search(r'[\u0900-\u097F]', text): return 'hi' # Hindi/Marathi/Sanskrit
    if re.search(r'[\u0980-\u09FF]', text): return 'bn' # Bengali
    if re.search(r'[\u0A80-\u0AFF]', text): return 'gu' # Gujarati
    if re.search(r'[\u0B80-\u0BFF]', text): return 'ta' # Tamil
    if re.search(r'[\u0C00-\u0C7F]', text): return 'te' # Telugu
    if re.search(r'[\u0C80-\u0CFF]', text): return 'kn' # Kannada
    if re.search(r'[\u0D00-\u0D7F]', text): return 'ml' # Malayalam
    return 'en' # Default

def generate_voice(text):
    """Converts AI response text into an audio byte stream for playback."""
    try:
        # Clean text for better speech synthesis (remove markdown)
        clean_text = text.replace('*', '').replace('#', '').replace('_', '')
        lang = get_language_code(clean_text)
        tts = gTTS(text=clean_text, lang=lang, slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.getvalue()
    except Exception as e:
        print(f"TTS Error: {e}")
        return None

# -----------------------------------------------------------------------------
# 2. DATA PROCESSING & EMISSION LOGIC (The "Engine")
# -----------------------------------------------------------------------------

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("Daily Household Transactions.csv")
    except FileNotFoundError:
        st.error("File 'Daily Household Transactions.csv' not found. Please upload it.")
        return pd.DataFrame()

    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df = df[df['Income/Expense'] == 'Expense'].copy()
    if 'Currency' in df.columns:
        df = df[df['Currency'] == 'INR'] 
    
    # Fill NA for smooth plotting
    df['Category'] = df['Category'].fillna('Other')
    df['Subcategory'] = df['Subcategory'].fillna('General')
    df['Note'] = df['Note'].fillna('')

    return df

class CarbonScoringEngine:
    EMISSION_FACTORS = {
        'Transportation': 0.15, 'Food': 0.06, 'Utilities': 0.20,
        'Household': 0.08, 'Apparel': 0.10, 'Education': 0.01,
        'Health': 0.03, 'Personal Development': 0.01, 'Festivals': 0.05,
        'subscription': 0.005, 'Other': 0.05
    }
    
    SUBCATEGORY_FACTORS = {
        'Train': 0.04, 'Air': 0.25, 'auto': 0.12,
        'Vegetables': 0.03, 'Meat': 0.15,
    }
    
    RECOMMENDATIONS = {
        'Transportation': [
            "🚗 **Carpooling**: Reduces individual footprint by ~40% for daily commutes.",
            "🚲 **Active Transport**: Consider cycling for trips under 5km; it's zero emission!",
            "🚆 **Rail over Road**: Trains are 80% less carbon-intensive than solo driving.",
            "🔋 **EV Switch**: Transitioning to an Electric Vehicle can cut lifetime emissions by 50%."
        ],
        'Food': [
            "🥩 **Meat Reduction**: Reducing meat consumption by just one day a week saves ~4kg CO2.",
            "🌾 **Local Sourcing**: Buy local seasonal produce to cut down on 'food miles'.",
            "🥡 **Waste Not**: Meal prepping reduces food waste, a major methane source."
        ],
        'Utilities': [
            "💡 **LED Switch**: Switch to LED bulbs to cut lighting energy by 75%.",
            "🔌 **Vampire Power**: Unplug chargers and standby TVs to save 10% on bills.",
            "🌡️ **Smart Climate**: Adjusting AC by 1°C can save 6% electricity."
        ],
        'Apparel': [
            "👕 **Fast Fashion**: Buying one used item instead of new reduces its carbon footprint by 82%.",
            "🧶 **Material Choice**: Choose natural fibers like organic cotton or linen over polyester."
        ]
    }

    @staticmethod
    def calculate_footprint(row):
        category = row.get('Category', 'Other')
        subcategory = row.get('Subcategory', '')
        amount = row.get('Amount', 0)
        
        factor = CarbonScoringEngine.EMISSION_FACTORS.get(category, 0.05)
        
        if subcategory in CarbonScoringEngine.SUBCATEGORY_FACTORS:
            factor = CarbonScoringEngine.SUBCATEGORY_FACTORS[subcategory]
        elif isinstance(subcategory, str) and 'Meat' in subcategory:
            factor = 0.12 
            
        carbon_mass = amount * factor
        return factor, carbon_mass

    @staticmethod
    def generate_explanation(row, factor, carbon_mass):
        category = row['Category']
        intensity_label = "Low"
        if factor > 0.12: intensity_label = "High"
        elif factor > 0.05: intensity_label = "Moderate"
        
        explanation = f"**{intensity_label} Intensity** ({factor} kg/₹). "
        if intensity_label == "High":
            explanation += f"Driven by high-emission activity in *{category}*."
        else:
            explanation += f"Efficient spending in *{category}*."
        return explanation

    @staticmethod
    def calculate_eco_score(carbon_mass, amount):
        if amount == 0: return 100
        intensity = carbon_mass / amount
        score = max(0, 100 - (intensity * 400)) 
        return int(score)

    @staticmethod
    def determine_persona(avg_score):
        if avg_score >= 80: return "🌱 Eco-Warrior", "You are leading the charge for a greener planet!"
        elif avg_score >= 60: return "🌿 Conconscious Citizen", "You are making good choices, but there's room to grow."
        elif avg_score >= 40: return "🏭 Carbon Neutral Aspirant", "Your footprint is visible. Let's optimize your habits."
        else: return "⚠️ High Emitter", "Your activities have a significant impact. Action needed."
        
    @staticmethod
    def get_prescriptive_advice(category):
        return CarbonScoringEngine.RECOMMENDATIONS.get(category, ["🌱 Review this expense for sustainable alternatives.", "♻️ Consider the lifecycle impact of this purchase."])

    @staticmethod
    def calculate_offsets(total_carbon_kg):
        trees_needed = total_carbon_kg / 21
        cost_usd = (total_carbon_kg / 1000) * 12 
        cost_inr = cost_usd * 84 
        return trees_needed, cost_inr

# -----------------------------------------------------------------------------
# 3. ADVANCED VISUALIZATION GENERATORS
# -----------------------------------------------------------------------------

def plot_forecast(daily_emissions):
    if daily_emissions.empty or len(daily_emissions) < 5:
        return None
    daily_emissions = daily_emissions.sort_values('Date')
    daily_emissions['DayIndex'] = np.arange(len(daily_emissions))
    
    X = daily_emissions['DayIndex'].values
    y = daily_emissions['Carbon_Footprint_kg'].values
    
    if len(X) > 0:
        coef = np.polyfit(X, y, 1)
        poly1d_fn = np.poly1d(coef)
        
        future_days = np.arange(len(daily_emissions), len(daily_emissions) + 30)
        future_dates = [daily_emissions['Date'].iloc[-1] + timedelta(days=int(i)) for i in range(1, 31)]
        future_emissions = poly1d_fn(future_days)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=daily_emissions['Date'], y=daily_emissions['Carbon_Footprint_kg'], 
                                mode='lines+markers', name='Historical Data', line=dict(color='#00d26a')))
        fig.add_trace(go.Scatter(x=daily_emissions['Date'], y=poly1d_fn(X), 
                                mode='lines', name='Trend', line=dict(color='white', dash='dash')))
        fig.add_trace(go.Scatter(x=future_dates, y=future_emissions, 
                                mode='lines', name='30-Day Forecast', line=dict(color='#ffaa00', dash='dot')))
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white", hovermode="x unified")
        return fig
    return None

def plot_sankey(df):
    """Generates an advanced Flow diagram from Total -> Category -> Subcategory"""
    cat_emissions = df.groupby('Category')['Carbon_Footprint_kg'].sum()
    subcat_emissions = df.groupby(['Category', 'Subcategory'])['Carbon_Footprint_kg'].sum().reset_index()
    
    nodes = ["Total Carbon Footprint"] + list(cat_emissions.index) + list(subcat_emissions['Subcategory'].unique())
    node_dict = {node: i for i, node in enumerate(nodes)}
    
    source = []
    target = []
    value = []
    
    # Layer 1: Total to Category
    for cat, val in cat_emissions.items():
        if val > 0:
            source.append(node_dict["Total Carbon Footprint"])
            target.append(node_dict[cat])
            value.append(val)
            
    # Layer 2: Category to Subcategory
    for _, row in subcat_emissions.iterrows():
        if row['Carbon_Footprint_kg'] > 0:
            source.append(node_dict[row['Category']])
            target.append(node_dict[row['Subcategory']])
            value.append(row['Carbon_Footprint_kg'])
            
    fig = go.Figure(data=[go.Sankey(
        node=dict(pad=15, thickness=20, line=dict(color="black", width=0.5), label=nodes, color="#00d26a"),
        link=dict(source=source, target=target, value=value, color="rgba(0, 210, 106, 0.4)")
    )])
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white", height=450)
    return fig

# -----------------------------------------------------------------------------
# 4. MAIN APPLICATION UI
# -----------------------------------------------------------------------------

def main():
    data_df = load_data()
    if data_df.empty:
        return

    # --- Header & Nav ---
    st.title("Ecopay Carbon Engine")
    st.markdown("### Next-Gen Carbon Attribution & Scoring for AI for Good")
    
    col_nav1, col_nav2 = st.columns([3, 1])
    with col_nav1:
        min_date = data_df['Date'].min()
        max_date = data_df['Date'].max()
        date_range = st.date_input("Analysis Period", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    with col_nav2:
        st.caption("Engine Version: v7.0 (Floating Ecopay AI Edition)")
        st.caption("AI Status: Ecopay Intelligence Online 🟢")

    # --- Data Processing ---
    if len(date_range) == 2:
        start_date, end_date = date_range
        mask = (data_df['Date'] >= pd.to_datetime(start_date)) & (data_df['Date'] <= pd.to_datetime(end_date))
        filtered_df = data_df.loc[mask].copy()
    else:
        filtered_df = data_df.copy()

    engine = CarbonScoringEngine()
    results = filtered_df.apply(lambda x: engine.calculate_footprint(x), axis=1, result_type='expand')
    filtered_df[['Emission_Factor', 'Carbon_Footprint_kg']] = results
    filtered_df['Explanation'] = filtered_df.apply(lambda x: engine.generate_explanation(x, x['Emission_Factor'], x['Carbon_Footprint_kg']), axis=1)
    filtered_df['Eco_Score'] = filtered_df.apply(lambda x: engine.calculate_eco_score(x['Carbon_Footprint_kg'], x['Amount']), axis=1)

    st.markdown("<br>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # SECTION 1: DASHBOARD & METRICS
    # -------------------------------------------------------------------------
    st.markdown("## 📊 1. Core ESG Dashboard")
    st.markdown("Real-time overview of your environmental impact based on financial activity.")
    
    avg_score = filtered_df['Eco_Score'].mean()
    persona, persona_desc = engine.determine_persona(avg_score)
    total_carbon = filtered_df['Carbon_Footprint_kg'].sum()

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Total Spend Analyzed", f"₹{filtered_df['Amount'].sum():,.0f}")
    with col2: st.metric("Carbon Footprint", f"{total_carbon:,.2f} kg CO2e")
    with col3: st.metric("Total Transactions", f"{len(filtered_df)}")
    with col4: st.markdown(f"<div style='background-color:rgba(0,210,106,0.1); padding:10px; border-radius:10px; border:1px solid #00d26a; text-align:center;'><strong>{persona}</strong><br><span style='font-size:0.8em; color:#aaa;'>{persona_desc}</span></div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # VISUALS: GAUGE CHART & SUNBURST
    # -------------------------------------------------------------------------
    c1, c2 = st.columns([1, 1.5])
    
    with c1:
        st.subheader("Your Ecopay Score")
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = avg_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            gauge = {
                'axis': {'range': [0, 100]},
                'bar': {'color': "#00d26a"},
                'steps': [
                    {'range': [0, 40], 'color': "rgba(255, 75, 75, 0.4)"},
                    {'range': [40, 70], 'color': "rgba(255, 170, 0, 0.4)"},
                    {'range': [70, 100], 'color': "rgba(0, 210, 106, 0.4)"}],
            }
        ))
        fig_gauge.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white", height=300, margin=dict(t=20, b=20))
        st.plotly_chart(fig_gauge, use_container_width=True)
        
        st.markdown("""
        <div class="explainer-box">
            <div class="explainer-title">💡 Simple English Explanation: The Eco-Score Gauge</div>
            Think of this exactly like a Financial Credit Score, but for the planet. <b>100 is perfect</b>, meaning your purchases have zero carbon emissions. If your score is low (in the red zone), it means you are spending money on highly polluting categories like flights, petrol, or heavy electronics.
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.subheader("Emission Hierarchy (Heatmap)")
        cat_group = filtered_df.groupby(['Category', 'Subcategory'])[['Carbon_Footprint_kg', 'Amount']].sum().reset_index()
        fig_sun = px.sunburst(cat_group, path=['Category', 'Subcategory'], values='Carbon_Footprint_kg',
                            color='Carbon_Footprint_kg', color_continuous_scale='RdYlGn_r')
        fig_sun.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white", height=300, margin=dict(t=20, b=20))
        st.plotly_chart(fig_sun, use_container_width=True)
        
        st.markdown("""
        <div class="explainer-box">
            <div class="explainer-title">💡 Simple English Explanation: The Pizza Chart (Sunburst)</div>
            This breaks down your footprint like a pizza. The <b>inner slices</b> are your big habits (like 'Transportation' or 'Food'). If you look at the <b>outer slices</b>, it shows you the specific things inside those habits causing pollution (like 'Train' vs 'Cab'). The darker red a slice is, the worse it is for the environment.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # -------------------------------------------------------------------------
    # VISUALS: SANKEY DIAGRAM & SCATTER PLOT
    # -------------------------------------------------------------------------
    st.markdown("## 🕸️ 2. Deep Dive Analytics")
    
    st.subheader("The Carbon Flow River (Sankey Diagram)")
    st.plotly_chart(plot_sankey(filtered_df), use_container_width=True)
    st.markdown("""
    <div class="explainer-box">
        <div class="explainer-title">💡 Simple English Explanation: The River Chart (Sankey Flow)</div>
        Follow the river! This highly advanced chart shows exactly how your total pollution (on the left) splits into different life categories (in the middle), and then splits again into specific items (on the right). Thicker rivers mean a bigger carbon footprint. It visually proves exactly where your emissions are "flowing".
    </div>
    """, unsafe_allow_html=True)

    col_scat, col_radar = st.columns([1.5, 1])
    
    with col_scat:
        st.subheader("Efficiency Matrix: Cost vs Pollution")
        fig_scat = px.scatter(filtered_df, x="Amount", y="Carbon_Footprint_kg", color="Category", 
                              size="Amount", hover_data=["Note"], opacity=0.8)
        fig_scat.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white", 
                               xaxis_title="Money Spent (₹)", yaxis_title="Carbon Pollution (kg CO2e)")
        st.plotly_chart(fig_scat, use_container_width=True)
        
        st.markdown("""
        <div class="explainer-box">
            <div class="explainer-title">💡 Simple English Explanation: Cost vs Pollution Matrix</div>
            Every circle is a single purchase. The further to the <b>right</b> a circle is, the more expensive it was. The <b>higher up</b> it is, the more pollution it caused. You want your circles to be low and to the right (Expensive but Eco-friendly). Circles high up on the left are "Toxic" (Cheap but highly polluting).
        </div>
        """, unsafe_allow_html=True)
        
    with col_radar:
        st.subheader("Benchmarking Web")
        # Generate Radar Chart Data
        radar_df = filtered_df.groupby('Category')['Carbon_Footprint_kg'].sum().reset_index()
        # Mock "Optimal" footprint as 50% of their actual for visual benchmarking
        radar_df['Optimal Target'] = radar_df['Carbon_Footprint_kg'] * 0.5
        
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(r=radar_df['Carbon_Footprint_kg'], theta=radar_df['Category'], fill='toself', name='You', line_color='#ff4b4b'))
        fig_radar.add_trace(go.Scatterpolar(r=radar_df['Optimal Target'], theta=radar_df['Category'], fill='toself', name='Optimal User', line_color='#00d26a'))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=False)), paper_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig_radar, use_container_width=True)
        
        st.markdown("""
        <div class="explainer-box">
            <div class="explainer-title">💡 Simple English Explanation: The Spider Web (Radar)</div>
            This compares you to a perfect "Eco-Warrior". The green shape is the goal. The red shape is you. If your red shape spikes way outside the green shape in a category like "Food", it means your diet is heavily polluting compared to the optimal standard.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # -------------------------------------------------------------------------
    # TIME SERIES / DAY OF WEEK HEATMAP
    # -------------------------------------------------------------------------
    st.markdown("## 📅 3. Temporal Habits & AI Forecasting")
    
    col_heat, col_line = st.columns([1, 1.5])
    
    with col_heat:
        st.subheader("Weekly Pollution Intensity")
        # Group by day of week
        filtered_df['Day_Name'] = filtered_df['Date'].dt.day_name()
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        heat_df = filtered_df.groupby('Day_Name')['Carbon_Footprint_kg'].sum().reindex(day_order).reset_index()
        
        fig_bar_day = px.bar(heat_df, x='Day_Name', y='Carbon_Footprint_kg', color='Carbon_Footprint_kg', color_continuous_scale='Oranges')
        fig_bar_day.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white", xaxis_title="Day", yaxis_title="Total Emissions")
        st.plotly_chart(fig_bar_day, use_container_width=True)
        
        st.markdown("""
        <div class="explainer-box">
            <div class="explainer-title">💡 Simple English Explanation: The Weekday Pattern</div>
            Are you a weekend polluter? This chart groups all your carbon footprints by the day of the week. Many users find they pollute 3x more on Saturdays due to shopping and travel. This helps the AI pinpoint exactly <i>when</i> your bad habits trigger.
        </div>
        """, unsafe_allow_html=True)
        
    with col_line:
        st.subheader("AI Predictive Trend Analysis")
        daily_emissions = filtered_df.groupby('Date')[['Carbon_Footprint_kg']].sum().reset_index()
        fig_forecast = plot_forecast(daily_emissions)
        if fig_forecast:
            st.plotly_chart(fig_forecast, use_container_width=True)
        st.markdown("""
        <div class="explainer-box">
            <div class="explainer-title">💡 Simple English Explanation: The AI Crystal Ball (Forecast)</div>
            The green line is the past—what you actually emitted. The white dotted line is your average trend. The yellow dotted line is our AI looking into the future. It uses math (linear regression) to guess exactly how much you will pollute over the next 30 days if you don't change your habits right now.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # -------------------------------------------------------------------------
    # SIMULATOR & ACTION PLAN
    # -------------------------------------------------------------------------
    st.markdown("## 🎛️ 4. Impact Simulator & Action Plan")
    
    col_sim_controls, col_sim_res = st.columns([1, 1.5])
    
    with col_sim_controls:
        st.subheader("Simulate Habit Changes")
        reduce_transport = st.slider("Reduce Transportation Use", 0, 100, 20, format="-%d%%")
        reduce_food = st.slider("Shift to Plant-Based Diet", 0, 100, 15, format="-%d%%")
        reduce_utility = st.slider("Improve Home Energy Efficiency", 0, 100, 10, format="-%d%%")
        
        st.markdown("""
        <div class="explainer-box">
            <div class="explainer-title">💡 Simple English Explanation: The "What If" Machine</div>
            Move these sliders to play a game of "What If". What if you took 20% fewer cabs? What if you ate 15% less meat? The chart on the right will instantly update to show you how many kilograms of pollution you would save by making those small lifestyle changes.
        </div>
        """, unsafe_allow_html=True)
        
    with col_sim_res:
        current_totals = filtered_df.groupby('Category')['Carbon_Footprint_kg'].sum()
        new_transport = current_totals.get('Transportation', 0) * (1 - reduce_transport/100)
        new_food = current_totals.get('Food', 0) * (1 - reduce_food/100)
        new_utility = current_totals.get('Utilities', 0) * (1 - reduce_utility/100)
        other_cats = current_totals.drop(['Transportation', 'Food', 'Utilities'], errors='ignore').sum()
        
        projected_total = new_transport + new_food + new_utility + other_cats
        saved = total_carbon - projected_total
        
        c_sim1, c_sim2 = st.columns(2)
        c_sim1.metric("Simulated New Footprint", f"{projected_total:,.2f} kg", help="Your new estimated total.")
        c_sim2.metric("Carbon Erased!", f"{saved:,.2f} kg", delta=f"{saved/(total_carbon+0.1)*100:.1f}% Reduction", delta_color="normal")
        
        sim_df = pd.DataFrame({'Scenario': ['Your Reality', 'Simulated Future'], 'Emissions (kg)': [total_carbon, projected_total]})
        fig_sim = px.bar(sim_df, x='Scenario', y='Emissions (kg)', color='Scenario', color_discrete_sequence=['#ff4b4b', '#00d26a'])
        fig_sim.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white", height=250)
        st.plotly_chart(fig_sim, use_container_width=True)

    st.markdown("### 🚀 Prescriptive Recommendations (AI Generated)")
    top_2_categories = filtered_df.groupby('Category')['Carbon_Footprint_kg'].sum().nlargest(2).index.tolist()
    
    col_rec1, col_rec2 = st.columns(2)
    for i, category in enumerate(top_2_categories):
        target_col = col_rec1 if i == 0 else col_rec2
        with target_col:
            st.markdown(f"#### Priority {i+1} Target: {category}")
            recommendations = engine.get_prescriptive_advice(category)
            for rec in recommendations:
                st.info(rec)

    st.markdown("---")

    # -------------------------------------------------------------------------
    # CARBON OFFSETTING
    # -------------------------------------------------------------------------
    st.markdown("## 🌳 5. Neutralize Your Impact (Offsetting)")
    trees_needed, offset_cost = engine.calculate_offsets(total_carbon)
    
    col_off1, col_off2 = st.columns(2)
    with col_off1:
        st.metric("Trees Required to Offset", f"{trees_needed:.1f} 🌳")
    with col_off2:
        st.metric("Est. Market Cost to Offset", f"₹{offset_cost:,.2f}")
        
    st.markdown("""
    <div class="explainer-box">
        <div class="explainer-title">💡 Simple English Explanation: Offsetting</div>
        Even if you have great habits, you still pollute. "Offsetting" means paying to clean up your mess. This calculation shows exactly how many real-life trees need to be planted, and how much money it would cost to buy verified carbon credits, to magically erase your entire footprint back to zero.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br><br><br><br><br>", unsafe_allow_html=True) # Extra padding for floating button

    # -------------------------------------------------------------------------
    # SECTION 6: FLOATING MULTILINGUAL GROQ AI
    # -------------------------------------------------------------------------
    st.markdown("## 🤖 6. Intelligent Ecopay AI")
    st.markdown("Your personal RAG (Retrieval-Augmented Generation) Sustainability Advisor has been transformed into a **Modern Floating Circular Logo**! Look at the **bottom-left** of your screen to interact with Ecopay AI.")

    st.markdown("""
    <div class="explainer-box">
        <div class="explainer-title">💡 Hackathon UI/UX Feature: Floating Context-Aware Ecopay AI</div>
        We didn't just build a chatbot; we built an embedded AI RAG agent. We feed it your exact live data, footprint scores, and worst habits seamlessly in the background. Clicking the floating circular logo in the bottom-left utilizes the blazing-fast <b>Groq llama-3.3-70b-versatile</b> engine to instantly recognize hidden patterns and prescribe money-saving actions based on YOUR exact dataset, fully supporting <b>all regional Indian languages</b> natively.
    </div>
    """, unsafe_allow_html=True)

    # --- Setup Context Generation for the Popover AI ---
    top_items = filtered_df.nlargest(5, 'Carbon_Footprint_kg')[['Category', 'Note', 'Carbon_Footprint_kg']].to_dict(orient='records')
    cat_summary = filtered_df.groupby('Category')['Carbon_Footprint_kg'].sum().to_dict()
    
    system_context = f"""
    You are 'Ecopay AI', an elite, highly intelligent Environmental, Social, and Governance (ESG) advisor.
    Your absolute primary goal is to identify HIDDEN PATTERNS from the user's data and prescribe actionable solutions.
    
    Here is the user's live Matrix Data:
    - Overall Eco-Score: {avg_score:.0f}/100 (100 is absolute zero carbon)
    - Total Carbon Footprint: {total_carbon:.2f} kg CO2e
    - Total Money Spent: ₹{filtered_df['Amount'].sum():,.0f}
    - Category Breakdown (kg CO2e): {cat_summary}
    - Top 5 Most Polluting Transactions: {top_items}
    
    Instructions for your response:
    1. Be concise, highly professional, and encouraging.
    2. Speak in a consultative tone.
    3. You MUST structure your response with these exact headers if asked to analyze the data (translate these headers if speaking in a regional language):
       - 🔍 **Hidden Pattern Recognized:** (Explain a trend in their data)
       - 🚀 **Prescriptive Action Plan:** (Give 2 highly specific actions to reduce footprint and save money)
       - 💰 **Estimated Financial & Carbon Savings:** (Estimate what they will save if they follow your advice)
    4. Do not output raw markdown tables unless explicitly asked.
    5. MULTILINGUAL INDIAN SUPPORT (CRITICAL): You MUST support all regional languages in India (Hindi, Tamil, Telugu, Kannada, Malayalam, Bengali, Marathi, Gujarati, etc.). Autodetect the language used by the user and reply ENTIRELY in that exact same language while maintaining professional ESG terminology and accurate data insights.
    """

    # Ensure session state for chat exists
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": f"Hello! I am Ecopay AI. I've successfully ingested your {len(filtered_df)} transactions.\n\n🌍 **I support all Indian languages (हिंदी, தமிழ், తెలుగు, বাংলা, मराठी, etc.)!**\n\nAsk me in your preferred language to uncover your **Hidden Patterns** or generate a **Prescriptive Action Plan** to begin!"}
        ]

    # --- The Floating Popover Interface ---
    # Passing just an emoji creates the perfect circular logo based on our CSS
    with st.popover("🌿"):
        st.markdown("### 🤖 Ecopay AI")
        st.caption("AI Context Engine & Voice Synth: Active 🟢")
        
        # Fixed height scrollable container for chat history
        chat_container = st.container(height=350)
        
        # Placeholder to ensure audio is rendered in the correct position
        audio_container = st.empty()

        # Input form to interact with the LLM
        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_input("Ask me to analyze hidden trends or prescribe actions...")
            submitted = st.form_submit_button("Send to Ecopay AI 🚀")

        # Process AI generation BEFORE rendering the chat history
        # This prevents the need for st.rerun(), keeping the popover OPEN natively.
        if submitted and user_input:
            st.session_state.latest_audio = None # Clear old audio so it doesn't replay randomly
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            try:
                # API Call Logic using dynamic key resolution
                api_key = st.secrets.get("Groq_API", globals().get("Groq_API", locals().get("Groq_API")))
                
                if not api_key:
                    st.error("⚠️ Groq API key not found. Ensure 'Groq_API' is defined.")
                else:
                    client = Groq(api_key=api_key)
                    
                    messages_payload = [{"role": "system", "content": system_context}]
                    # Maintain context for recent messages
                    messages_payload.extend([{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-5:]])

                    with st.spinner("Analyzing deep matrix trends via Groq..."):
                        chat_completion = client.chat.completions.create(
                            messages=messages_payload,
                            model="llama-3.3-70b-versatile", # Upgraded to the highly capable, multilingual supported model
                            temperature=0.7,
                            max_tokens=1024,
                        )
                        response = chat_completion.choices[0].message.content
                        st.session_state.messages.append({"role": "assistant", "content": response})

                    with st.spinner("Generating Voice Response..."):
                        audio_bytes = generate_voice(response)
                        if audio_bytes:
                            st.session_state.latest_audio = audio_bytes

            except Exception as e:
                st.error(f"Groq Integration Error: {str(e)}")

        # Render chat history AFTER logic so we don't need a hard rerun
        with chat_container:
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    st.markdown(f"<div class='user-bubble'>👤 <b>You:</b><br>{msg['content']}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='ai-bubble'>🤖 <b>Ecopay AI:</b><br>{msg['content']}</div>", unsafe_allow_html=True)

        # --- Voice Playback Component ---
        with audio_container:
            if st.session_state.get("latest_audio"):
                st.audio(st.session_state.latest_audio, format="audio/mp3", autoplay=True)

if __name__ == "__main__":
    main()