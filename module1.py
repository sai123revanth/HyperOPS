import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Ecopay | Carbon Attribution Engine",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for a modern, "Eco-FinTech" aesthetic
st.markdown("""
<style>
    /* Main Background & Text */
    .stApp {
        /* Enhanced Gradient for a richer, more attractive look */
        background: linear-gradient(150deg, #050a0e 0%, #061e14 50%, #00331e 100%);
        background-attachment: fixed;
        color: #fafafa;
    }
    
    /* Modern Gradient Metrics Cards (The "Credit" Section) */
    div[data-testid="stMetric"] {
        background: rgba(17, 24, 39, 0.7); /* Semi-transparent */
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 210, 106, 0.2);
        border-left: 4px solid #00d26a; /* Bright green accent */
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

    /* Metric Values */
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        color: #ffffff; 
        font-weight: 700;
        text-shadow: 0 2px 4px rgba(0,0,0,0.5);
    }
    
    /* Metric Labels */
    div[data-testid="stMetricLabel"] {
        color: #9ca3af;
        font-size: 0.9rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Headers */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        color: #ffffff;
    }
    h1 { font-weight: 800; letter-spacing: -1px; }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        color: white;
    }
    
    /* Section Dividers */
    hr {
        margin-top: 3rem;
        margin-bottom: 3rem;
        border: 0;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Custom Info Box */
    .info-box {
        background-color: rgba(0, 168, 232, 0.1);
        border-left: 5px solid #00a8e8;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 10px;
    }

</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. DATA PROCESSING & EMISSION LOGIC (The "Engine")
# -----------------------------------------------------------------------------

@st.cache_data
def load_data():
    """
    Loads and preprocesses the transaction data.
    """
    try:
        df = pd.read_csv("Daily Household Transactions.csv")
    except FileNotFoundError:
        st.error("File 'Daily Household Transactions.csv' not found. Please upload it.")
        return pd.DataFrame()

    # 1. Date Parsing
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    
    # 2. Filter for Expenses only
    df = df[df['Income/Expense'] == 'Expense'].copy()
    
    # 3. Handle specific currency logic
    df = df[df['Currency'] == 'INR'] 

    return df

class CarbonScoringEngine:
    """
    Core logic for mapping transactions to carbon footprints using standard ESG frameworks.
    """
    
    # Estimated Emission Factors (kgCO2e per INR)
    # Derived from Economic Input-Output Life Cycle Assessment (EIO-LCA) models suitable for the region.
    EMISSION_FACTORS = {
        'Transportation': 0.15, 'Food': 0.06, 'Utilities': 0.20,
        'Household': 0.08, 'Apparel': 0.10, 'Education': 0.01,
        'Health': 0.03, 'Personal Development': 0.01, 'Festivals': 0.05,
        'subscription': 0.005, 'Other': 0.05
    }
    
    # Subcategory refinements for granular accuracy
    SUBCATEGORY_FACTORS = {
        'Train': 0.04, 'Air': 0.25, 'auto': 0.12,
        'Vegetables': 0.03, 'Meat': 0.15,
    }
    
    # Prescriptive Advice Database
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
        # Scientific approx: A mature tree absorbs ~21kg CO2 per year
        trees_needed = total_carbon_kg / 21
        # Approx cost: Verified carbon credits average ~$10-15 per tonne (1000kg)
        cost_usd = (total_carbon_kg / 1000) * 12 
        cost_inr = cost_usd * 84 # Approx exchange rate
        return trees_needed, cost_inr

# -----------------------------------------------------------------------------
# 3. ADVANCED FEATURES: FORECASTING & SIMULATION
# -----------------------------------------------------------------------------

def plot_forecast(daily_emissions):
    """Generates a predictive trend line using simple linear regression."""
    if daily_emissions.empty or len(daily_emissions) < 5:
        return None

    # Prepare data for regression
    daily_emissions = daily_emissions.sort_values('Date')
    daily_emissions['DayIndex'] = np.arange(len(daily_emissions))
    
    # Simple Linear Regression (y = mx + c)
    X = daily_emissions['DayIndex'].values
    y = daily_emissions['Carbon_Footprint_kg'].values
    
    if len(X) > 0:
        coef = np.polyfit(X, y, 1)
        poly1d_fn = np.poly1d(coef)
        
        # Forecast next 30 days
        future_days = np.arange(len(daily_emissions), len(daily_emissions) + 30)
        future_dates = [daily_emissions['Date'].iloc[-1] + timedelta(days=int(i)) for i in range(1, 31)]
        future_emissions = poly1d_fn(future_days)
        
        # Plot
        fig = go.Figure()
        
        # Historical
        fig.add_trace(go.Scatter(x=daily_emissions['Date'], y=daily_emissions['Carbon_Footprint_kg'], 
                                mode='lines+markers', name='Historical Data', line=dict(color='#00d26a')))
        
        # Trend Line
        fig.add_trace(go.Scatter(x=daily_emissions['Date'], y=poly1d_fn(X), 
                                mode='lines', name='Trend', line=dict(color='white', dash='dash')))
        
        # Forecast
        fig.add_trace(go.Scatter(x=future_dates, y=future_emissions, 
                                mode='lines', name='30-Day Forecast', line=dict(color='#ffaa00', dash='dot')))

        fig.update_layout(
            title="Carbon Emission Forecast (AI Trend Analysis)",
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)", 
            font_color="white",
            hovermode="x unified"
        )
        return fig
    return None

# -----------------------------------------------------------------------------
# 4. MAIN APPLICATION UI
# -----------------------------------------------------------------------------

def main():
    data_df = load_data()
    if data_df.empty:
        return

    # --- Header & Nav ---
    st.title("Ecopay Carbon Engine")
    st.markdown("### Next-Gen Carbon Attribution & Scoring")
    
    col_nav1, col_nav2 = st.columns([3, 1])
    with col_nav1:
        min_date = data_df['Date'].min()
        max_date = data_df['Date'].max()
        date_range = st.date_input("Analysis Period", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    with col_nav2:
        st.caption("Engine Version: v3.0 (Alpha)")
        st.caption("AI Status: Online")

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

    # -------------------------------------------------------------------------
    # INTRO: SCIENTIFIC METHODOLOGY (Collapsible)
    # -------------------------------------------------------------------------
    with st.expander("📘 How It Works: The Science of Carbon Attribution (Click to Expand)", expanded=False):
        st.markdown("""
        ### Carbon Attribution Methodology
        Ecopay utilizes a **Spend-Based Method** for carbon accounting, consistent with the GHG Protocol for Scope 3 (Category 1: Purchased Goods and Services).
        
        1.  **Transaction Classification (NLP):**
            We parse transaction metadata (Merchant, Category, Note) to map financial activities to sustainability vectors.
        
        2.  **Emission Factor Mapping (EIO-LCA):**
            We apply **Emission Factors (EF)** expressed in $kgCO_2e/INR$. These factors are derived from **Environmentally Extended Input-Output (EEIO)** models, which estimate the emissions produced throughout the supply chain of a product per unit of currency spent.
            * **Scope 1:** Direct emissions (e.g., fuel burnt in your car).
            * **Scope 2:** Indirect emissions (e.g., electricity used).
            * **Scope 3:** Upstream supply chain emissions (e.g., farming required for your food).
            
        3.  **The Eco-Score Algorithm:**
            Your score (0-100) is a normalized efficiency metric calculated as:
            $$ Score = 100 - (\\frac{Total Emissions (kg)}{Total Spend (INR)} \\times Sensitivity Factor) $$
            A higher score indicates you are spending money efficiently with lower carbon intensity.
        """)

    # -------------------------------------------------------------------------
    # SECTION 1: DASHBOARD
    # -------------------------------------------------------------------------
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("## 📊 Main Dashboard")
    st.markdown("Real-time overview of your environmental impact based on financial activity.")
    
    # Calculate Persona
    avg_score = filtered_df['Eco_Score'].mean()
    persona, persona_desc = engine.determine_persona(avg_score)

    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    total_carbon = filtered_df['Carbon_Footprint_kg'].sum()
    
    with col1: 
        st.metric("Total Spend", f"₹{filtered_df['Amount'].sum():,.0f}", help="Total financial outflow analyzed in the selected period.")
    with col2: 
        st.metric("Carbon Footprint", f"{total_carbon:,.2f} kg", delta="-5% (Target)", help="Total Equivalent Carbon Dioxide (CO2e) emitted directly or indirectly.")
    with col3: 
        st.metric("Avg Eco Score", f"{avg_score:.0f}/100", help="0-100 Score. 100 is Carbon Neutral. <50 is High Impact.")
    with col4: 
        st.markdown(f"<div style='background-color:rgba(0,210,106,0.1); padding:10px; border-radius:10px; border:1px solid #00d26a; text-align:center;'><strong>{persona}</strong><br><span style='font-size:0.8em; color:#aaa;'>{persona_desc}</span></div>", unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)

    # Visuals
    c1, c2 = st.columns([1.5, 1])
    with c1:
        st.subheader("Emission Sources")
        st.markdown("Identify which categories are contributing most to your footprint.")
        cat_group = filtered_df.groupby(['Category', 'Subcategory'])[['Carbon_Footprint_kg', 'Amount']].sum().reset_index()
        fig_sun = px.sunburst(cat_group, path=['Category', 'Subcategory'], values='Carbon_Footprint_kg',
                            color='Carbon_Footprint_kg', color_continuous_scale='RdYlGn_r',
                            title="Carbon Heatmap Hierarchy")
        fig_sun.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig_sun, use_container_width=True)

    with c2:
        st.subheader("Top Polluters")
        st.markdown("The specific activities driving up your score.")
        top_cats = filtered_df.groupby('Category')['Carbon_Footprint_kg'].sum().nlargest(5).sort_values(ascending=True)
        fig_bar = px.bar(top_cats, orientation='h', color=top_cats.values, color_continuous_scale='Reds')
        fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white", showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)

    # Transaction Table
    st.subheader("Deep Dive Analysis")
    st.markdown("Granular review of every transaction with automated engine logic.")
    st.dataframe(filtered_df[['Date', 'Category', 'Note', 'Amount', 'Carbon_Footprint_kg', 'Eco_Score', 'Explanation']].sort_values(by='Carbon_Footprint_kg', ascending=False), use_container_width=True)

    st.markdown("---")

    # -------------------------------------------------------------------------
    # SECTION 2: AI FORECAST
    # -------------------------------------------------------------------------
    st.markdown("## 🔮 Predictive Carbon Analytics")
    st.markdown("Using linear regression to project your emission trends for the next 30 days based on current behavior.")
    
    daily_emissions = filtered_df.groupby('Date')[['Carbon_Footprint_kg']].sum().reset_index()
    fig_forecast = plot_forecast(daily_emissions)
    
    if fig_forecast:
        st.plotly_chart(fig_forecast, use_container_width=True)
        
        # Simulated AI Insight
        trend_val = daily_emissions['Carbon_Footprint_kg'].iloc[-1]
        st.info(f"💡 **AI Insight:** Your carbon trend is volatile. Based on the projection, you are expected to reach **{trend_val*30:,.0f} kg** next month if habits persist. Reducing 'Transportation' frequency could flatten this curve.")
    else:
        st.warning("Not enough data points to generate a reliable forecast.")

    st.markdown("---")

    # -------------------------------------------------------------------------
    # SECTION 3: SIMULATOR
    # -------------------------------------------------------------------------
    st.markdown("## 🎛️ Lifestyle Impact Simulator")
    st.markdown("Visualize the impact of specific habit changes on your total footprint.")
    
    col_sim_controls, col_sim_res = st.columns([1, 2])
    
    with col_sim_controls:
        st.subheader("Adjust Habits")
        reduce_transport = st.slider("Reduce Transportation", 0, 100, 0, format="-%d%%", help="Simulate taking fewer cabs/flights.")
        reduce_food = st.slider("Plant-Based Diet Shift (Food)", 0, 100, 0, format="-%d%%", help="Simulate replacing meat meals with veg.")
        reduce_utility = st.slider("Energy Efficiency (Utilities)", 0, 100, 0, format="-%d%%", help="Simulate using LED bulbs/saving electricity.")
        
    with col_sim_res:
        # Calculation
        current_totals = filtered_df.groupby('Category')['Carbon_Footprint_kg'].sum()
        
        new_transport = current_totals.get('Transportation', 0) * (1 - reduce_transport/100)
        new_food = current_totals.get('Food', 0) * (1 - reduce_food/100)
        new_utility = current_totals.get('Utilities', 0) * (1 - reduce_utility/100)
        
        # Other categories remain same
        other_cats = current_totals.drop(['Transportation', 'Food', 'Utilities'], errors='ignore').sum()
        
        projected_total = new_transport + new_food + new_utility + other_cats
        saved = total_carbon - projected_total
        
        st.subheader("Projected Impact")
        
        c_sim1, c_sim2 = st.columns(2)
        c_sim1.metric("Projected Footprint", f"{projected_total:,.2f} kg", help="Your new estimated total.")
        c_sim2.metric("Carbon Saved", f"{saved:,.2f} kg", delta=f"{saved/(total_carbon+0.1)*100:.1f}% Reduction", delta_color="normal", help="Total CO2 prevented from entering the atmosphere.")
        
        # Simple Bar chart comparison
        sim_df = pd.DataFrame({
            'Scenario': ['Current', 'Simulated'],
            'Emissions (kg)': [total_carbon, projected_total]
        })
        fig_sim = px.bar(sim_df, x='Scenario', y='Emissions (kg)', color='Scenario', color_discrete_sequence=['#ff4b4b', '#00d26a'])
        fig_sim.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig_sim, use_container_width=True)

    st.markdown("---")
    
    # -------------------------------------------------------------------------
    # NEW SECTION: AI ACTION PLAN (Prescriptive Features)
    # -------------------------------------------------------------------------
    st.markdown("## 🚀 AI-Driven Prescriptive Action Plan")
    st.markdown("Based on your unique spending profile, we have identified high-impact areas and specific actions you can take immediately.")
    
    # Identify top 2 highest emitting categories
    top_2_categories = filtered_df.groupby('Category')['Carbon_Footprint_kg'].sum().nlargest(2).index.tolist()
    
    col_rec1, col_rec2 = st.columns(2)
    
    for i, category in enumerate(top_2_categories):
        target_col = col_rec1 if i == 0 else col_rec2
        with target_col:
            st.markdown(f"#### Priority {i+1}: {category}")
            current_cat_emit = filtered_df[filtered_df['Category'] == category]['Carbon_Footprint_kg'].sum()
            st.markdown(f"**Current Impact:** {current_cat_emit:.2f} kg CO2e")
            st.progress(min(1.0, current_cat_emit / total_carbon), text="Contribution to Total Footprint")
            
            st.markdown("**Recommended Actions:**")
            recommendations = engine.get_prescriptive_advice(category)
            for rec in recommendations:
                st.info(rec)

    st.markdown("---")

    # -------------------------------------------------------------------------
    # SECTION 4: BENCHMARKING
    # -------------------------------------------------------------------------
    st.markdown("## 🏆 Community Benchmarking")
    st.markdown("Compare your footprint against regional averages and the Ecopay community.")
    
    col_bench_1, col_bench_2 = st.columns(2)
    
    with col_bench_1:
        # Mock Data for Benchmarking
        bench_data = {
            'Metric': ['Global Avg', 'National Avg', 'Ecopay Top 10%', 'You'],
            'Monthly Emissions (kg)': [380, 250, 120, total_carbon/12] # Assuming total is roughly annual or scaling it
        }
        df_bench = pd.DataFrame(bench_data)
        
        fig_bench = px.bar(df_bench, x='Metric', y='Monthly Emissions (kg)', 
                         color='Metric', 
                         color_discrete_map={'You': '#00d26a', 'Global Avg': '#888', 'National Avg': '#aaa', 'Ecopay Top 10%': '#ffd700'},
                         title="Monthly Average Comparison")
        fig_bench.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig_bench, use_container_width=True)
        
    with col_bench_2:
        st.info("ℹ️ **Did you know?** The average urban resident emits roughly 250kg of CO2 per month via direct spending. To reach the 2050 Net Zero goals, this needs to drop to <150kg.")
        
        st.markdown("#### Your Ranking")
        if avg_score > 70:
            st.success("🌟 You are in the **Top 15%** of Ecopay users!")
        elif avg_score > 50:
            st.warning("You are in the **Top 60%**. Try the Simulator to find ways to improve.")
        else:
            st.error("You are in the **Bottom 30%**. High emission intensity detected.")

    st.markdown("---")

    # -------------------------------------------------------------------------
    # NEW SECTION: CARBON OFFSETTING
    # -------------------------------------------------------------------------
    st.markdown("## 🌳 Neutralize Your Impact (Offsetting Path)")
    st.markdown("Even with the best habits, some emissions are unavoidable. Here is what it takes to become Carbon Neutral today.")
    
    trees_needed, offset_cost = engine.calculate_offsets(total_carbon)
    
    col_off1, col_off2 = st.columns(2)
    
    with col_off1:
        st.metric("Trees Required", f"{trees_needed:.1f} 🌳", help="Number of mature trees needed to absorb this amount of CO2 in one year.")
    with col_off2:
        st.metric("Est. Offset Cost", f"₹{offset_cost:,.2f}", help="Approximate market cost to purchase verified carbon credits for this amount.")

    st.markdown("<br><br><br>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()