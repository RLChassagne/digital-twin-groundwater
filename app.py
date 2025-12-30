import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Digital Twin Groundwater", layout="wide")

# CSS style to customize the interface appearance
st.markdown("""
    <style>
    .main { background-color: #F5F5DC; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #5D4037; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR (LATERAL PANEL) ---
with st.sidebar:
    try:
        st.image("DT.png", use_container_width=True)
    except:
        st.warning("Image DT.png not found.")
    
    st.title("Parameters & Legend")
    st.markdown("---")
    st.write("**Critical Threshold:** -1.2m")
    
    # UPDATED LEGEND
    st.success("🟢 **Green:** Safe Level (> Threshold)")
    st.info("⚪ **Gray:** Below Threshold (Recovery)")
    st.error("🔴 **Red:** Pump Stopped (Shutdown)")
    
    st.markdown("---")
    speed = st.slider("Simulation Speed", 0.01, 0.5, 0.1)

# --- DATA LOADING ---
FILE_NAME = "groundwater_level_modified.csv"
MINIMUM_THRESHOLD = -1.2

@st.cache_data
def load_data():
    return pd.read_csv(FILE_NAME)

try:
    df = load_data()
except:
    st.error("CSV file not found!")
    st.stop()

# --- MAIN INTERFACE ---
st.title("🌊 Digital Twin: Groundwater Monitoring")
plot_spot = st.empty()  # Reserved zone for dynamic chart
status_spot = st.empty() # Reserved zone for alert messages

if st.button('Start Real-Time Simulation'):
    
    stop_indices = df['Height'] <= MINIMUM_THRESHOLD
    stop_index = stop_indices.idxmax() if stop_indices.any() else len(df)
    
    # Historical data simulation
    for i in range(len(df)):
        current_time = df.loc[i, 'Time']
        current_height = df.loc[i, 'Height']
        
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.set_facecolor('white')
        
        # Data point color logic
        mask = df.index <= i
        colors = ['green' if h > MINIMUM_THRESHOLD else 'gray' for h in df.loc[mask, 'Height']]
        ax.scatter(df.loc[mask, 'Time'], df.loc[mask, 'Height'], c=colors, s=15)
        
        # --- STATUS MESSAGE LOGIC ---
        if current_height <= MINIMUM_THRESHOLD:
            # Marking the shutdown point
            if i >= stop_index:
                ax.scatter(df.loc[stop_index, 'Time'], df.loc[stop_index, 'Height'], color='red', marker='X', s=120, zorder=5)
            
            msg = f"🚨 ALERT (t={current_time:.1f}): Level too low! PUMP STOPPED"
            status_spot.error(msg) # Red banner
        else:
            msg = f"✅ System (t={current_time:.1f}): Safe Level"
            status_spot.success(msg) # Green banner
        # ------------------------------------
        
        ax.set_xlim(df['Time'].min(), 130)
        ax.set_ylim(df['Height'].min() - 0.5, df['Height'].max() + 0.5)
        ax.axhline(MINIMUM_THRESHOLD, color='red', linestyle='--', alpha=0.3)
        ax.set_title(f"Live Monitoring - Time: {current_time:.2f}")
        ax.set_xlabel("Time")
        ax.set_ylabel("Height (m)")
        
        plot_spot.pyplot(fig)
        plt.close(fig) 
        time.sleep(speed)

    # --- PREDICTION SCENARIOS ---
    status_spot.warning("🔮 Calculating future scenarios...")
    
    last_t = df['Time'].iloc[-1]
    last_h = df['Height'].iloc[-1]
    t_future = np.linspace(last_t, last_t + 30, 50)
    
    h_neutral = last_h + 0.5 * np.sin((t_future - last_t) / 5)
    h_high = h_neutral + 0.05 * (t_future - last_t)
    h_low = h_neutral - 0.05 * (t_future - last_t)
    
    fig, ax = plt.subplots(figsize=(10, 5))
    final_colors = ['green' if h > MINIMUM_THRESHOLD else 'gray' for h in df['Height']]
    ax.scatter(df['Time'], df['Height'], c=final_colors, s=15)
    
    ax.plot(t_future, h_high, 'g--', label="High Recharge")
    ax.plot(t_future, h_neutral, 'b--', label="Stable")
    ax.plot(t_future, h_low, 'orange', linestyle='--', label="Drought")
    
    ax.axhline(MINIMUM_THRESHOLD, color='red', linestyle='--', alpha=0.3)
    ax.legend(loc='upper right')
    ax.set_title("Digital Twin Forecast Predictions")
    ax.set_xlabel("Time")
    ax.set_ylabel("Height (m)")
    
    plot_spot.pyplot(fig)
    status_spot.success("Simulation complete.")
