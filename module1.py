import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

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
        font-size: 2.2rem;
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
    
    /* Navigation/Controls Container */
    .nav-container {
        background-color: #1f2937;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        border: 1px solid #374151;
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
    # Simulate loading the user's uploaded file. 
    # In a real deployment, this would use the uploaded file object or path.
    # For this demo, we assume the file exists in the directory.
    try:
        df = pd.read_csv("Daily Household Transactions.csv")
    except FileNotFoundError:
        st.error("File 'Daily Household Transactions.csv' not found. Please upload it.")
        return pd.DataFrame()

    # 1. Date Parsing (Handling potentially mixed formats)
    # The snippet showed '20/09/2018 12:04:08' and '19/09/2018'
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    
    # 2. Filter for Expenses only (Income doesn't add to consumption footprint directly)
    df = df[df['Income/Expense'] == 'Expense'].copy()
    
    # 3. Handle specific currency logic (assuming INR for this dataset)
    # If other currencies exist, conversion logic would go here.
    df = df[df['Currency'] == 'INR'] 

    return df

class CarbonScoringEngine:
    """
    Core logic for mapping transactions to carbon footprints.
    """
    
    # Estimated Emission Factors (kgCO2e per INR)
    # In a real app, this would query an API like Climatiq or Exiobase.
    # These are heuristic estimations for demonstration.
    EMISSION_FACTORS = {
        'Transportation': 0.15,   # High fuel intensity
        'Food': 0.06,             # Agriculture intensity
        'Utilities': 0.20,        # Electricity/Gas
        'Household': 0.08,        # General goods
        'Apparel': 0.10,          # Fast fashion impact
        'Education': 0.01,        # Low direct impact
        'Health': 0.03,           # Services
        'Personal Development': 0.01,
        'Festivals': 0.05,        # Consumables
        'subscription': 0.005,    # Digital goods (Server energy only)
        'Other': 0.05             # Fallback
    }
    
    # Subcategory refinements (Overrides)
    SUBCATEGORY_FACTORS = {
        'Train': 0.04,            # Efficient transport
        'Air': 0.25,              # High impact
        'auto': 0.12,             # Fossil fuel
        'Vegetables': 0.03,       # Low impact food
        'Meat': 0.15,             # High impact food
    }

    @staticmethod
    def calculate_footprint(row):
        category = row.get('Category', 'Other')
        subcategory = row.get('Subcategory', '')
        amount = row.get('Amount', 0)
        
        # Determine Factor
        factor = CarbonScoringEngine.EMISSION_FACTORS.get(category, 0.05)
        
        # Apply Subcategory refinement if applicable
        if subcategory in CarbonScoringEngine.SUBCATEGORY_FACTORS:
            factor = CarbonScoringEngine.SUBCATEGORY_FACTORS[subcategory]
        elif isinstance(subcategory, str) and 'Meat' in subcategory:
            factor = 0.12 # Heuristic detection
            
        carbon_mass = amount * factor # kgCO2e
        
        return factor, carbon_mass

    @staticmethod
    def generate_explanation(row, factor, carbon_mass):
        """Generates natural language explanation for the score."""
        amount = row['Amount']
        category = row['Category']
        
        intensity_label = "Low"
        if factor > 0.12: intensity_label = "High"
        elif factor > 0.05: intensity_label = "Moderate"
        
        explanation = f"Classified as **{intensity_label} Intensity** ({factor} kgCO2e/INR). "
        
        if intensity_label == "High":
            explanation += f"Driven by high-emission activity in *{category}*."
        elif intensity_label == "Low":
            explanation += f"Efficient spending in *{category}*."
            
        return explanation

    @staticmethod
    def calculate_eco_score(carbon_mass, amount):
        """
        Calculates a 0-100 score. 
        100 = Carbon Neutral/Positive
        0 = Extremely High Intensity
        """
        if amount == 0: return 100
        intensity = carbon_mass / amount
        # Sigmoid-like decay: Higher intensity -> Lower Score
        score = max(0, 100 - (intensity * 400)) 
        return int(score)

# -----------------------------------------------------------------------------
# 3. MAIN APPLICATION UI
# -----------------------------------------------------------------------------

def main():
    # Load Data First
    data_df = load_data()
    if data_df.empty:
        return

    # --- Header & Top Navigation Controls ---
    st.title("Ecopay Carbon Engine")
    st.markdown("### Carbon Attribution & Scoring Dashboard")
    st.markdown("Mapping categorized financial transactions to standardized emission factors to produce actionable climate intelligence.")
    
    st.markdown("---")
    
    # Date Filter
    min_date = data_df['Date'].min()
    max_date = data_df['Date'].max()
    
    date_range = st.date_input(
        "Analysis Period",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    st.divider()

    # --- Processing Data with Engine ---
    if len(date_range) == 2:
        start_date, end_date = date_range
        mask = (data_df['Date'] >= pd.to_datetime(start_date)) & (data_df['Date'] <= pd.to_datetime(end_date))
        filtered_df = data_df.loc[mask].copy()
    else:
        filtered_df = data_df.copy()

    # Apply Carbon Logic
    engine = CarbonScoringEngine()
    
    # Vectorized application of logic would be faster, but apply is better for 'explanation' generation here
    results = filtered_df.apply(
        lambda x: engine.calculate_footprint(x), axis=1, result_type='expand'
    )
    filtered_df[['Emission_Factor', 'Carbon_Footprint_kg']] = results
    
    # Generate Explanations & Eco Scores
    filtered_df['Explanation'] = filtered_df.apply(
        lambda x: engine.generate_explanation(x, x['Emission_Factor'], x['Carbon_Footprint_kg']), axis=1
    )
    filtered_df['Eco_Score'] = filtered_df.apply(
        lambda x: engine.calculate_eco_score(x['Carbon_Footprint_kg'], x['Amount']), axis=1
    )

    # 1. TOP LEVEL METRICS (CREDIT SECTION)
    
    # Add Space
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_spend = filtered_df['Amount'].sum()
    total_carbon = filtered_df['Carbon_Footprint_kg'].sum()
    avg_score = filtered_df['Eco_Score'].mean()
    intensity = (total_carbon / total_spend) if total_spend > 0 else 0

    with col1:
        st.metric("Total Spend", f"₹{total_spend:,.0f}", delta_color="off")
    with col2:
        st.metric("Carbon Footprint", f"{total_carbon:,.2f} kgCO₂e", delta="-12% vs avg")
    with col3:
        st.metric("Carbon Intensity", f"{intensity:.3f} kg/₹", help="Kilograms of CO2 emitted per Rupee spent")
    with col4:
        st.metric("Avg Eco Score", f"{avg_score:.0f}/100", delta=f"{avg_score-50:.0f} pts")

    # Add Space
    st.markdown("<br><br>", unsafe_allow_html=True)

    # 2. VISUALIZATION ROW
    c1, c2 = st.columns([1.5, 1])

    with c1:
        st.subheader("Carbon Attribution by Category")
        # Aggregating for Sunburst
        cat_group = filtered_df.groupby(['Category', 'Subcategory'])[['Carbon_Footprint_kg', 'Amount']].sum().reset_index()
        fig_sun = px.sunburst(
            cat_group, 
            path=['Category', 'Subcategory'], 
            values='Carbon_Footprint_kg',
            color='Carbon_Footprint_kg',
            color_continuous_scale='RdYlGn_r', # Red is high carbon
            title="Emission Sources Hierarchy"
        )
        fig_sun.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig_sun, use_container_width=True)

    with c2:
        st.subheader("Timeline Analysis")
        # Time series
        daily_emissions = filtered_df.groupby('Date')[['Carbon_Footprint_kg']].sum().reset_index()
        fig_line = px.area(
            daily_emissions, 
            x='Date', 
            y='Carbon_Footprint_kg',
            line_shape='spline',
            color_discrete_sequence=['#00d26a'],
            title="Daily Emission Trend"
        )
        fig_line.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig_line, use_container_width=True)

    # 3. DETAILED ATTRIBUTION TABLE
    st.subheader("Transaction Attribution Engine")
    
    # Sort by impact
    display_df = filtered_df[['Date', 'Category', 'Subcategory', 'Note', 'Amount', 'Emission_Factor', 'Carbon_Footprint_kg', 'Eco_Score', 'Explanation']].sort_values(by='Carbon_Footprint_kg', ascending=False)
    
    # Config for styling the dataframe
    st.dataframe(
        display_df,
        use_container_width=True,
        column_config={
            "Date": st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
            "Amount": st.column_config.NumberColumn("Amount (₹)", format="₹%d"),
            "Emission_Factor": st.column_config.NumberColumn("Emiss. Factor", format="%.2f"),
            "Carbon_Footprint_kg": st.column_config.ProgressColumn(
                "Carbon Impact", 
                help="Relative impact", 
                format="%.2f kg",
                min_value=0, 
                max_value=float(display_df['Carbon_Footprint_kg'].max()) if not display_df.empty else 1.0
            ),
            "Eco_Score": st.column_config.NumberColumn(
                "Score",
                help="0 (Bad) - 100 (Good)",
                format="%d"
            ),
            "Note": st.column_config.TextColumn("Details", width="medium"),
            "Explanation": st.column_config.TextColumn("Engine Logic", width="large")
        },
        height=400
    )

    # 4. EXPLAINABILITY SECTION (Deep Dive)
    st.markdown("---")
    st.subheader("🔍 Transaction Inspector")
    
    col_select, col_explain = st.columns([1, 2])
    
    with col_select:
        selected_idx = st.selectbox("Select a High-Impact Transaction to Audit:", display_df.index[:10], format_func=lambda x: f"{display_df.loc[x, 'Note']} ({display_df.loc[x, 'Amount']} INR)")
        
    with col_explain:
        tx = display_df.loc[selected_idx]
        
        st.markdown(f"#### Audit: {tx['Note']}")
        
        e1, e2, e3 = st.columns(3)
        e1.metric("Category", tx['Category'])
        e2.metric("Emission Factor", f"{tx['Emission_Factor']:.2f}")
        e3.metric("Attributed Carbon", f"{tx['Carbon_Footprint_kg']:.2f} kg")
        
        st.info(f"**Engine Reason:** {tx['Explanation']}")
        
        if tx['Eco_Score'] < 50:
            st.warning("⚠️ **Improvement Tip:** Consider switching to public transport or grouping orders to reduce this category's footprint.")
        else:
            st.success("✅ **Good Choice:** This transaction has a relatively low carbon intensity.")

    # Added extra space at the bottom for better scroll/layout
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()