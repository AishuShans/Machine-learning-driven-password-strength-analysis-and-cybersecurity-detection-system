import streamlit as st
import math
import plotly.graph_objects as go
from utils.style import apply_master_theme

st.set_page_config(page_title="Crack Time Estimation", page_icon="⏱️", layout="wide")
apply_master_theme()

def colored_progress(label, value, max_value, color):
    pct = min((value / max_value) * 100, 100)
    st.markdown(f"""
    <p style='margin-bottom: 2px; font-size: 0.9rem;'>{label}</p>
    <div style="width: 100%; background-color: rgba(255,255,255,0.1); border-radius: 10px; margin-bottom: 15px;">
        <div style="width: {pct}%; height: 8px; background-color: {color}; border-radius: 10px; transition: 0.5s;"></div>
    </div>
    """, unsafe_allow_html=True)

st.title("⏱️ Advanced Telemetry & Crack Time")
st.write("Deep analysis of the credential currently in memory.")

# Check if a password exists in memory
if 'target_pwd' not in st.session_state or not st.session_state.target_pwd:
    st.warning("No password detected in memory. Please return to the Analyzer page to input a credential.")
    if st.button("⬅️ Return to Analyzer"):
        st.switch_page("pages/1_🔐_Password_Analysis.py")
else:
    pwd = st.session_state.target_pwd
    
    # Recalculate basic features for charts
    length = len(pwd)
    digits = sum(c.isdigit() for c in pwd)
    upper = sum(c.isupper() for c in pwd)
    lower = sum(c.islower() for c in pwd)
    special = length - digits - upper - lower
    unique_chars = len(set(pwd))
    len_safe = length if length > 0 else 1
    prob = [pwd.count(c) / len_safe for c in set(pwd)]
    entropy = -sum(p * math.log2(p) for p in prob if p > 0)
    
    # Calculate combinations perfectly
    pool_size = (1 if lower > 0 else 0)*26 + (1 if upper > 0 else 0)*26 + (1 if digits > 0 else 0)*10 + (1 if special > 0 else 0)*32
    pool_size = max(pool_size, 1) # Failsafe
    combs = pool_size ** len_safe
    
    # Determine color theme based on length
    color = "#00cfff" if length >= 12 else ("#faca2b" if length >= 8 else "#ff4b4b")

    if st.button("⬅️ Back to Analyzer"):
        st.switch_page("pages/1_🔐_Password_Analysis.py")
    st.write("---")

    # PROGRESS BARS
    b1, b2, b3 = st.columns(3)
    with b1: colored_progress("Length Strength", length, 20, color)
    with b2: colored_progress("Character Diversity", (unique_chars/len_safe)*100, 100, color)
    with b3: colored_progress("Entropy Level", entropy, 5, color)
        
    # METRICS
    st.markdown("#### Key Metrics")
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("Length", length)
    m2.metric("Upper", upper)
    m3.metric("Lower", lower)
    m4.metric("Numbers", digits)
    m5.metric("Symbols", special)
    m6.metric("Entropy", f"{round(entropy, 1)} bits")

    st.write("<br>", unsafe_allow_html=True)
    col_chart1, col_chart2 = st.columns(2)

    # RADAR CHART
    with col_chart1:
        st.markdown("#### 🎯 Feature Comparison Radar")
        radar_vals = [min(length/20*100, 100), min(entropy/5*100, 100), (unique_chars/len_safe)*100, min((length*4+entropy)/150*100, 100)]
        fig_radar = go.Figure(go.Scatterpolar(r=radar_vals, theta=['Length', 'Entropy', 'Diversity', 'Score'], fill='toself', line_color=color))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, 100])), showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="white"), margin=dict(t=20, b=20, l=20, r=20), height=350)
        st.plotly_chart(fig_radar, use_container_width=True)

    # CRACK TIME ESTIMATION
    with col_chart2:
        st.markdown("#### ⏱️ Actual Crack Time Estimation")
        online_time = combs / 100 
        offline_cpu = combs / 1e8 
        offline_gpu = combs / 1e10 
        
        # New, highly accurate time formatter!
        def format_time(seconds):
            if seconds < 1: return "Instant (🔴 Very Weak)"
            elif seconds < 60: return f"{int(seconds)} Seconds (🔴 Very Weak)"
            elif seconds < 3600: return f"{int(seconds/60)} Minutes (🔴 Very Weak)"
            elif seconds < 86400: return f"{int(seconds/3600)} Hours (🟡 Moderate)"
            elif seconds < 31536000: return f"{int(seconds/86400)} Days (🟡 Moderate)"
            elif seconds < 3153600000: return f"{int(seconds/31536000)} Years (🟢 Strong)"
            else: return "Centuries+ (🟢 Uncrackable)"

        st.write(f"- **Web Form (100/sec):** {format_time(online_time)}")
        st.write(f"- **Offline CPU (100M/sec):** {format_time(offline_cpu)}")
        st.write(f"- **GPU Botnet (10B/sec):** {format_time(offline_gpu)}")

        times = [max(online_time, 0.1), max(offline_cpu, 0.1), max(offline_gpu, 0.1)]
        
        # Draw the updated bar chart
        fig_bar = go.Figure(go.Bar(
            x=times, 
            y=["Web Form", "CPU", "GPU"], 
            orientation='h', 
            marker_color=['#00cfff', '#faca2b', '#ff4b4b']
        ))
        fig_bar.update_layout(xaxis_type="log", xaxis_title="Seconds to Crack (Log Scale)", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="white"), margin=dict(t=10, b=20, l=10, r=20), height=200)
        st.plotly_chart(fig_bar, use_container_width=True)