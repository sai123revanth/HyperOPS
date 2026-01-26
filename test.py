import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="GreenIQ | Carbon Analytics",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for GreenIQ Branding
st.markdown("""
    <style>
        .main {
            background-color: #f9fbf9;
        }
        .stMetric {
            background-color: #ffffff;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            border-left: 5px solid #2ecc71;
        }
        h1, h2, h3 {
            color: #27ae60;
            font-family: 'Helvetica Neue', sans-serif;
        }
        .highlight {
            color: #2ecc71;
            font-weight: bold;
        }
        /* Custom card style for Offset Marketplace */
        .offset-card {
            background-color: white;
            padding: 20px;
            border-radius: 15px;
            border: 1px solid #e0e0e0;
            text-align: center;
            transition: transform 0.2s;
        }
        .offset-card:hover {
            transform: scale(1.02);
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. DATA PROCESSING & LOGIC
# -----------------------------------------------------------------------------

# Estimated Emission Factors (kg CO2e per INR spent)
# In a real API, these would come from the Merchant Categorization Engine
EMISSION_FACTORS = {
    'Transportation': 0.15,  # High fuel usage
    'Food': 0.06,           # Agriculture/Transport
    'Utilities': 0.20,      # Energy consumption
    'Household': 0.05,      # Goods manufacturing
    'Apparel': 0.10,        # Fast fashion impact
    'Beauty': 0.04,         # Chemicals/Packaging
    'Health': 0.03,         # Services (lower direct impact)
    'Education': 0.01,      # Mostly service/digital
    'Gift': 0.05,
    'Social Life': 0.08,    # Dining out/Events
    'Other': 0.05,
    'subscription': 0.005,  # Digital services (server costs)
    'Festivals': 0.08       # Material consumption
}

@st.cache_data
def load_data(filepath):
    """Loads and preprocesses the transaction dataset."""
    try:
        df = pd.read_csv(filepath)
        
        # Standardize dates
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
        
        # Filter only Expenses (Income reduces net footprint conceptually, but here we track gross output)
        df = df[df['Income/Expense'] == 'Expense'].copy()
        
        # Normalize Category names for mapping
        df['Category_Map'] = df['Category'].str.strip().fillna('Other')
        
        # Calculate Carbon Footprint
        # Logic: Amount * Emission Factor for that Category
        def get_emission(row):
            cat = row['Category_Map']
            # Fuzzy match or direct lookup
            factor = EMISSION_FACTORS.get(cat, EMISSION_FACTORS.get('Other', 0.05))
            
            # Specific override for Subcategories if needed (Example logic)
            if 'Train' in str(row['Subcategory']):
                factor = 0.04 # Trains are cleaner than general transport
            elif 'Flight' in str(row['Subcategory']):
                factor = 0.25 # Flights are higher
            
            return row['Amount'] * factor

        df['Carbon_Emission_kg'] = df.apply(get_emission, axis=1)
        
        return df.sort_values(by='Date')
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Load Data
df = load_data('Daily Household Transactions.csv')

if df.empty:
    st.warning("Please upload 'Daily Household Transactions.csv' to proceed.")
    st.stop()

# -----------------------------------------------------------------------------
# 3. SIDEBAR CONTROLS
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3209/3209265.png", width=80)
    st.title("GreenIQ Controls")
    
    st.markdown("---")
    
    # Date Filter
    min_date = df['Date'].min()
    max_date = df['Date'].max()
    
    date_range = st.date_input(
        "Select Analysis Period",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Category Filter
    all_cats = ['All'] + sorted(df['Category'].dropna().unique().tolist())
    selected_cat = st.selectbox("Filter by Category", all_cats)
    
    st.markdown("---")
    st.info("💡 **Tip:** Transportation usually accounts for 30% of an average user's carbon footprint.")

# Apply Filters
start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
mask = (df['Date'] >= start_date) & (df['Date'] <= end_date)
if selected_cat != 'All':
    mask = mask & (df['Category'] == selected_cat)
    
filtered_df = df.loc[mask]

# -----------------------------------------------------------------------------
# 4. MAIN DASHBOARD
# -----------------------------------------------------------------------------

# -- Header --
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.title("GreenIQ Analytics Dashboard")
    st.markdown("Tracking your **Personal Carbon Footprint** through Transaction Analytics.")
with col_h2:
    st.metric(label="Sustainability Score", value="72/100", delta="2.5%")

st.markdown("---")

# -- Top Level KPIs --
total_spend = filtered_df['Amount'].sum()
total_emissions = filtered_df['Carbon_Emission_kg'].sum()
# Avoid division by zero
avg_intensity = (total_emissions / total_spend) if total_spend > 0 else 0
trees_needed = total_emissions / 20  # Approx 20kg CO2 absorbed per tree/year

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric("Total Spend", f"₹{total_spend:,.0f}", delta_color="off")
with kpi2:
    st.metric("Total Carbon Emissions", f"{total_emissions:,.2f} kg CO2e", delta="-5% vs Last Month")
with kpi3:
    st.metric("Carbon Intensity", f"{avg_intensity:.3f} kg/₹", help="Kilograms of CO2 emitted per Rupee spent.")
with kpi4:
    st.metric("Offset Required", f"{int(trees_needed)} Trees 🌳", delta_color="inverse")

# -----------------------------------------------------------------------------
# 5. DETAILED VISUALIZATIONS
# -----------------------------------------------------------------------------

tab1, tab2, tab3 = st.tabs(["📊 Impact Analysis", "📈 Trends & Insights", "🌍 Offset Marketplace"])

with tab1:
    st.subheader("Carbon Impact Breakdown")
    
    c1, c2 = st.columns([1.5, 1])
    
    with c1:
        # Bar Chart: Emissions by Category
        emission_by_cat = filtered_df.groupby('Category')['Carbon_Emission_kg'].sum().reset_index()
        fig_bar = px.bar(
            emission_by_cat, 
            x='Category', 
            y='Carbon_Emission_kg',
            color='Carbon_Emission_kg',
            color_continuous_scale=['#a8e6cf', '#2ecc71', '#0b5345'],
            title="Total Emissions by Spending Category",
            labels={'Carbon_Emission_kg': 'CO2 Emissions (kg)'},
            template="simple_white"
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with c2:
        # Donut Chart: Share of Emissions
        fig_pie = px.pie(
            emission_by_cat,
            values='Carbon_Emission_kg',
            names='Category',
            title="Carbon Footprint Distribution",
            color_discrete_sequence=px.colors.sequential.Greens_r,
            hole=0.4
        )
        fig_pie.update_traces(textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)

    # Scatter: Spend vs Emission (Identify high impact, low cost items)
    st.markdown("### Spending Efficiency Matrix")
    st.caption("Identify 'High Emission' transactions relative to their cost.")
    
    fig_scatter = px.scatter(
        filtered_df,
        x='Amount',
        y='Carbon_Emission_kg',
        color='Category',
        size='Amount',
        hover_data=['Subcategory', 'Date'],
        title="Transaction Scatter: Cost (₹) vs. Impact (kg CO2)",
        template="simple_white",
        color_discrete_sequence=px.colors.qualitative.Prism
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

with tab2:
    st.subheader("Emissions Timeline")
    
    # Aggregate by Month
    daily_emissions = filtered_df.groupby('Date')[['Carbon_Emission_kg', 'Amount']].sum().reset_index()
    
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=daily_emissions['Date'], 
        y=daily_emissions['Carbon_Emission_kg'],
        mode='lines',
        name='CO2 Emissions',
        line=dict(color='#27ae60', width=3),
        fill='tozeroy'
    ))
    
    fig_line.update_layout(
        title="Daily Emission Trends",
        xaxis_title="Date",
        yaxis_title="CO2 (kg)",
        template="plotly_white",
        hovermode="x unified"
    )
    st.plotly_chart(fig_line, use_container_width=True)
    
    # Insights Section
    st.subheader("🤖 AI Insights (Simulation)")
    high_impact_cat = emission_by_cat.loc[emission_by_cat['Carbon_Emission_kg'].idxmax()]
    
    st.markdown(f"""
    <div style='background-color: #e8f8f5; padding: 20px; border-radius: 10px; border-left: 5px solid #1abc9c;'>
        <h4>🌱 Insight Report</h4>
        <ul>
            <li>Your highest impact category is <b>{high_impact_cat['Category']}</b>, contributing <b>{high_impact_cat['Carbon_Emission_kg']:.1f} kg</b> of CO2.</li>
            <li>Spending on <i>Vegetarian options</i> instead of meat could reduce your 'Food' footprint by approx 40%.</li>
            <li>Switching from Private Transport to Public Transport for 5 trips this month would save ~15 kg CO2.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with tab3:
    st.subheader("Verified Offset Marketplace")
    st.write("Compensate for your **{:.2f} kg** CO2e footprint today.".format(total_emissions))
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("""
        <div class="offset-card">
            <h3>🌲 Reforestation</h3>
            <p>Plant native trees in the Amazon.</p>
            <h2 style="color: #27ae60;">₹ 450</h2>
            <p>Offsets ~250kg CO2</p>
            <button style="background-color:#2ecc71; color:white; border:none; padding:10px 20px; border-radius:5px;">Buy Credits</button>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        st.markdown("""
        <div class="offset-card">
            <h3>☀️ Solar Energy</h3>
            <p>Fund solar panels for rural schools.</p>
            <h2 style="color: #f1c40f;">₹ 800</h2>
            <p>Offsets ~500kg CO2</p>
            <button style="background-color:#f1c40f; color:white; border:none; padding:10px 20px; border-radius:5px;">Invest</button>
        </div>
        """, unsafe_allow_html=True)
        
    with c3:
        st.markdown("""
        <div class="offset-card">
            <h3>🌊 Ocean Cleanup</h3>
            <p>Remove plastic from the Pacific.</p>
            <h2 style="color: #3498db;">₹ 1,200</h2>
            <p>Offsets ~700kg CO2</p>
            <button style="background-color:#3498db; color:white; border:none; padding:10px 20px; border-radius:5px;">Support</button>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: grey;'>"
    "GreenIQ Hackathon Project © 2024 | "
    "Data Source: User Financial Transactions | "
    "Emission Factors: IPCC Guidelines (Simulated)"
    "</div>", 
    unsafe_allow_html=True
)