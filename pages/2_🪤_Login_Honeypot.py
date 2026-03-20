import streamlit as st
import pandas as pd
import datetime
import random
import os
import time
import requests
from utils.style import apply_master_theme

# --- PAGE SETUP ---
st.set_page_config(page_title="Secure Authentication", page_icon="🪤", layout="wide")
apply_master_theme()

# --- DATABASE SETUP ---
DATA_DIR = 'data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

USERS_DB = f'{DATA_DIR}/users.csv'
LOGS_DB = f'{DATA_DIR}/login_logs.csv'

# Initialize CSVs
if not os.path.exists(USERS_DB):
    pd.DataFrame(columns=["Username", "Password", "Created_At"]).to_csv(USERS_DB, index=False)
if not os.path.exists(LOGS_DB):
    pd.DataFrame(columns=["Timestamp", "Target_Username", "Password_Tried", "IP_Address", "Location", "lat", "lon", "Device", "Status"]).to_csv(LOGS_DB, index=False)

# --- REAL-TIME GEOLOCATION API ---
def get_real_ip_and_location():
    try:
        # Pings a safe, free server to get your actual IP and coordinates
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get('http://ip-api.com/json/', headers=headers, timeout=5)
        data = response.json()
        if data.get('status') == 'success':
            ip = data.get('query', '127.0.0.1')
            city = data.get('city', 'Unknown City')
            country = data.get('countryCode', 'UN')
            lat = float(data.get('lat', 11.0168)) 
            lon = float(data.get('lon', 76.9558))
            return ip, f"{city}, {country}", lat, lon
    except:
        pass
    # Fallback to Coimbatore if your internet drops during the demo
    return "127.0.0.1", "Coimbatore, IN", 11.0168, 76.9558

# --- BACKEND FUNCTIONS ---
def register_user(username, password):
    df_users = pd.read_csv(USERS_DB)
    if username in df_users['Username'].values:
        return False 
    
    new_user = pd.DataFrame([{
        "Username": username, 
        "Password": password, 
        "Created_At": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }])
    new_user.to_csv(USERS_DB, mode='a', header=False, index=False)
    return True

def log_attempt(username, password, is_success):
    # Fetch the REAL data of the person clicking the button
    real_ip, real_loc, lat, lon = get_real_ip_and_location()
    
    dev = "User Desktop" if is_success else "Unknown/Suspicious Device"
    status = "Success" if is_success else "Failed"
    
    new_log = pd.DataFrame([{
        "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Target_Username": username,
        "Password_Tried": password,
        "IP_Address": real_ip,
        "Location": real_loc,
        "lat": lat if not is_success else 0.0, # Hide success logins from the threat map
        "lon": lon if not is_success else 0.0,
        "Device": dev,
        "Status": status
    }])
    new_log.to_csv(LOGS_DB, mode='a', header=False, index=False)

def verify_login(username, password):
    df_users = pd.read_csv(USERS_DB)
    match = df_users[(df_users['Username'] == username) & (df_users['Password'] == password)]
    
    if not match.empty:
        log_attempt(username, "HIDDEN", True)
        return True
    else:
        log_attempt(username, password, False)
        return False

# --- UI RENDERING ---
st.markdown("<h1>🪤 Cyber-Sentinel Authentication</h1>", unsafe_allow_html=True)
st.write("---")

if 'logged_in_user' not in st.session_state:
    st.session_state.logged_in_user = None

if st.session_state.logged_in_user:
    st.success(f"You are already logged in as **{st.session_state.logged_in_user}**.")
    if st.button("Proceed to Personal Dashboard ➡️"):
        st.switch_page("pages/3_User_Dashboard.py")
    if st.button("Logout"):
        st.session_state.logged_in_user = None
        st.rerun()
else:
    tab1, tab2 = st.tabs(["🔐 Secure Login", "📝 Register Account"])

    with tab1:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("### Access Terminal")
            with st.container(border=True):
                l_user = st.text_input("Username", key="login_user")
                l_pwd = st.text_input("Password", type="password", key="login_pwd")
                
                if st.button("Authenticate", use_container_width=True):
                    if l_user and l_pwd:
                        with st.spinner("Verifying credentials..."):
                            time.sleep(1)
                            if verify_login(l_user, l_pwd):
                                st.session_state.logged_in_user = l_user
                                st.success("Access Granted! Redirecting...")
                                time.sleep(1)
                                st.switch_page("pages/3_User_Dashboard.py")
                            else:
                                st.error("❌ Invalid Credentials. This unauthorized attempt has been logged.")
                    else:
                        st.warning("Please enter both username and password.")

        with col2:
            st.markdown("### 🛡️ Security Notice")
            st.info("""
            This terminal is actively monitored. 
            All failed login attempts are routed to the Honeypot database and analyzed by the XGBoost Risk Engine.
            """)

    with tab2:
        st.markdown("### Create New Identity")
        with st.container(border=True):
            r_user = st.text_input("Choose a Username", key="reg_user")
            r_pwd = st.text_input("Choose a Secure Password", type="password", key="reg_pwd")
            
            if st.button("Register Account", use_container_width=True):
                if r_user and r_pwd:
                    if register_user(r_user, r_pwd):
                        st.success(f"Account '{r_user}' successfully created! You may now log in.")
                        st.balloons()
                    else:
                        st.error("Username already exists. Please choose another.")
                else:
                    st.warning("Fields cannot be empty.")