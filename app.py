import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Synthetic Digital Twin Groundwater", layout="wide")

# CSS style to customize the interface appearance
st.markdown("""
    <style>
    .main { background-color: #F5F5DC; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #5D4037; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR (LATERAL PANEL) ---
with st.sidebar:
    st.markdown("***")
    st.write("Developed by ROMAIN CHASSAGNE")
    st.markdown("***")
    try:
        st.image("DT.png", use_container_width=True)
    except:
        st.warning("Image DT.png not found.")
    
    st.markdown("---")
    
    # UPDATED LEGEND
    st.success("🟢 **Green:** Safe Level")
    st.info("⚪ **Gray:** Groundwater Critical level reached")
    
    st.markdown("---")
    speed = st.slider("Simulation Speed", 0.001, 0.4, 0.05)

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
st.title("💧 Synthetic Digital Twin for Groundwater Extraction and Monitoring")

st.markdown("""
*This synthetic digital twin demonstrates how real-time monitoring can be integrated 
into a web application. It mimics the continuous observation of water table levels 
and groundwater extraction. When the water table reaches a critical low level, 
the system automatically triggers a pump shutdown; as levels recover above the 
safety threshold, the pump reactivates. Following the historical data sequence, 
the model forecasts three potential future scenarios.* 

**Digital twin workflow:** Data Acquisition → Data Flow → Data Assimilation 
& Analysis → Decision Making → Real-World Action → What-if Forecasting. 

**Future enhancements:** will include integrating in-situ real-time data and authentic sensor inputs.
""")

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
            if i >= stop_index:
                ax.scatter(df.loc[stop_index, 'Time'], df.loc[stop_index, 'Height'], color='red', marker='X', s=120, zorder=5)
            
            msg = f"🚨 ALERT (t={current_time:.1f}): Groundwater Level too low! PUMP STOPPED"
            status_spot.error(msg)
        else:
            msg = f"✅ System (t={current_time:.1f}): Normal condition : PUMP ON"
            status_spot.success(msg)
        
        ax.set_xlim(df['Time'].min(), 130)
        ax.set_ylim(df['Height'].min() - 0.5, df['Height'].max() + 0.5)
        ax.axhline(MINIMUM_THRESHOLD, color='red', linestyle='--', alpha=0.3)
        ax.set_title(f"Live Monitoring - Time: {current_time:.2f}")
        ax.set_xlabel("Time (dimensionless)")
        ax.set_ylabel("Height (dimensionless)")
        
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
    ax.legend(loc='upper left')
    ax.set_title("Forecasting scenarios")
    ax.set_xlabel("Time (dimensionless)")
    ax.set_ylabel("Height (dimensionless)")
    
    plot_spot.pyplot(fig) # Correctly indented inside the button block
    status_spot.success("Simulation complete.")

# --- REFERENCES SECTION (Aligned to the left, outside the button block) ---
st.markdown("---")
st.subheader("📚 References & Resources")
st.markdown("""
- **Practical Data Assimilation for the Subsurface. R. Chassagne** [Earth Sciences. Université de Lorraine (Nancy) 2025](https://brgm.hal.science/tel-05147912v1)
""")
st.markdown("""
- **Digital Twins for the subsurface, how far can we go? R. Chassagne, F. Wellmann** [SIAM Conference on Mathematical & Computational Issues in the Geosciences](https://brgm.hal.science/hal-04031559/)
""")

