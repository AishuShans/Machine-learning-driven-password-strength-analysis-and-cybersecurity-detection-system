import streamlit as st
from utils.style import apply_master_theme #import your master theme
# 1. Page Configuration
st.set_page_config(page_title="Cyber-Sentinel AI", layout="wide", page_icon="🛡️")
apply_master_theme()
# 2. Master Purple UI Theme (CSS)
st.markdown("""
    <style>
    /* Dark Background Gradient */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: white;
    }
    
    /* Neon Purple Glow Headers */
    h1, h2, h3 {
        color: #a855f7 !important;
        text-shadow: 0 0 15px rgba(168, 85, 247, 0.6);
        font-family: 'Arial', sans-serif;
    }

    /* Gradient Buttons */
    div.stButton > button {
        background: linear-gradient(90deg, #a855f7 0%, #00cfff 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: bold;
        transition: 0.3s;
        width: 100%;
    }
    div.stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 20px rgba(168, 85, 247, 0.4);
        color: white;
    }

    /* Glassmorphism Metric Cards */
    div[data-testid="stMetricBlock"] {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(168, 85, 247, 0.3);
        border-radius: 15px !important;
        padding: 15px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    div[data-testid="stMetricLabel"] {
        color: #00cfff !important;
    }
    div[data-testid="stMetricValue"] {
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Header Section
st.title("🛡️ Cyber-Sentinel Intelligence System")
st.subheader("Next-Gen AI Security Operations Center")
st.write("---")

# 4. Dynamic Metrics Row
c1, c2, c3, c4 = st.columns(4)
c1.metric("Security Level", "98.2%", "Optimized")
c2.metric("Threats Deflected", "1,240", "Active")
c3.metric("System Uptime", "99.9%", "Stable")
c4.metric("Active Honeypots", "12", "Live")

st.write("---")
st.info("Welcome, Operative. Please use the sidebar to navigate the intelligence modules.")

# --- NAVIGATION TILES ---
st.write("<br>", unsafe_allow_html=True)
col_nav1, col_nav2, col_nav3 = st.columns(3)

with col_nav1:
    st.markdown("### 🔐 Password Intelligence")
    st.write("Evaluate password strength using XGBoost machine learning.")
    if st.button("Open Analyzer ➡️", use_container_width=True):
        st.switch_page("pages/1_🔐_Password_Analysis.py")

with col_nav2:
    st.markdown("### 🪤 Risk Honeypot")
    st.write("Detect suspicious behavior and simulate login attacks.")
    if st.button("Open Honeypot ➡️", use_container_width=True):
        st.switch_page("pages/2_🪤_Login_Honeypot.py")

with col_nav3:
    st.markdown("### 📊 Admin Control")
    st.write("Visualize global threats and analyze intelligence data.")
    if st.button("Open Dashboard ➡️", use_container_width=True):
        st.switch_page("pages/4_🛡️_Admin_Dashboard.py")