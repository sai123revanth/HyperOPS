import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import random
from datetime import datetime, timedelta

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Ecopay | Merchant Sustainability Index",
    page_icon="🏢",
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
    h1 {
        font-family: 'Inter', sans-serif;
        font-size: 2.5rem;
        font-weight: 800;
        letter-spacing: -1px;
        background: -webkit-linear-gradient(#fff, #aaa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    h2, h3 {
        font-family: 'Inter', sans-serif;
        color: white;
        font-weight: 700;
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
        box-shadow: 0 12px 40px rgba(0, 210, 106, 0.2);
    }

    /* Merchant Score Grade */
    .grade-circle {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2.5rem;
        font-weight: 900;
        color: white;
        box-shadow: 0 0 20px rgba(0,0,0,0.5);
    }
    .grade-A { background: linear-gradient(135deg, #00b09b, #96c93d); border: 3px solid #fff; }
    .grade-B { background: linear-gradient(135deg, #f2994a, #f2c94c); border: 3px solid #fff; }
    .grade-C { background: linear-gradient(135deg, #eb3349, #f45c43); border: 3px solid #fff; }

    /* Custom Progress Bars */
    .stProgress > div > div > div > div {
        background-image: linear-gradient(to right, #00d26a , #00eb78);
    }
    
    /* Pill Badges */
    .esg-pill {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 5px;
        margin-bottom: 5px;
        border: 1px solid rgba(255,255,255,0.2);
    }
    .pill-env { background: rgba(25, 135, 84, 0.2); color: #75b798; }
    .pill-soc { background: rgba(13, 202, 240, 0.2); color: #3dd5f3; }
    .pill-gov { background: rgba(255, 193, 7, 0.2); color: #ffca2c; }
    
    /* Certification Badges */
    .cert-badge {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid #ffd700;
        color: #ffd700;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        display: inline-block;
        margin-right: 5px;
    }

    /* Search Bar Styling */
    input[type="text"] {
        background-color: rgba(255,255,255,0.1) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 10px !important;
    }
    
    /* Section Divider */
    .section-divider {
        margin-top: 40px;
        margin-bottom: 20px;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. DATA LOGIC & MOCK DATABASE
# -----------------------------------------------------------------------------

# Simulated ESG Database with Enhanced Metadata
MERCHANT_DB = {
    'Netflix': {
        'score': 85, 'grade': 'A', 'sector': 'Tech', 
        'esg': [80, 90, 85], 'flags': [], 
        'desc': 'Carbon neutral via offsetting, high diversity scores in leadership.',
        'certs': ['Net Zero Committment', 'Equality 100'],
        'sentiment': 0.8
    },
    'Tata Sky': {
        'score': 65, 'grade': 'B', 'sector': 'Telecom', 
        'esg': [60, 70, 65], 'flags': ['Energy Intensity'], 
        'desc': 'Moderate renewable adoption, standard governance practices.',
        'certs': ['ISO 14001'],
        'sentiment': 0.4
    },
    'Mobile Service Provider': {
        'score': 70, 'grade': 'B', 'sector': 'Telecom', 
        'esg': [65, 75, 70], 'flags': [], 
        'desc': 'Transitioning to green towers and renewable energy sources.',
        'certs': [],
        'sentiment': 0.5
    },
    'Indian Railways (Train)': {
        'score': 92, 'grade': 'A+', 'sector': 'Transport', 
        'esg': [95, 85, 90], 'flags': ['Public Good'], 
        'desc': 'Most efficient transport mode per passenger-km. Heavy electrification underway.',
        'certs': ['Public Utility', 'Green Transport'],
        'sentiment': 0.9
    },
    'Local Auto/Taxi': {
        'score': 45, 'grade': 'C', 'sector': 'Transport', 
        'esg': [30, 60, 45], 'flags': ['Fossil Fuel'], 
        'desc': 'High particulate emissions, informal labor sector with mixed standards.',
        'certs': [],
        'sentiment': -0.2
    },
    'Local Grocery/Vegetable': {
        'score': 88, 'grade': 'A', 'sector': 'Retail', 
        'esg': [90, 85, 80], 'flags': ['Local Sourcing'], 
        'desc': 'Minimal packaging, short supply chain, supports local agriculture.',
        'certs': ['Local Business'],
        'sentiment': 0.85
    },
    'Fast Food Chain': {
        'score': 35, 'grade': 'C-', 'sector': 'Food', 
        'esg': [20, 40, 45], 'flags': ['Plastic Waste', 'Deforestation Risk'], 
        'desc': 'Heavy reliance on industrial meat and single-use plastics.',
        'certs': [],
        'sentiment': -0.6
    },
    'Online Fashion': {
        'score': 40, 'grade': 'C', 'sector': 'Retail', 
        'esg': [30, 40, 50], 'flags': ['Fast Fashion', 'Microplastics'], 
        'desc': 'High volume, low durability model associated with textile waste.',
        'certs': [],
        'sentiment': -0.4
    }
}

@st.cache_data
def load_merchant_data():
    """Extracts 'Merchants' from transaction data using heuristics."""
    try:
        df = pd.read_csv("Daily Household Transactions.csv")
        # Heuristic: Use Subcategory if available, else Note, else Category
        df['Merchant_Proxy'] = df['Subcategory'].fillna(df['Note']).fillna(df['Category'])
        
        # Clean up names for matching (simple demo logic)
        df['Merchant_Clean'] = df['Merchant_Proxy'].apply(lambda x: str(x).split(' ')[0] if isinstance(x, str) else 'Unknown')
        
        # Calculate Spend per Merchant
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
        df = df[df['Income/Expense'] == 'Expense']
        
        merchant_spend = df.groupby('Merchant_Proxy')['Amount'].sum().reset_index().sort_values(by='Amount', ascending=False)
        return merchant_spend
    except:
        return pd.DataFrame(columns=['Merchant_Proxy', 'Amount'])

def get_merchant_profile(name):
    # Fuzzy matching for demo purposes
    for key in MERCHANT_DB:
        if key.lower() in str(name).lower() or str(name).lower() in key.lower():
            return MERCHANT_DB[key]
    # Default random profile if not known
    return {
        'score': 50, 'grade': 'B-', 'sector': 'General', 
        'esg': [50, 50, 50], 'flags': ['Data Unavailable'], 
        'desc': 'Limited ESG disclosures available for this entity.',
        'certs': [],
        'sentiment': 0.0
    }

# -----------------------------------------------------------------------------
# 3. VISUALIZATION FUNCTIONS
# -----------------------------------------------------------------------------

def plot_radar_chart(esg_scores):
    categories = ['Environmental', 'Social', 'Governance']
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=esg_scores,
        theta=categories,
        fill='toself',
        fillcolor='rgba(0, 210, 106, 0.3)',
        line_color='#00d26a'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], color='white'),
            bgcolor='rgba(255,255,255,0.05)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=False,
        height=300,
        margin=dict(l=40, r=40, t=20, b=20)
    )
    return fig

def plot_spend_vs_sustainability(merchant_df):
    # Enrich DF with scores
    merchant_df['Score'] = merchant_df['Merchant_Proxy'].apply(lambda x: get_merchant_profile(x)['score'])
    merchant_df['Size'] = np.log(merchant_df['Amount'] + 1) * 5 # Scale bubble size
    
    fig = px.scatter(
        merchant_df.head(15), # Top 15 spend
        x="Score", 
        y="Amount",
        size="Size",
        color="Score",
        hover_name="Merchant_Proxy",
        color_continuous_scale="RdYlGn",
        text="Merchant_Proxy",
        title="Portfolio Impact Analysis: Spend vs. Sustainability"
    )
    
    fig.update_traces(textposition='top center')
    fig.update_layout(
        xaxis_title="Sustainability Score (0-100)",
        yaxis_title="Total Spend (INR)",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(255,255,255,0.05)',
        font=dict(color='white'),
        showlegend=False,
        height=400
    )
    return fig

def plot_trend_analysis():
    # Simulated Trend Data
    months = [datetime.now() - timedelta(days=30*i) for i in range(5, -1, -1)]
    dates = [d.strftime("%b %Y") for d in months]
    scores = [65, 68, 67, 72, 75, 78] # Upward trend simulation
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=scores, mode='lines+markers', line=dict(color='#00d26a', width=4), fill='tozeroy', fillcolor='rgba(0,210,106,0.1)'))
    
    fig.update_layout(
        title="Your Sustainability Score Trend",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(255,255,255,0.05)',
        font=dict(color='white'),
        xaxis=dict(showgrid=False),
        yaxis=dict(range=[0, 100], showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
        height=300
    )
    return fig

def plot_supply_chain_map():
    # Mock Supply Chain Data
    supply_data = pd.DataFrame({
        'lat': [20.5937, 35.8617, -14.2350, 51.1657, 37.0902],
        'lon': [78.9629, 104.1954, -51.9253, 10.4515, -95.7129],
        'Location': ['India (Domestic)', 'China (Assembly)', 'Brazil (Raw Materials)', 'Germany (Design)', 'USA (Tech Services)'],
        'Risk': ['Low', 'Med', 'High', 'Low', 'Low']
    })
    
    fig_map = px.scatter_geo(
        supply_data, lat='lat', lon='lon', color='Risk',
        hover_name='Location', size=[30, 20, 40, 15, 25],
        projection="natural earth",
        color_discrete_map={'Low': '#00d26a', 'Med': '#ffc107', 'High': '#dc3545'},
        title="Global Supply Chain Transparency Map (Simulated)"
    )
    fig_map.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        geo=dict(bgcolor='rgba(0,0,0,0)', showland=True, landcolor='#1f2937', showocean=True, oceancolor='#0e1117'),
        font_color='white',
        margin=dict(t=30, b=0, l=0, r=0),
        height=350
    )
    return fig_map

# -----------------------------------------------------------------------------
# 4. MAIN APP LAYOUT
# -----------------------------------------------------------------------------

def main():
    # --- HERO SECTION ---
    col_title, col_score = st.columns([2, 1])
    with col_title:
        st.title("Merchant Sustainability Index")
        st.markdown("### The Truth Behind Your Transactions")
        st.markdown("Analyze the ESG performance of the brands you fund. Identify high-risk merchants and discover greener alternatives.")
    
    # Load Data
    merchant_data = load_merchant_data()
    
    # Calculate Weighted Avg Score
    portfolio_score = 0
    if not merchant_data.empty:
        merchant_data['Score'] = merchant_data['Merchant_Proxy'].apply(lambda x: get_merchant_profile(x)['score'])
        portfolio_score = (merchant_data['Score'] * merchant_data['Amount']).sum() / merchant_data['Amount'].sum()

    with col_score:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center; padding: 10px;">
            <h4 style="margin:0; color:#aaa;">Your Portfolio Score</h4>
            <div style="font-size: 3rem; font-weight: 800; color: #00d26a;">{portfolio_score:.1f}</div>
            <span class="esg-pill pill-env">Top 15% of Users</span>
        </div>
        """, unsafe_allow_html=True)

    # --- SEARCH & OVERVIEW SECTION ---
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        col_search, col_filter = st.columns([3, 1])
        
        with col_search:
            st.subheader("🔍 Merchant Lookup")
            # Selectbox acts as a search bar with autocomplete from the data
            search_options = ["Select a merchant..."] + list(merchant_data['Merchant_Proxy'].unique())
            selected_merchant_name = st.selectbox("Search database or select from your history:", search_options, label_visibility="collapsed")
        
        with col_filter:
            st.subheader("Filter View")
            st.selectbox("Filter by Sector", ["All Sectors", "Retail", "Food", "Transport", "Tech"], label_visibility="collapsed")
            
        st.markdown('</div>', unsafe_allow_html=True)

    # --- MERCHANT DETAIL VIEW (Dynamic) ---
    if selected_merchant_name and selected_merchant_name != "Select a merchant...":
        profile = get_merchant_profile(selected_merchant_name)
        
        # Color logic for grade
        grade_cls = "grade-B"
        if "A" in profile['grade']: grade_cls = "grade-A"
        if "C" in profile['grade'] or "D" in profile['grade']: grade_cls = "grade-C"
        
        st.markdown(f"## 🏢 {selected_merchant_name}")
        
        # Detail Columns
        col_profile1, col_profile2, col_profile3 = st.columns([1, 1.5, 1.5])
        
        # 1. SCORE CARD
        with col_profile1:
            st.markdown(f"""
            <div style="display:flex; flex-direction:column; align-items:center;">
                <div class="grade-circle {grade_cls}">{profile['grade']}</div>
                <h4 style="margin-top:10px;">{profile['score']} / 100</h4>
                <p style="color:#aaa; font-size:0.9rem;">Sustainability Rating</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("")
            st.markdown("**Risk Flags:**")
            if profile['flags']:
                for flag in profile['flags']:
                    st.markdown(f"⚠️ `{flag}`")
            else:
                st.markdown("✅ No major flags")
                
            if profile['certs']:
                st.markdown("**Certifications:**")
                for cert in profile['certs']:
                    st.markdown(f"""<span class="cert-badge">🏅 {cert}</span>""", unsafe_allow_html=True)

        # 2. RADAR & METRICS
        with col_profile2:
            st.markdown("**ESG Performance Breakdown**")
            st.plotly_chart(plot_radar_chart(profile['esg']), use_container_width=True)
            
            st.markdown(f"""
            <div style="text-align:center;">
                <span class="esg-pill pill-env">Env: {profile['esg'][0]}</span>
                <span class="esg-pill pill-soc">Soc: {profile['esg'][1]}</span>
                <span class="esg-pill pill-gov">Gov: {profile['esg'][2]}</span>
            </div>
            """, unsafe_allow_html=True)

        # 3. ANALYSIS & ALTERNATIVES
        with col_profile3:
            st.markdown("**AI Truth Lens 👁️**")
            st.info(profile['desc'])
            
            # Sentiment Analysis Bar
            st.markdown("**Public Sentiment**")
            st.progress(max(0.0, min(1.0, (profile['sentiment'] + 1) / 2)))
            
            if profile['score'] < 70:
                st.markdown("### 🌱 Greener Swaps")
                st.markdown(f"Switching from *{selected_merchant_name}* could save CO2.")
                
                # Dynamic suggestions based on sector
                if profile['sector'] == 'Food':
                    st.success("👉 **Local Farmers Market**: 95/100 (Saves ~4kg CO2/meal)")
                elif profile['sector'] == 'Retail':
                    st.success("👉 **Thrift/Second-hand**: 92/100 (Circular Economy)")
                elif profile['sector'] == 'Transport':
                    st.success("👉 **Public Metro**: 98/100 (80% less emissions)")
                else:
                    st.success("👉 **Certified B-Corp Alternative**: 90/100")
            else:
                st.balloons()
                st.success("🌟 **Great Choice!** This merchant is a sustainability leader in their sector.")

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    # --- PORTFOLIO INTELLIGENCE (All in One Page) ---
    st.markdown("## 📈 Portfolio Intelligence")
    st.markdown("Deep dive analytics into your spending habits across the entire merchant ecosystem.")
    
    # Row 1: Spend Map & Supply Chain
    row1_c1, row1_c2 = st.columns(2)
    
    with row1_c1:
        st.markdown("### 💰 Spend vs. Sustainability")
        st.markdown("Are you spending more on low-scoring merchants? Bubbles represent transaction volume.")
        st.plotly_chart(plot_spend_vs_sustainability(merchant_data), use_container_width=True)
        
    with row1_c2:
        st.markdown("### 🔗 Supply Chain Transparency")
        st.markdown("Tracing the likely origin of products associated with your top merchants based on sector averages.")
        st.plotly_chart(plot_supply_chain_map(), use_container_width=True)

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

    # Row 2: Trend & Community
    row2_c1, row2_c2 = st.columns([1.5, 1])
    
    with row2_c1:
        st.markdown("### 📊 Sustainability Trend")
        st.markdown("Tracking the improvement of your portfolio score over the last 6 months.")
        st.plotly_chart(plot_trend_analysis(), use_container_width=True)
        
    with row2_c2:
        st.markdown("### 🗣️ Community & Alerts")
        st.markdown("""
        <div class="glass-card">
            <h4>Top Rated by Community</h4>
            <ol>
                <li>🌿 <b>Organic Harvest</b> (4.9 ⭐)</li>
                <li>🚲 <b>City Cycles</b> (4.8 ⭐)</li>
                <li>☀️ <b>Solarify</b> (4.7 ⭐)</li>
            </ol>
            <hr style="border-color:rgba(255,255,255,0.1)">
            <h4>Greenwashing Alerts ⚠️</h4>
            <ul>
                <li>❌ <b>FastFashionCo</b>: Claims 'Sustainable' but failed transparency audit.</li>
                <li>❌ <b>EcoWater</b>: Plastic bottles labeled as 'Green'.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # --- ADVANCED FEATURE: IMPACT SIMULATOR ---
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    st.markdown("## 🎛️ Impact Simulator")
    
    sim_col1, sim_col2 = st.columns([1, 2])
    with sim_col1:
        st.markdown("If you shifted your spending from Grade C merchants to Grade A merchants, how much would your score improve?")
        shift_pct = st.slider("Shift Spending %", 0, 100, 20)
    
    with sim_col2:
        projected_score = min(100, portfolio_score + (shift_pct * 0.3)) # Simple simulation logic
        improvement = projected_score - portfolio_score
        
        st.markdown(f"""
        <div class="glass-card" style="display:flex; justify-content:space-around; align-items:center;">
            <div>
                <h4 style="margin:0; color:#aaa;">Current Score</h4>
                <div style="font-size: 2rem; font-weight: 700; color: white;">{portfolio_score:.1f}</div>
            </div>
            <div style="font-size: 2rem;">➡️</div>
            <div>
                <h4 style="margin:0; color:#aaa;">Projected Score</h4>
                <div style="font-size: 2rem; font-weight: 700; color: #00d26a;">{projected_score:.1f}</div>
            </div>
            <div style="background:rgba(0,210,106,0.2); padding:10px 20px; border-radius:10px; color:#00d26a; font-weight:bold;">
                +{improvement:.1f} Points
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br><br>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()