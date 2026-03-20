import streamlit as st
import pandas as pd
import math
import re
import joblib
import random
import string
import plotly.graph_objects as go
from utils.style import apply_master_theme

# --- PAGE SETUP & THEME ---
st.set_page_config(page_title="Password Intelligence", page_icon="🔐", layout="wide")
apply_master_theme()

# --- ML CACHE & COMMON BREACH LIST ---
@st.cache_resource
def load_model():
    try: return joblib.load('models/password_strength_model.pkl') 
    except: return None
xgb_model = load_model()

COMMON_PASSWORDS = {'123456', 'password', '12345678', 'qwerty', '12345', '123456789', 'iloveyou', 'admin', 'welcome', '1234', '111111'}

# --- CUSTOM UI COMPONENTS ---
def colored_progress(label, value, max_value, color):
    pct = min((value / max_value) * 100, 100)
    st.markdown(f"""
    <p style='margin-bottom: 2px; font-size: 0.9rem;'>{label}</p>
    <div style="width: 100%; background-color: rgba(255,255,255,0.1); border-radius: 10px; margin-bottom: 15px;">
        <div style="width: {pct}%; height: 8px; background-color: {color}; border-radius: 10px; transition: 0.5s;"></div>
    </div>
    """, unsafe_allow_html=True)

# --- ENGINE: EXTRACT FEATURES ---
def extract_all_features(pwd):
    length = len(pwd)
    digits = sum(c.isdigit() for c in pwd)
    upper = sum(c.isupper() for c in pwd)
    lower = sum(c.islower() for c in pwd)
    special = length - digits - upper - lower
    unique_chars = len(set(pwd))
    
    len_safe = length if length > 0 else 1
    prob = [pwd.count(c) / len_safe for c in set(pwd)]
    entropy = -sum(p * math.log2(p) for p in prob if p > 0)
    
    has_digit = 1 if digits > 0 else 0
    has_upper = 1 if upper > 0 else 0
    has_lower = 1 if lower > 0 else 0
    has_special = 1 if special > 0 else 0
    char_type_count = has_digit + has_upper + has_lower + has_special

    features = {
        'length': length, 'digits': digits, 'upper': upper, 'lower': lower,
        'special': special, 'unique_chars': unique_chars, 'digit_ratio': digits / len_safe,
        'upper_ratio': upper / len_safe, 'lower_ratio': lower / len_safe,
        'special_ratio': special / len_safe, 'has_digit': has_digit, 'has_upper': has_upper,
        'has_lower': has_lower, 'has_special': has_special,
        'starts_with_letter': 1 if length > 0 and pwd[0].isalpha() else 0,
        'ends_with_digit': 1 if length > 0 and pwd[-1].isdigit() else 0,
        'repeated_chars': sum(1 for i in range(length-1) if pwd[i] == pwd[i+1]),
        'consecutive_digits': len(re.findall(r'\d{2,}', pwd)),
        'entropy': entropy, 'char_type_count': char_type_count,
        'complexity_score': length * char_type_count + entropy, 
        'char_diversity': unique_chars / len_safe,
        'contains_pattern': 1 if re.search(r'(123|abc|qwer|pass|zxcv)', pwd.lower()) else 0
    }
    return pd.DataFrame([features]), features

# --- ENGINE: GENERATOR ---
def generate_custom_password(length, use_upper, use_lower, use_digits, use_special):
    chars = ""
    if use_upper: chars += string.ascii_uppercase
    if use_lower: chars += string.ascii_lowercase
    if use_digits: chars += string.digits
    if use_special: chars += "!@#$%^&*"
    if not chars: chars = string.ascii_lowercase
    return ''.join(random.choice(chars) for _ in range(length))

# ==========================================
# 🎨 SIDEBAR (RESTORED!)
# ==========================================
with st.sidebar:
    st.markdown("### 🎛️ Dashboard Controls")
    advanced_mode = st.toggle("🔬 Enable Advanced Mode", value=False, help="Toggle full metrics, charts, and deep insights.")
    
    st.write("---")
    st.markdown("### ✨ Advanced Generator")
    gen_len = st.slider("Length", 8, 32, 16)
    c1, c2 = st.columns(2)
    with c1:
        g_up = st.checkbox("Uppercase", value=True)
        g_low = st.checkbox("Lowercase", value=True)
    with c2:
        g_num = st.checkbox("Numbers", value=True)
        g_sym = st.checkbox("Symbols", value=True)
    
    if st.button("Generate Secure Password", use_container_width=True):
        st.session_state.gen_pwd = generate_custom_password(gen_len, g_up, g_low, g_num, g_sym)
    
    # 1-Click Copy Feature
    if 'gen_pwd' in st.session_state and st.session_state.gen_pwd:
        st.success("Generated! Click icon below to copy:")
        st.code(st.session_state.gen_pwd, language="text")

# ==========================================
# 🎨 MAIN UI RENDERING
# ==========================================

st.markdown("<h1>🛡️ Password Strength Analyzer</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='color: #00cfff;'>Check how secure your password is in real-time</h4>", unsafe_allow_html=True)
st.write("---")

# --- INPUT SECTION ---
if 'gen_pwd' not in st.session_state:
    st.session_state.gen_pwd = ""

