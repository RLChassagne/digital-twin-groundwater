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
    # LÉGENDE NETTOYÉE ET MISE À JOUR
    st.success("🟢 **Vert :** Niveau Sûr (> Seuil)")
    st.info("⚪ **Gris :** Sous le seuil (Récupération)")
    st.error("🔴 **Rouge :** Point d'arrêt (Shutdown)")
    # Case Orange supprimée ici
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
plot_spot = st.empty()  
status_spot = st.empty() 

if st.button('Lancer la Simulation en Temps Réel'):
    
    stop_indices = df['Height'] <= MINIMUM_THRESHOLD
    stop_index = stop_indices.idxmax() if stop_indices.any() else len(df)
    
    # Simulation des données historiques
    for i in range(len(df)):
        current_time = df.loc[i, 'Time']
        current_height = df.loc[i, 'Height']
        
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.set_facecolor('white')
        
        # Logique de couleur des points
        mask = df.index <= i
        colors = ['green' if h > MINIMUM_THRESHOLD else 'gray' for h in df.loc[mask, 'Height']]
        ax.scatter(df.loc[mask, 'Time'], df.loc[mask, 'Height'], c=colors, s=15)
        
        # --- LOGIQUE DU MESSAGE DE STATUT (CORRIGÉE) ---
        if current_height <= MINIMUM_THRESHOLD:
            # Si on est pile au moment du shutdown (index précis) ou après en zone critique
            if i >= stop_index:
                ax.scatter(df.loc[stop_index, 'Time'], df.loc[stop_index, 'Height'], color='red', marker='X', s=120, zorder=5)
            
            msg = f"🚨 ALERTE (t={current_time:.1f}) : Niveau trop bas ! POMPE ARRÊTÉE"
            status_spot.error(msg) # Bandeau Rouge
        else:
            msg = f"✅ Système (t={current_time:.1f}) : Niveau Sûr"
            status_spot.success(msg) # Bandeau Vert (Success)
        # -----------------------------------------------
        
        ax.set_xlim(df['Time'].min(), 130)
        ax.set_ylim(df['Height'].min() - 0.5, df['Height'].max() + 0.5)
        ax.axhline(MINIMUM_THRESHOLD, color='red', linestyle='--', alpha=0.3)
        ax.set_title(f"Monitoring en Direct - Temps: {current_time:.2f}")
        ax.set_xlabel("Temps")
        ax.set_ylabel("Hauteur (m)")
        
        plot_spot.pyplot(fig)
        plt.close(fig) 
        time.sleep(speed)

    # --- SCÉNARIOS DE PRÉDICTION ---
    status_spot.warning("🔮 Calcul des scénarios futurs en cours...")
    
    last_t = df['Time'].iloc[-1]
    last_h = df['Height'].iloc[-1]
    t_future = np.linspace(last_t, last_t + 30, 50)
    
    h_neutral = last_h + 0.5 * np.sin((t_future - last_t) / 5)
    h_high = h_neutral + 0.05 * (t_future - last_t)
    h_low = h_neutral - 0.05 * (t_future - last_t)
    
    fig, ax = plt.subplots(figsize=(10, 5))
    final_colors = ['green' if h > MINIMUM_THRESHOLD else 'gray' for h in df['Height']]
    ax.scatter(df['Time'], df['Height'], c=final_colors, s=15)
    
    ax.plot(t_future, h_high, 'g--', label="Recharge Haute (Prédiction)")
    ax.plot(t_future, h_neutral, 'b--', label="Stable (Prédiction)")
    ax.plot(t_future, h_low, 'orange', linestyle='--', label="Sécheresse (Prédiction)")
    
    ax.axhline(MINIMUM_THRESHOLD, color='red', linestyle='--', alpha=0.3)
    ax.legend(loc='upper right')
    ax.set_title("Prédictions du Jumeau Numérique")
    
    plot_spot.pyplot(fig)
    status_spot.success("Simulation terminée.")
