import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import time

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Digital Twin Groundwater", layout="wide")

# Style CSS pour personnaliser l'apparence
st.markdown("""
    <style>
    .main { background-color: #F5F5DC; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #5D4037; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR (PANNEAU LATÉRAL) ---
with st.sidebar:
    try:
        st.image("DT.png", use_container_width=True)
    except:
        st.warning("Image DT.png non trouvée.")
    
    st.title("Paramètres & Légende")
    st.markdown("---")
    st.write("**Seuil critique :** -1.2m")
    st.info("🔵 **Bleu :** Niveau Normal")
    st.error("🔴 **Rouge :** Pompe Arrêtée")
    st.warning("🟠 **Orange :** Scénario Sécheresse")
    st.markdown("---")
    speed = st.slider("Vitesse de simulation", 0.01, 0.5, 0.1)

# --- CHARGEMENT DES DONNÉES ---
FILE_NAME = "groundwater_level_modified.csv"
MINIMUM_THRESHOLD = -1.2

@st.cache_data
def load_data():
    return pd.read_csv(FILE_NAME)

try:
    df = load_data()
except:
    st.error("Fichier CSV introuvable !")
    st.stop()

# --- INTERFACE PRINCIPALE ---
st.title("🌊 Digital Twin : Surveillance de Nappe Phréatique")
plot_spot = st.empty()  # Zone réservée pour le graphique dynamique
status_spot = st.empty() # Zone réservée pour les messages d'alerte

if st.button('Lancer la Simulation en Temps Réel'):
    
    stop_indices = df['Height'] <= MINIMUM_THRESHOLD
    stop_index = stop_indices.idxmax() if stop_indices.any() else len(df)
    
    # Simulation des données historiques
    for i in range(len(df)):
        current_time = df.loc[i, 'Time']
        current_height = df.loc[i, 'Height']
        
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.set_facecolor('white')
        
        # Données historiques
        mask = df.index <= i
        colors = ['darkblue' if h > MINIMUM_THRESHOLD else 'gray' for h in df.loc[mask, 'Height']]
        ax.scatter(df.loc[mask, 'Time'], df.loc[mask, 'Height'], c=colors, s=15)
        
        # --- CORRECTION DE LA LOGIQUE D'ALERTE ---
        if i >= stop_index:
            ax.scatter(df.loc[stop_index, 'Time'], df.loc[stop_index, 'Height'], color='red', marker='X', s=100)
            msg = f"🚨 ALERTE (t={current_time:.1f}) : Niveau trop bas ! POMPE ARRÊTÉE"
            status_spot.error(msg)
        else:
            msg = f"✅ Système (t={current_time:.1f}) : NORMAL"
            status_spot.info(msg)
        # ------------------------------------------
        
        ax.set_xlim(df['Time'].min(), 130)
        ax.set_ylim(df['Height'].min() - 0.5, df['Height'].max() + 0.5)
        ax.axhline(MINIMUM_THRESHOLD, color='red', linestyle='--', alpha=0.3)
        ax.set_title(f"Monitoring en Direct - Temps: {current_time:.2f}")
        ax.set_xlabel("Temps")
        ax.set_ylabel("Hauteur (m)")
        
        plot_spot.pyplot(fig)
        plt.close(fig) # Important pour éviter de saturer la mémoire
        time.sleep(speed)

    # --- SCÉNARIOS DE PRÉDICTION ---
    status_spot.warning("🔮 Calcul des scénarios futurs en cours...")
    
    last_t = df['Time'].iloc[-1]
    last_h = df['Height'].iloc[-1]
    t_future = np.linspace(last_t, last_t + 30, 50)
    
    h_neutral = last_h + 0.5 * np.sin((t_future - last_t) / 5)
    h_high = h_neutral + 0.05 * (t_future - last_t)
    h_low = h_neutral - 0.05 * (t_future - last_t)
    
    # Mise à jour finale du graphique avec les prédictions
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.scatter(df['Time'], df['Height'], c=['darkblue' if h > MINIMUM_THRESHOLD else 'gray' for h in df['Height']], s=15)
    ax.plot(t_future, h_high, 'g--', label="Recharge Haute")
    ax.plot(t_future, h_neutral, 'b--', label="Stable")
    ax.plot(t_future, h_low, 'orange', linestyle='--', label="Sécheresse")
    ax.axhline(MINIMUM_THRESHOLD, color='red', linestyle='--', alpha=0.3)
    ax.legend(loc='upper right')
    ax.set_title("Prédictions du Jumeau Numérique")
    
    plot_spot.pyplot(fig)
    status_spot.success("Simulation terminée.")
