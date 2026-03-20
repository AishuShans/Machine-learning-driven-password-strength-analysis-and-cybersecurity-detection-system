import streamlit as st

def apply_master_theme():
    st.markdown("""
        <style>
        /* 1. Main Dashboard Background */
        .stApp, .main {
            background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%) !important;
            color: white;
        }
        
        /* 2. THE NUCLEAR SIDEBAR FIX */
        [data-testid="stSidebar"] {
            background-color: #130f26 !important; /* Deep Purple */
            border-right: 2px solid #a855f7 !important;
        }
        [data-testid="stSidebar"] > div:first-child {
            background-color: transparent !important;
        }
        /* Target the sidebar navigation links */
        [data-testid="stSidebarNav"] {
            background-color: transparent !important;
        }
        
        /* 3. Neon Purple Headers */
        h1, h2, h3 {
            color: #a855f7 !important;
            text-shadow: 0 0 15px rgba(168, 85, 247, 0.6);
            font-family: 'Arial', sans-serif;
        }

        /* 4. Gradient Buttons */
        div.stButton > button {
            background: linear-gradient(90deg, #a855f7 0%, #00cfff 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 10px 24px !important;
            font-weight: bold !important;
            transition: 0.3s !important;
            width: 100% !important;
        }
        div.stButton > button:hover {
            transform: scale(1.02) !important;
            box-shadow: 0 0 20px rgba(168, 85, 247, 0.4) !important;
        }

        /* 5. Glassmorphism Metric Cards & Inputs */
        div[data-testid="stMetricBlock"], div[data-baseweb="input"] {
            background: rgba(255, 255, 255, 0.05) !important;
            backdrop-filter: blur(10px) !important;
            border: 1px solid rgba(168, 85, 247, 0.3) !important;
            border-radius: 15px !important;
        }
        div[data-testid="stMetricLabel"] {
            color: #00cfff !important;
        }
        div[data-testid="stMetricValue"] {
            color: white !important;
        }
        </style>
        """, unsafe_allow_html=True)