# Keep track of the password for the Crack Time page
pwd = st.text_input("🔑 Enter Target Password:", value=st.session_state.gen_pwd, type="password", help="Use the eye icon to show/hide text.")
st.session_state.target_pwd = pwd

# --- AI ANALYSIS & FEEDBACK ---
if pwd:
    df_feat, rf = extract_all_features(pwd)
    
    pred = xgb_model.predict(df_feat)[0] if xgb_model else 0
    raw_score = (rf['complexity_score'] / 150) * 100
    
    if pred == 0: score = min(int(raw_score), 39)
    elif pred == 1: score = min(max(int(raw_score), 40), 79)
    else: score = max(int(raw_score), 80)
    score = min(score, 100)
    percentile = max(10, score - 5)

    if score < 40:
        status, color, icon, risk = "WEAK", "#ff4b4b", "🚨", "High Risk"
        explain = "This password relies on basic structures and lacks the entropy required to stop attackers."
    elif score < 80:
        status, color, icon, risk = "MEDIUM", "#faca2b", "⚠️", "Medium Risk"
        explain = "This password has good foundational strength, but lacks the length or diversity for maximum security."
    else:
        status, color, icon, risk = "STRONG", "#00cfff", "🛡️", "Low Risk"
        explain = "Exceptional architecture. This credential utilizes high entropy and complex character diversity."

    # 1. REPORT CARD
    st.markdown("### 📋 Password Report Card")
    rc1, rc2 = st.columns([1, 2])
    with rc1:
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number", value = score,
            title = {'text': f"{status}", 'font': {'color': color, 'size': 20}},
            gauge = {
                'axis': {'range': [None, 100], 'visible': False}, 'bar': {'color': color},
                'bgcolor': "rgba(255,255,255,0.05)",
                'steps': [{'range': [0, 40], 'color': "rgba(255, 75, 75, 0.2)"},
                          {'range': [40, 80], 'color': "rgba(250, 202, 43, 0.2)"},
                          {'range': [80, 100], 'color': "rgba(0, 207, 255, 0.2)"}]
            }
        ))
        fig_gauge.update_layout(height=220, margin=dict(t=30, b=10, l=10, r=10), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
        st.plotly_chart(fig_gauge, use_container_width=True)
        st.markdown(f"<p style='text-align: center; color: {color}; margin-top:-40px;'><strong>{risk}</strong></p>", unsafe_allow_html=True)

    # 2. EXPLAINABILITY ENGINE
    with rc2:
        st.markdown("#### 🔍 Explainability Engine")
        st.info(explain)
        st.write(f"📊 **Dataset Comparison:** Stronger than **{percentile}%** of average users.")
        if pwd.lower() in COMMON_PASSWORDS:
            st.error("🚨 BREACH ALERT: This password is commonly used and easily guessable!")

    # 3. SMART SUGGESTIONS
    st.write("---")
    st.markdown("#### 💡 Smart Suggestions")
    s1, s2 = st.columns(2)
    with s1:
        if rf['length'] >= 12: st.success("✔ Good length")
        else: st.error("❌ Increase length to at least 12 characters")
        if rf['contains_pattern'] == 1: st.warning("⚠️ Pattern Detected: Contains sequential/keyboard patterns.")
        if rf['repeated_chars'] > 0: st.warning("⚠️ Pattern Detected: Contains repeated characters.")
    with s2:
        if rf['char_type_count'] >= 4: st.success("✔ Uses multiple character types")
        elif rf['special'] == 0: st.error("❌ Add special characters like @, #, !")
        elif rf['upper'] == 0: st.error("❌ Add uppercase letters")
        elif rf['digits'] == 0: st.error("❌ Add numbers")

    # 4. ADVANCED MODE (Toggled via Sidebar)
    if advanced_mode:
        st.write("---")
        st.markdown("## 🔬 Advanced Telemetry & Charts")
        
        b1, b2, b3 = st.columns(3)
        with b1: colored_progress("Length Strength", rf['length'], 20, color)
        with b2: colored_progress("Character Diversity", rf['char_diversity'] * 100, 100, color)
        with b3: colored_progress("Entropy Level", rf['entropy'], 5, color)
            
        m1, m2, m3, m4, m5, m6 = st.columns(6)
        m1.metric("Length", rf['length'])
        m2.metric("Upper", rf['upper'])
        m3.metric("Lower", rf['lower'])
        m4.metric("Numbers", rf['digits'])
        m5.metric("Symbols", rf['special'])
        m6.metric("Entropy", f"{round(rf['entropy'], 1)} bits")

        st.markdown("#### 🎯 Feature Comparison Radar")
        radar_vals = [min(rf['length']/20*100, 100), min(rf['entropy']/5*100, 100), rf['char_diversity']*100, score]
        fig_radar = go.Figure(go.Scatterpolar(r=radar_vals, theta=['Length', 'Entropy', 'Diversity', 'Overall Score'], fill='toself', line_color=color))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, 100])), showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="white"), margin=dict(t=20, b=20, l=20, r=20), height=300)
        st.plotly_chart(fig_radar, use_container_width=True)

    # 5. NAVIGATION TO CRACK TIME PAGE
    st.write("---")
    st.markdown("### ⏱️ Attack Vector Analysis")
    st.write("Run a full threat simulation to estimate brute-force crack times across different hardware setups.")
    if st.button("🚀 View Crack Time Estimation", use_container_width=True):
        st.switch_page("pages/5_Crack_Time.py")