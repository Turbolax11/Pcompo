from pathlib import Path
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Titre principal
st.markdown("<h1 style='text-align: center; color: #6C63FF;'>Calcul d'épaisseur pour composites</h1>", unsafe_allow_html=True)

# Sélection de la méthode
method = st.radio(
    "Méthode de calcul :",
    ("Méthode 1 : Basée sur la masse de fibres", "Méthode 2 : Basée sur le grammage et le nombre de plis"),
    index=0,
    horizontal=True
)

# Fonctions de calcul
def calcul_epaisseur_masse(m_f, A, V_f, rho_f):
    """Calcule l'épaisseur en fonction de la masse de fibres."""
    V_fibres = m_f / rho_f  # volume des fibres (m³)
    V_total = V_fibres / V_f  # volume total du composite (m³)
    e = V_total / A  # épaisseur en m
    return e * 1000  # conversion en mm

def calcul_resine(m_f, V_f, rho_f, rho_m):
    """Calcule la masse de résine nécessaire."""
    V_fibres = m_f / rho_f  # volume des fibres (m³)
    V_total = V_fibres / V_f  # volume total du composite (m³)
    V_resine = V_total * (1 - V_f)  # volume de résine (m³)
    return V_resine * rho_m * 1000  # conversion en g

def calcul_epaisseur_inverse(grammage, nb_plis, rho_f, V_f):
    """Calcule l'épaisseur en fonction du grammage et du nombre de plis."""
    grammage_kg_m2 = grammage / 1000  # g/m² -> kg/m²
    V_total_per_m2 = (grammage_kg_m2 * nb_plis) / (rho_f * V_f)
    return V_total_per_m2 * 1000  # conversion en mm

# Méthode 1 : Basée sur la masse de fibres
if method == "Méthode 1 : Basée sur la masse de fibres":
    st.markdown("<h3 style='text-align: center;'>Paramètres de la méthode 1</h3>", unsafe_allow_html=True)

     # Sélection du matériau
    col1, col2, col3 = st.columns(3)

    with col1:
        carbone_selected = st.button("Carbone (1780 kg/m³)", key="carbone_m2")
    with col2:
        verre_selected = st.button("Verre (2540 kg/m³)", key="verre_m2")
    with col3:
        custom_density = st.number_input("Saisir une densité (kg/m³):", min_value=1000, max_value=3000, value=1780, key="custom_density_m2")

    if carbone_selected:
        rho_f = 1780
    elif verre_selected:
        rho_f = 2540
    else:
        rho_f = custom_density

    rho_f = st.slider("Densité (kg/m³):", min_value=1000, max_value=3000, value=int(rho_f), key="density_slider_m2")

    # Paramètres principaux
    col1, col2 = st.columns(2)
    with col1:
        largeur = st.slider("Largeur (mm)", 10, 1000, 200)
    with col2:
        longueur = st.slider("Longueur (mm)", 10, 1000, 200)

    m_f = st.slider("Masse de fibres (g)", 10, 2000, 100)
    V_f = st.slider("Fraction volumique de fibres (V_f)", 0.3, 0.7, 0.6, step=0.01)
    rho_m = st.slider("Densité de la matrice (kg/m³)", 800, 1500, 1200)

    # Calculs
    A = (largeur * longueur) / 1e6  # Surface en m²
    épaisseur = calcul_epaisseur_masse(m_f / 1000, A, V_f, rho_f)
    masse_resine = calcul_resine(m_f / 1000, V_f, rho_f, rho_m)

    # Affichage des résultats
    st.markdown(f"<h3 style='text-align: center; color: #333;'>Épaisseur Calculée</h3>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='text-align: center; color: #FF6B6B;'>{épaisseur:.2f} mm</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center; color: #333;'>Masse de résine nécessaire</h3>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='text-align: center; color: #6C63FF;'>{masse_resine:.2f} g</h1>", unsafe_allow_html=True)

    # Graphique interactif
    V_f_values = np.linspace(0.3, 0.7, 100)
    épaisseur_values = [calcul_epaisseur_masse(m_f / 1000, A, vf, rho_f) for vf in V_f_values]

    fig, ax = plt.subplots()
    ax.plot(V_f_values, épaisseur_values, label="Épaisseur (mm)", color="#6C63FF", linewidth=2)
    ax.scatter(V_f, épaisseur, color="#FF6B6B", label="Valeur actuelle", zorder=5)
    ax.set_xlabel("Fraction volumique de fibres (V_f)")
    ax.set_ylabel("Épaisseur (mm)")
    ax.set_title("Variation de l'épaisseur en fonction de V_f")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

# Méthode 2 : Basée sur le grammage et le nombre de plis
elif method == "Méthode 2 : Basée sur le grammage et le nombre de plis":
    st.markdown("<h3 style='text-align: center;'>Paramètres de la méthode 2</h3>", unsafe_allow_html=True)

    # Sélection du matériau
  # Sélection du matériau
    col1, col2, col3 = st.columns(3)

    with col1:
        carbone_selected = st.button("Carbone (1780 kg/m³)", key="carbone_m2")
    with col2:
        verre_selected = st.button("Verre (2540 kg/m³)", key="verre_m2")
    with col3:
        custom_density = st.number_input("Saisir une densité (kg/m³):", min_value=1000, max_value=3000, value=1780, key="custom_density_m2")

    if carbone_selected:
        rho_f = 1780
    elif verre_selected:
        rho_f = 2540
    else:
        rho_f = custom_density

    rho_f = st.slider("Densité (kg/m³):", min_value=1000, max_value=3000, value=int(rho_f), key="density_slider_m2")

    # Paramètres principaux
    grammage = st.slider("Grammage surfacique (g/m²)", 100, 2000, 300)
    nb_plis = st.number_input("Nombre de plis", min_value=1, max_value=20, value=5, step=1, format="%d")
    V_f = st.slider("Fraction volumique de fibres (V_f)", 0.3, 0.7, 0.6, step=0.01)

    # Calculs
    épaisseur = calcul_epaisseur_inverse(grammage, nb_plis, rho_f, V_f)

    # Affichage des résultats
    st.markdown(f"<h3 style='text-align: center; color: #333;'>Épaisseur Calculée</h3>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='text-align: center; color: #FF6B6B;'>{épaisseur:.2f} mm</h1>", unsafe_allow_html=True)

    # Graphique interactif
    nb_plis_values = range(1, nb_plis + 5)
    épaisseur_values = [calcul_epaisseur_inverse(grammage, n, rho_f, V_f) for n in nb_plis_values]

    fig, ax = plt.subplots()
    ax.plot(nb_plis_values, épaisseur_values, label="Épaisseur (mm)", color="#6C63FF", linewidth=2)
    ax.scatter(nb_plis, épaisseur, color="#FF6B6B", label="Valeur actuelle", zorder=5)
    ax.set_xlabel("Nombre de plis")
    ax.set_ylabel("Épaisseur (mm)")
    ax.set_title("Variation de l'épaisseur en fonction du nombre de plis")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)
