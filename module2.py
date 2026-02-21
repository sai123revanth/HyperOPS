import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import textwrap
from groq import Groq  # Import Groq for the AI Chatbot

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Ecopay | Carbon Offset Marketplace",
    page_icon="🌍",
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
    
    /* Heading Adjustments */
    .stApp h1 {
        font-family: 'Inter', sans-serif;
        color: white;
        font-size: 2.2rem !important; 
        font-weight: 800;
        letter-spacing: -1px;
        white-space: nowrap; 
        overflow: hidden;
        text-overflow: ellipsis;
        padding-top: 10px;
    }
    
    /* =========================================
       CART POPOVER STYLING (Top Right)
       ========================================= */
    div.element-container:has(.cart-marker) + div.element-container div[data-testid="stPopover"] {
        position: fixed !important;
        top: 55px !important; 
        right: 40px !important;
        z-index: 999999 !important; 
        width: auto !important;
    }
    
    div.element-container:has(.cart-marker) + div.element-container div[data-testid="stPopover"] > div > button {
        width: 65px !important;
        height: 65px !important;
        border-radius: 50% !important; 
        background: linear-gradient(135deg, #00d26a 0%, #00b359 100%) !important;
        color: white !important;
        border: 2px solid rgba(255,255,255,0.2) !important;
        box-shadow: 0 10px 25px rgba(0, 210, 106, 0.6) !important;
        padding: 0 !important;
        font-size: 1.2rem !important;
        font-weight: bold !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    }
    
    div.element-container:has(.cart-marker) + div.element-container div[data-testid="stPopover"] > div > button:hover {
        transform: translateY(-8px) scale(1.1) !important;
        box-shadow: 0 20px 40px rgba(0, 210, 106, 0.8) !important;
        border-color: white !important;
    }

    div.element-container:has(.cart-marker) + div.element-container div[data-testid="stPopover"] > div > button > div {
        display: flex;
        flex-direction: column;
        align-items: center;
        line-height: 1;
    }

    /* =========================================
       CHATBOT POPOVER STYLING (Bottom Left)
       ========================================= */
    div.element-container:has(.chat-marker) + div.element-container div[data-testid="stPopover"] {
        position: fixed !important;
        bottom: 40px !important; 
        left: 40px !important;
        z-index: 999999 !important; 
        width: auto !important;
    }
    
    div.element-container:has(.chat-marker) + div.element-container div[data-testid="stPopover"] > div > button {
        width: 65px !important;
        height: 65px !important;
        border-radius: 50% !important; 
        background: linear-gradient(135deg, #007bb5 0%, #00a8e8 100%) !important;
        color: white !important;
        border: 2px solid rgba(255,255,255,0.2) !important;
        box-shadow: 0 10px 25px rgba(0, 168, 232, 0.6) !important;
        padding: 0 !important;
        font-size: 1.8rem !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    }
    
    div.element-container:has(.chat-marker) + div.element-container div[data-testid="stPopover"] > div > button:hover {
        transform: translateY(-8px) scale(1.1) !important;
        box-shadow: 0 20px 40px rgba(0, 168, 232, 0.8) !important;
        border-color: white !important;
    }

    /* Widen the Chatbot Popover Body */
    div.element-container:has(.chat-marker) + div.element-container [data-testid="stPopoverBody"] {
        width: 450px !important;
        max-width: 90vw !important;
        border-radius: 16px;
        border: 1px solid #374151;
        box-shadow: 0 20px 50px rgba(0,0,0,0.6);
    }

    /* Advanced Project Card Container */
    .project-card-container {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        display: flex;
        flex-direction: column;
        height: 100%;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        margin-bottom: 10px;
    }
    
    .project-card-container:hover {
        transform: translateY(-8px) scale(1.01);
        border-color: #00d26a;
        box-shadow: 0 20px 40px rgba(0, 210, 106, 0.15);
    }

    .project-image {
        width: 100%;
        height: 180px;
        object-fit: cover;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        filter: brightness(0.9);
        transition: filter 0.3s ease;
    }
    
    .project-card-container:hover .project-image {
        filter: brightness(1.1);
    }

    .card-content {
        padding: 20px;
        flex-grow: 1;
        display: flex;
        flex-direction: column;
    }

    h3.project-title {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 1.2rem;
        margin: 0 0 10px 0;
        color: #ffffff;
        line-height: 1.4;
        min-height: 3.4em;
    }

    p.project-desc {
        font-family: 'Inter', sans-serif;
        color: #b0b8c3;
        font-size: 0.9rem;
        line-height: 1.6;
        margin-bottom: 15px;
        flex-grow: 1;
    }

    div[data-testid="stMetric"] {
        background: rgba(17, 24, 39, 0.7);
        border: 1px solid rgba(0, 168, 232, 0.3);
        border-left: 4px solid #00a8e8;
        padding: 15px;
        border-radius: 10px;
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 1.6rem;
        color: white;
    }

    .badge {
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-right: 6px;
        display: inline-block;
        margin-bottom: 8px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .badge-forest { background-color: rgba(25, 135, 84, 0.2); color: #75b798; border-color: #198754; }
    .badge-energy { background-color: rgba(255, 193, 7, 0.1); color: #ffca2c; border-color: #ffc107; }
    .badge-methane { background-color: rgba(220, 53, 69, 0.2); color: #ea868f; border-color: #dc3545; }
    .badge-community { background-color: rgba(13, 110, 253, 0.2); color: #6ea8fe; border-color: #0d6efd; }
    .badge-blue { background-color: rgba(13, 202, 240, 0.2); color: #3dd5f3; border-color: #0dcaf0; }
    
    .meta-tag {
        background: rgba(255,255,255,0.05); 
        padding: 4px 8px; 
        border-radius: 6px; 
        font-size: 0.8rem;
        color: #e0e0e0;
        display: inline-flex;
        align-items: center;
        gap: 5px;
        border: 1px solid rgba(255,255,255,0.05);
    }

    .price-section {
        margin-top: 15px;
        padding-top: 15px;
        border-top: 1px solid rgba(255,255,255,0.1);
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
    }

    div.stButton > button:first-child {
        background-color: #00d26a;
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        width: 100%;
        transition: background-color 0.2s;
    }
    div.stButton > button:first-child:hover {
        background-color: #00b359;
        border-color: #00b359;
        box-shadow: 0 4px 12px rgba(0, 210, 106, 0.4);
    }

    [data-testid="stPopoverBody"] {
        background-color: #0e1117;
        color: white;
        border: 1px solid #374151;
        box-shadow: 0 10px 40px rgba(0,0,0,0.5);
    }
    
    .filter-container {
        background-color: rgba(255, 255, 255, 0.05);
        padding: 24px;
        border-radius: 12px;
        margin-bottom: 30px;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: rgba(255,255,255,0.02);
        border-radius: 8px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 30px;
        white-space: pre-wrap;
        border-radius: 6px;
        color: #aaa;
        font-size: 0.8rem;
        padding: 0 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(255,255,255,0.1) !important;
        color: #fff !important;
    }
    
    h2, h3, h4 { font-family: 'Inter', sans-serif; color: white; }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. DATA SIMULATION (Connecting to Engine Logic)
# -----------------------------------------------------------------------------

@st.cache_data
def load_user_footprint():
    """
    Simulates fetching the user's calculated footprint from the Engine module.
    In a real app, this would pull from a shared database/state.
    """
    try:
        df = pd.read_csv("Daily Household Transactions.csv")
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
        df = df[df['Income/Expense'] == 'Expense']
        
        total_spend = df['Amount'].sum()
        estimated_carbon_kg = total_spend * 0.08 
        return estimated_carbon_kg
    except:
        return 1250.00 # Fallback default

# Extensive Project Database (20+ Projects)
PROJECTS = [
    {
        "id": 1,
        "name": "Sundarbans Mangrove Restoration",
        "location": "West Bengal, India",
        "type": "Reforestation",
        "registry": "Verra (VCS)",
        "vintage": 2023,
        "price_per_tonne": 1200, 
        "rating": "AAA",
        "sdgs": ["13", "14", "15"],
        "description": "Restoring critical mangrove ecosystems that act as massive carbon sinks and protect against cyclones. Supports local biodiversity including the Bengal Tiger.",
        "lat": 21.9497, "lon": 88.8993,
        "funded_percent": 78
    },
    {
        "id": 2,
        "name": "Rajasthan Solar Park Initiative",
        "location": "Rajasthan, India",
        "type": "Renewable Energy",
        "registry": "Gold Standard",
        "vintage": 2024,
        "price_per_tonne": 650,
        "rating": "A+",
        "sdgs": ["7", "9", "13"],
        "description": "Replacing coal-fired grid electricity with clean solar power, creating local engineering jobs in the desert region of Bhadla.",
        "lat": 27.0238, "lon": 74.2179,
        "funded_percent": 45
    },
    {
        "id": 3,
        "name": "Clean Cookstoves for Rural Families",
        "location": "Odisha, India",
        "type": "Community",
        "registry": "Gold Standard",
        "vintage": 2023,
        "price_per_tonne": 950,
        "rating": "AA",
        "sdgs": ["3", "5", "13"],
        "description": "Distributing efficient cookstoves to reduce wood burning, significantly improving indoor air quality for women and children.",
        "lat": 20.9517, "lon": 85.0985,
        "funded_percent": 92
    },
    {
        "id": 4,
        "name": "Urban Landfill Methane Capture",
        "location": "Delhi, India",
        "type": "Methane Capture",
        "registry": "CDM (UN)",
        "vintage": 2022,
        "price_per_tonne": 800,
        "rating": "A",
        "sdgs": ["11", "13"],
        "description": "Capturing methane from waste decomposition to generate electricity and prevent potent GHG release into the atmosphere.",
        "lat": 28.7041, "lon": 77.1025,
        "funded_percent": 60
    },
    {
        "id": 5,
        "name": "Tamil Nadu Wind Power Project",
        "location": "Tamil Nadu, India",
        "type": "Renewable Energy",
        "registry": "Verra (VCS)",
        "vintage": 2023,
        "price_per_tonne": 700,
        "rating": "A",
        "sdgs": ["7", "13"],
        "description": "Large scale wind farms generating clean energy for the southern grid, offsetting thermal power dependency.",
        "lat": 8.5241, "lon": 77.5892,
        "funded_percent": 85
    },
    {
        "id": 6,
        "name": "Himalayan Hydroelectric Run-of-River",
        "location": "Himachal Pradesh, India",
        "type": "Renewable Energy",
        "registry": "CDM (UN)",
        "vintage": 2024,
        "price_per_tonne": 750,
        "rating": "A-",
        "sdgs": ["7", "6", "13"],
        "description": "Sustainable hydro power using natural river flow without large dams, minimizing ecosystem disruption in the mountains.",
        "lat": 31.1048, "lon": 77.1734,
        "funded_percent": 40
    },
    {
        "id": 7,
        "name": "Kerala Blue Carbon Seagrass",
        "location": "Kerala, India",
        "type": "Reforestation",
        "registry": "Verra (VCS)",
        "vintage": 2023,
        "price_per_tonne": 1400,
        "rating": "AAA",
        "sdgs": ["14", "13"],
        "description": "Restoring seagrass beds which sequester carbon 35x faster than tropical rainforests and support fisheries.",
        "lat": 9.9312, "lon": 76.2673,
        "funded_percent": 30
    },
    {
        "id": 8,
        "name": "Indore Bio-CNG from Waste",
        "location": "Madhya Pradesh, India",
        "type": "Methane Capture",
        "registry": "Gold Standard",
        "vintage": 2023,
        "price_per_tonne": 1100,
        "rating": "AA+",
        "sdgs": ["11", "12", "7"],
        "description": "Converting municipal wet waste into Bio-CNG for public buses, solving waste and energy issues simultaneously.",
        "lat": 22.7196, "lon": 75.8577,
        "funded_percent": 95
    },
    {
        "id": 9,
        "name": "Safe Water Project",
        "location": "Assam, India",
        "type": "Community",
        "registry": "Gold Standard",
        "vintage": 2024,
        "price_per_tonne": 1000,
        "rating": "AA",
        "sdgs": ["6", "3", "13"],
        "description": "Providing water filters to eliminate the need for boiling water with firewood, saving forests and time.",
        "lat": 26.2006, "lon": 92.9376,
        "funded_percent": 55
    },
    {
        "id": 10,
        "name": "Regenerative Agriculture Cotton",
        "location": "Maharashtra, India",
        "type": "Reforestation",
        "registry": "Verra (VCS)",
        "vintage": 2023,
        "price_per_tonne": 1300,
        "rating": "AAA",
        "sdgs": ["12", "15", "1"],
        "description": "Supporting farmers to switch to organic, regenerative cotton farming that sequesters carbon in soil.",
        "lat": 19.7515, "lon": 75.7139,
        "funded_percent": 65
    },
    {
        "id": 11,
        "name": "Amazon Rainforest Protection",
        "location": "Brazil",
        "type": "Reforestation",
        "registry": "Verra (VCS)",
        "vintage": 2022,
        "price_per_tonne": 1600,
        "rating": "AAA+",
        "sdgs": ["15", "13"],
        "description": "REDD+ project preventing deforestation in high-risk zones of the Amazon basin. A vital global carbon sink.",
        "lat": -3.4653, "lon": -62.2159,
        "funded_percent": 88
    },
    {
        "id": 12,
        "name": "Gujarat Coastal Wind Farms",
        "location": "Gujarat, India",
        "type": "Renewable Energy",
        "registry": "CDM (UN)",
        "vintage": 2023,
        "price_per_tonne": 680,
        "rating": "A",
        "sdgs": ["7", "13", "8"],
        "description": "Onshore wind farms utilizing high wind speeds along the western coast to power industrial zones.",
        "lat": 22.2587, "lon": 71.1924,
        "funded_percent": 70
    },
    {
        "id": 13,
        "name": "Rice Husk Biomass Power",
        "location": "Punjab, India",
        "type": "Renewable Energy",
        "registry": "Gold Standard",
        "vintage": 2024,
        "price_per_tonne": 720,
        "rating": "A+",
        "sdgs": ["7", "12", "13"],
        "description": "Using agricultural residue (rice husk) for power generation instead of burning it in fields, reducing smog.",
        "lat": 31.1471, "lon": 75.3412,
        "funded_percent": 50
    },
    {
        "id": 14,
        "name": "Bangalore Urban Tree Cover",
        "location": "Karnataka, India",
        "type": "Reforestation",
        "registry": "Local/Verra",
        "vintage": 2024,
        "price_per_tonne": 1500,
        "rating": "AA",
        "sdgs": ["11", "15", "3"],
        "description": "Urban afforestation project to combat heat island effect and restore the 'Garden City' reputation.",
        "lat": 12.9716, "lon": 77.5946,
        "funded_percent": 25
    },
    {
        "id": 15,
        "name": "Bihar LED Distribution",
        "location": "Bihar, India",
        "type": "Community",
        "registry": "CDM (UN)",
        "vintage": 2022,
        "price_per_tonne": 600,
        "rating": "B+",
        "sdgs": ["7", "13"],
        "description": "Replacing inefficient incandescent bulbs with high-quality LEDs in rural households.",
        "lat": 25.0961, "lon": 85.3131,
        "funded_percent": 98
    },
    {
        "id": 16,
        "name": "Kenya Geothermal Expansion",
        "location": "Kenya",
        "type": "Renewable Energy",
        "registry": "Gold Standard",
        "vintage": 2023,
        "price_per_tonne": 900,
        "rating": "AAA",
        "sdgs": ["7", "13"],
        "description": "Harnessing the Rift Valley's geothermal potential for constant, clean baseload power.",
        "lat": -0.0236, "lon": 37.9062,
        "funded_percent": 82
    },
    {
        "id": 17,
        "name": "Eastern Ghats Coffee Agroforestry",
        "location": "Andhra Pradesh, India",
        "type": "Reforestation",
        "registry": "Verra (VCS)",
        "vintage": 2023,
        "price_per_tonne": 1250,
        "rating": "AA+",
        "sdgs": ["15", "1", "13"],
        "description": "Shade-grown coffee plantations that maintain canopy cover and biodiversity in tribal areas.",
        "lat": 17.6868, "lon": 83.2185,
        "funded_percent": 60
    },
    {
        "id": 18,
        "name": "Industrial Waste Heat Recovery",
        "location": "Jharkhand, India",
        "type": "Methane Capture",
        "registry": "CDM (UN)",
        "vintage": 2022,
        "price_per_tonne": 550,
        "rating": "A",
        "sdgs": ["9", "12", "13"],
        "description": "Capturing waste heat from steel plants to generate electricity, reducing grid dependency.",
        "lat": 23.6913, "lon": 85.2722,
        "funded_percent": 90
    },
    {
        "id": 19,
        "name": "Solar Water Pumps for Farmers",
        "location": "Telangana, India",
        "type": "Renewable Energy",
        "registry": "Gold Standard",
        "vintage": 2024,
        "price_per_tonne": 850,
        "rating": "AA",
        "sdgs": ["2", "7", "13"],
        "description": "Replacing diesel pumps with solar pumps for irrigation, reducing fossil fuel use and costs.",
        "lat": 18.1124, "lon": 79.0193,
        "funded_percent": 35
    },
    {
        "id": 20,
        "name": "Indonesian Peatland Conservation",
        "location": "Indonesia",
        "type": "Reforestation",
        "registry": "Verra (VCS)",
        "vintage": 2023,
        "price_per_tonne": 1800,
        "rating": "AAA+",
        "sdgs": ["13", "15"],
        "description": "Protecting carbon-rich peat swamp forests from drainage and conversion to palm oil.",
        "lat": -0.7893, "lon": 113.9213,
        "funded_percent": 75
    }
]

# -----------------------------------------------------------------------------
# 3. HELPER FUNCTIONS
# -----------------------------------------------------------------------------

def calculate_equivalence(kg_co2):
    return {
        "trees": kg_co2 / 21,  
        "car_km": kg_co2 / 0.12, 
        "smartphones": kg_co2 / 0.008 
    }

def get_badge_class(ptype):
    if ptype == "Reforestation": return "badge-forest"
    if ptype == "Renewable Energy": return "badge-energy"
    if ptype == "Methane Capture": return "badge-methane"
    if ptype == "Community": return "badge-community"
    return "badge-blue"

def get_project_image(ptype, seed=1):
    if ptype == "Reforestation":
        return f"https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80" 
    elif ptype == "Renewable Energy":
        return f"https://images.unsplash.com/photo-1509391366360-2e959784a276?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80" 
    elif ptype == "Methane Capture":
        return f"https://images.unsplash.com/photo-1518709268805-4e9042af9f23?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80" 
    elif ptype == "Community":
        return f"https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80" 
    return f"https://images.unsplash.com/photo-1497436072909-60f360e1d4b0?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80" 

# -----------------------------------------------------------------------------
# 4. MAIN APP LAYOUT
# -----------------------------------------------------------------------------

def main():
    col_logo, col_space = st.columns([8, 2])
    
    with col_logo:
        st.title("Ecopay Offset Marketplace")
        st.markdown("##### Global Carbon Registry Access")
    
    if 'cart' not in st.session_state:
        st.session_state.cart = []
    
    cart_count = len(st.session_state.cart)
    
    # === CART POPOVER (TOP RIGHT) ===
    st.markdown('<div class="cart-marker"></div>', unsafe_allow_html=True)
    with st.popover(f"🛒 {cart_count}", help="View your selected offsets"):
        st.markdown("### Your Impact Basket")
        
        if not st.session_state.cart:
            st.info("Your cart is empty. Add projects to offset your footprint.")
        else:
            cart_total_cost = 0
            cart_total_offset = 0
            
            for i, item in enumerate(st.session_state.cart):
                cost = item['amount'] * (item['price'] / 1000)
                
                with st.container():
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown(f"**{item['name']}**")
                        st.caption(f"{item['amount']:.0f} kg • ₹{cost:.0f}")
                    with c2:
                        if st.button("🗑️", key=f"del_{i}"):
                            st.session_state.cart.pop(i)
                            st.rerun()
                
                cart_total_cost += cost
                cart_total_offset += item['amount']
                st.markdown("---")
            
            st.metric("Total to Pay", f"₹{cart_total_cost:,.0f}")
            st.success(f"Offsets: {cart_total_offset:,.0f} kg CO₂e")
            
            if st.button("Complete Purchase", type="primary"):
                st.balloons()
                st.session_state.cart = []
                st.success("Offset Certificate Generated! Check your email.")

    # --- TOP FILTERS ---
    with st.container():
        st.markdown("""<div class="filter-container">""", unsafe_allow_html=True)
        f_col1, f_col2 = st.columns([2, 1])
        
        with f_col1:
            selected_types = st.multiselect(
                "🔍 Filter by Project Type",
                ["Reforestation", "Renewable Energy", "Community", "Methane Capture"],
                default=["Reforestation", "Renewable Energy"]
            )
        
        with f_col2:
            max_price_limit = 2000
            max_price = st.slider("💰 Max Price (₹/tonne)", 0, max_price_limit, 2000)
        st.markdown("</div>", unsafe_allow_html=True)

    # --- Main Content ---
    st.markdown("### Close the Loop: Neutralize Your Residual Footprint")
    st.markdown("Invest in verified, high-impact climate projects to balance out emissions that cannot be reduced through behavioral change.")
    
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    
    current_footprint = load_user_footprint()
    offsets_in_cart = sum(item['amount'] for item in st.session_state.cart)
    net_gap = max(0, current_footprint - offsets_in_cart)
    
    with col_stat1:
        st.metric("Your Footprint (YTD)", f"{current_footprint:,.0f} kg", delta="Measured via Engine")
    with col_stat2:
        st.metric("Offset Status", f"{offsets_in_cart:,.0f} kg", delta=f"{offsets_in_cart/current_footprint*100:.1f}% Neutralized")
    with col_stat3:
        eq = calculate_equivalence(net_gap)
        st.metric("Net Zero Gap", f"{net_gap:,.0f} kg", delta="Remaining to Offset", delta_color="inverse")
        
    st.markdown(textwrap.dedent(f"""
    <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; margin-top: 10px; display: flex; justify-content: space-around; align-items: center; flex-wrap: wrap;">
    <span style="font-size: 1.1rem; margin: 5px;">⚠️ <b>{net_gap:,.0f} kg</b> Gap is equivalent to:</span>
    <span style="color: #00d26a; font-weight: bold; margin: 5px;">🌲 {eq['trees']:.0f} Mature Trees</span>
    <span style="color: #ffc107; font-weight: bold; margin: 5px;">🚗 {eq['car_km']:.0f} km Driven</span>
    <span style="color: #0d6efd; font-weight: bold; margin: 5px;">📱 {eq['smartphones']:.0f} Charges</span>
    </div>
    <br>
    """), unsafe_allow_html=True)

    # 2. GLOBAL PROJECT MAP
    st.subheader("🌏 Global Project Tracker")
    
    filtered_projects = [p for p in PROJECTS if p['type'] in selected_types and p['price_per_tonne'] <= max_price]
    
    if filtered_projects:
        map_df = pd.DataFrame(filtered_projects)
        fig_map = px.scatter_geo(
            map_df,
            lat='lat',
            lon='lon',
            color='type',
            hover_name='name',
            size='price_per_tonne',
            projection="natural earth",
            title="Verified Project Locations",
            color_discrete_map={
                "Reforestation": "#198754", 
                "Renewable Energy": "#ffc107", 
                "Community": "#0d6efd", 
                "Methane Capture": "#dc3545"
            }
        )
        fig_map.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            geo=dict(bgcolor="rgba(0,0,0,0)", showland=True, landcolor="#1f2937", showocean=True, oceancolor="#0e1117"),
            font_color="white",
            margin=dict(l=0, r=0, t=30, b=0),
            height=300
        )
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.warning("No projects match your current filters. Try adjusting the price or category.")

    # 3. PROJECT LISTINGS
    st.subheader("🌿 Featured Projects")
    st.markdown(f"Showing {len(filtered_projects)} verified projects available for immediate funding.")

    cols = st.columns(2)
    
    for idx, project in enumerate(filtered_projects):
        col = cols[idx % 2]
        with col:
            badge_cls = get_badge_class(project['type'])
            img_url = get_project_image(project['type'], seed=project['id'])
            
            card_html = textwrap.dedent(f"""
            <div class="project-card-container">
            <img src="{img_url}" class="project-image" alt="{project['name']}">
            <div class="card-content">
            <div>
            <h3 class="project-title">{project['name']}</h3>
            <div>
            <span class="badge {badge_cls}">{project['type']}</span>
            <span class="meta-tag">🛡️ {project['registry']}</span>
            </div>
            <p style="color:#aaa; font-size:0.85rem; margin: 8px 0;">📍 {project['location']}</p>
            <p class="project-desc">{project['description']}</p>
            <div style="display:flex; gap:6px; flex-wrap:wrap; margin-top: auto;">
            <span class="meta-tag">🇺🇳 SDGs: {', '.join(project['sdgs'])}</span>
            <span class="meta-tag">📅 {project['vintage']}</span>
            <span class="meta-tag">⭐ {project['rating']}</span>
            </div>
            </div>
            <div class="price-section">
            <div>
            <span style="font-size:1.4rem; font-weight:bold; color:#00d26a;">₹{project['price_per_tonne']}</span>
            <span style="color:#aaa; font-size:0.8rem;"> / tonne</span>
            </div>
            <div style="text-align:right;">
            <span style="font-size:0.8rem; color:#aaa;">Funded</span><br>
            <span style="font-weight:bold; color:#0dcaf0;">{project['funded_percent']}%</span>
            </div>
            </div>
            </div>
            </div>
            """)
            st.markdown(card_html, unsafe_allow_html=True)
            
            with st.container():
                st.markdown('<div style="margin-top: 10px;"></div>', unsafe_allow_html=True) 
                
                tabs = st.tabs(["Purchase", "Validation", "Impact"])
                
                with tabs[0]:
                    c1, c2 = st.columns([2, 1])
                    with c1:
                        offset_amount = st.slider(f"Amount (kg)", 0, 2000, 100, key=f"slider_{project['id']}", label_visibility="collapsed")
                        cost = offset_amount * (project['price_per_tonne'] / 1000)
                        st.caption(f"Offset: **{offset_amount} kg** | Cost: **₹{cost:.0f}**")
                    with c2:
                        st.write("") 
                        if st.button(f"Add 🛒", key=f"btn_{project['id']}"):
                            st.session_state.cart.append({
                                "name": project['name'],
                                "amount": offset_amount,
                                "price": project['price_per_tonne']
                            })
                            st.rerun()
                
                with tabs[1]:
                    st.markdown(f"**Registry:** {project['registry']}")
                    st.markdown(f"**Vintage:** {project['vintage']}")
                    st.markdown("**Verification Status:** ✅ Verified")
                    st.info("This project meets international carbon standards.")
                    
                with tabs[2]:
                    st.markdown("**SDG Alignment:**")
                    st.markdown(f"This project contributes to goals {', '.join(project['sdgs'])}.")
                    st.progress(project['funded_percent']/100, text="Funding Goal")
            
            st.markdown("---")

    # 4. EDUCATIONAL FOOTER
    st.markdown("---")
    st.subheader("📚 Verified Carbon Standard (VCS) Explained")
    
    with st.expander("What makes a 'Good' offset?", expanded=True):
        e1, e2, e3 = st.columns(3)
        with e1:
            st.info("**Additionality**\nThe project would not have happened without the funding from these carbon credits. It is 'additional' to business-as-usual.")
        with e2:
            st.info("**Permanence**\nThe CO2 removed is kept out of the atmosphere for a long time (e.g., 100+ years). Reversal risk is managed via insurance buffers.")
        with e3:
            st.info("**No Leakage**\nProtecting a forest here doesn't just move the logging to a neighboring forest. The net impact is globally positive.")

    # Extra space for scrolling at the bottom
    st.markdown("<br>" * 5, unsafe_allow_html=True)

    # =========================================================================
    # 5. FLOATING AI CHATBOT IMPLEMENTATION (BOTTOM LEFT)
    # =========================================================================
    
    # Initialize Chat Messages
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Namaste! 🙏 I am Ecopay AI. I can speak English, Hindi, Bengali, Tamil, Telugu, and all other Indian languages. How can I assist you with carbon offsets today?"}
        ]

    st.markdown('<div class="chat-marker"></div>', unsafe_allow_html=True)
    with st.popover("💬", help="Chat with Ecopay AI"):
        st.markdown("### Ecopay Sustainability Assistant")
        st.caption("Powered by Groq ✨")
        
        # Chat container
        chat_container = st.container(height=400)
        with chat_container:
            for msg in st.session_state.chat_messages:
                if msg["role"] != "system":
                    st.chat_message(msg["role"]).write(msg["content"])
        
        # Chat input box
        if prompt := st.chat_input("Ask about projects or sustainability..."):
            
            # Display user message instantly
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            st.rerun() # Trigger rerun to show user message before fetching from API

        # Process the last user message if it needs a response
        if len(st.session_state.chat_messages) > 0 and st.session_state.chat_messages[-1]["role"] == "user":
            try:
                # Initialize Groq Client
                client = Groq(api_key=st.secrets["Groq_Offset"])
                
                # System Prompt enforcing Indian Language Support
                system_prompt = """You are Ecopay's AI Assistant, an expert in carbon offsets, sustainability, and climate change in the Indian context. 
                CRITICAL INSTRUCTION: You must detect the language the user is speaking and reply fluently in THAT SAME LANGUAGE. You support all Indian languages including Hindi, Bengali, Tamil, Telugu, Marathi, Gujarati, Kannada, Malayalam, Odia, Punjabi, as well as English.
                Keep your responses polite, encouraging, concise, and helpful."""
                
                api_messages = [{"role": "system", "content": system_prompt}] + [
                    {"role": m["role"], "content": m["content"]} for m in st.session_state.chat_messages
                ]
                
                # Fetch Response
                with st.spinner("AI is typing..."):
                    response = client.chat.completions.create(
                        model="llama3-70b-8192", # Excellent multilingual support
                        messages=api_messages,
                        temperature=0.6,
                        max_tokens=400
                    )
                
                bot_reply = response.choices[0].message.content
                st.session_state.chat_messages.append({"role": "assistant", "content": bot_reply})
                st.rerun()
                
            except Exception as e:
                st.error(f"Error connecting to AI: {e}")

if __name__ == "__main__":
    main()