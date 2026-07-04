import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import io

st.set_page_config(page_title="Calculs Composites - Atelier", layout="wide")

st.markdown(
    "<h1 style='text-align: center; color: #6C63FF;'>Calculs Composites - Atelier</h1>",
    unsafe_allow_html=True,
)

MATERIAUX_FIBRES = {
    "Carbone HR (T300/T700)": 1780,
    "Carbone HM": 1900,
    "Carbone UHM": 2100,
    "Verre E": 2540,
    "Verre S": 2490,
    "Aramide (Kevlar)": 1440,
    "Basalte": 2700,
    "Lin": 1500,
}

def densite_ethanol(T):
    """Densite de l'ethanol absolu en kg/m3 en fonction de T (°C). Valide 0-60°C."""
    return 806.35 - 0.8897 * T

def densite_eau(T):
    """Densite de l'eau distillee en kg/m3 en fonction de T (°C). Valide 0-60°C."""
    return 999.84 + 0.0265 * T - 0.005425 * T ** 2

def selectionner_liquide(prefix):
    """Widget de selection du liquide + calcul densite. Retourne rho_liquide en kg/m3."""
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        liquide = st.selectbox(
            "Liquide d'immersion",
            ["Ethanol", "Eau distillee", "Personnalise"],
            key=f"{prefix}_liquide",
        )
    with col_l2:
        if liquide == "Ethanol":
            temp = st.number_input(
                "Temperature ethanol (degC)",
                value=20.0, min_value=5.0, max_value=60.0,
                step=0.5, format="%.1f", key=f"{prefix}_temp",
            )
            rho = densite_ethanol(temp)
            st.success(f"Densite ethanol a {temp:.1f} °C = **{rho:.2f} kg/m3**")
        elif liquide == "Eau distillee":
            temp = st.number_input(
                "Temperature eau (degC)",
                value=20.0, min_value=0.0, max_value=60.0,
                step=0.5, format="%.1f", key=f"{prefix}_temp",
            )
            rho = densite_eau(temp)
            st.success(f"Densite eau a {temp:.1f} °C = **{rho:.2f} kg/m3**")
        else:
            rho = st.number_input(
                "Densite liquide (kg/m3)",
                value=1000, min_value=500, max_value=2000,
                key=f"{prefix}_rho_perso",
            )
    return rho

def excel_bytes(sheets):
    """Convertit un dict {nom_feuille: DataFrame} en bytes xlsx telechargeable."""
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        for name, df in sheets.items():
            df.to_excel(writer, sheet_name=name[:31], index=False)
    return buf.getvalue()

RESINES = {
    "Epoxy standard": {"densite": 1200, "ratio_durcisseur": 30},
    "Epoxy aero (RTM6)": {"densite": 1140, "ratio_durcisseur": 0},
    "Polyester": {"densite": 1120, "ratio_durcisseur": 2},
    "Vinylester": {"densite": 1150, "ratio_durcisseur": 2},
    "Phenolique": {"densite": 1300, "ratio_durcisseur": 10},
    "BMI": {"densite": 1280, "ratio_durcisseur": 0},
    "Personnalisee": {"densite": 1200, "ratio_durcisseur": 30},
}

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Taux de Fibre (Vf)",
    "Entrefer Outillage",
    "Preparation Resine",
    "Masse & Densite Composite",
    "Double Pesee / Calcination",
    "Epaisseur Composite",
])

# =============================================================================
# TAB 1 : Taux de fibre
# =============================================================================
with tab1:
    st.markdown("### Calcul du taux volumique de fibres (Vf)")

    methode_vf = st.radio(
        "Methode :",
        [
            "A partir des masses fibre/resine",
            "A partir de la fraction massique et densite composite",
            "A partir de l'epaisseur mesuree",
        ],
        horizontal=True,
        key="methode_vf",
    )

    col_mat, col_res = st.columns(2)
    with col_mat:
        fibre_type = st.selectbox("Type de fibre", list(MATERIAUX_FIBRES.keys()), key="vf_fibre")
        rho_f = st.number_input(
            "Densite fibre (kg/m3)",
            value=MATERIAUX_FIBRES[fibre_type],
            min_value=500,
            max_value=5000,
            key="vf_rho_f",
        )
    with col_res:
        resine_type = st.selectbox("Type de resine", list(RESINES.keys()), key="vf_resine")
        rho_m = st.number_input(
            "Densite matrice (kg/m3)",
            value=RESINES[resine_type]["densite"],
            min_value=500,
            max_value=3000,
            key="vf_rho_m",
        )

    st.divider()

    if methode_vf == "A partir des masses fibre/resine":
        col1, col2 = st.columns(2)
        with col1:
            m_f = st.number_input("Masse de fibres (g)", value=100.0, min_value=0.1, step=1.0, key="vf_mf")
        with col2:
            m_r = st.number_input("Masse de resine impregnee (g)", value=60.0, min_value=0.1, step=1.0, key="vf_mr")

        v_f = (m_f / rho_f) / (m_f / rho_f + m_r / rho_m)
        w_f = m_f / (m_f + m_r)
        rho_c = rho_f * v_f + rho_m * (1 - v_f)

        col_r1, col_r2, col_r3 = st.columns(3)
        col_r1.metric("Vf (taux volumique)", f"{v_f * 100:.1f} %")
        col_r2.metric("Wf (taux massique)", f"{w_f * 100:.1f} %")
        col_r3.metric("Densite composite", f"{rho_c:.0f} kg/m3")

        st.divider()
        st.markdown("#### Sensibilite Vf en fonction du ratio fibre/resine")
        ratios = np.linspace(0.3, 5.0, 200)
        vf_vals = [(1 / rho_f) / (1 / rho_f + (1 / r) / rho_m) for r in ratios]
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(ratios, [v * 100 for v in vf_vals], color="#6C63FF", linewidth=2)
        ax.axhline(y=v_f * 100, color="#FF6B6B", linestyle="--", label=f"Vf actuel = {v_f*100:.1f}%")
        ax.axvline(x=m_f / m_r, color="#FF6B6B", linestyle=":", alpha=0.5)
        ax.set_xlabel("Ratio masse fibre / masse resine")
        ax.set_ylabel("Vf (%)")
        ax.set_title("Taux volumique vs ratio fibre/resine")
        ax.legend()
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)

        df_res_vf1 = pd.DataFrame([{
            "Fibre": fibre_type, "Densite fibre (kg/m3)": rho_f,
            "Resine": resine_type, "Densite matrice (kg/m3)": rho_m,
            "Masse fibre (g)": m_f, "Masse resine (g)": m_r,
            "Vf (%)": round(v_f * 100, 2), "Wf (%)": round(w_f * 100, 2),
            "Densite composite (kg/m3)": round(rho_c, 1),
        }])
        df_sens_vf1 = pd.DataFrame({"Ratio mf/mr": ratios, "Vf (%)": [v * 100 for v in vf_vals]})
        st.download_button(
            "Exporter Excel", excel_bytes({"Resultats": df_res_vf1, "Sensibilite": df_sens_vf1}),
            "taux_fibre.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="dl_tab1_m1",
        )

    elif methode_vf == "A partir de la fraction massique et densite composite":
        col1, col2 = st.columns(2)
        with col1:
            w_f_input = st.slider("Fraction massique fibres Wf (%)", 20.0, 90.0, 65.0, step=0.5, key="vf_wf")
        with col2:
            rho_c_input = st.number_input("Densite composite mesuree (kg/m3)", value=1550, min_value=800, max_value=3000, key="vf_rho_c")

        v_f = (w_f_input / 100) * rho_c_input / rho_f
        v_m = (1 - w_f_input / 100) * rho_c_input / rho_m
        v_p = 1 - v_f - v_m

        col_r1, col_r2, col_r3 = st.columns(3)
        col_r1.metric("Vf (taux volumique)", f"{v_f * 100:.1f} %")
        col_r2.metric("Vm (taux matrice)", f"{v_m * 100:.1f} %")
        col_r3.metric("Vp (taux porosite)", f"{v_p * 100:.1f} %")

        if v_p < 0:
            st.warning("Porosite negative : verifiez la coherence des donnees (densite composite trop elevee).")

        df_res_vf2 = pd.DataFrame([{
            "Fibre": fibre_type, "Densite fibre (kg/m3)": rho_f,
            "Resine": resine_type, "Densite matrice (kg/m3)": rho_m,
            "Wf (%)": w_f_input, "Densite composite mesuree (kg/m3)": rho_c_input,
            "Vf (%)": round(v_f * 100, 2), "Vm (%)": round(v_m * 100, 2),
            "Vp - Porosite (%)": round(v_p * 100, 2),
        }])
        st.download_button(
            "Exporter Excel", excel_bytes({"Resultats": df_res_vf2}),
            "taux_fibre.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="dl_tab1_m2",
        )

    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            grammage = st.number_input("Grammage fibre (g/m2)", value=300, min_value=50, max_value=3000, key="vf_gram")
        with col2:
            nb_plis = st.number_input("Nombre de plis", value=8, min_value=1, max_value=100, key="vf_plis")
        with col3:
            ep_mesuree = st.number_input("Epaisseur mesuree (mm)", value=2.50, min_value=0.1, step=0.01, format="%.2f", key="vf_ep")

        masse_surf_fibre = grammage * nb_plis / 1000  # kg/m2
        v_f = masse_surf_fibre / (rho_f * ep_mesuree / 1000)

        ep_par_pli = ep_mesuree / nb_plis

        col_r1, col_r2 = st.columns(2)
        col_r1.metric("Vf (taux volumique)", f"{v_f * 100:.1f} %")
        col_r2.metric("Epaisseur par pli", f"{ep_par_pli:.3f} mm")

        if v_f > 0.75:
            st.warning("Vf > 75% : valeur anormalement elevee, verifiez les donnees.")

        df_res_vf3 = pd.DataFrame([{
            "Fibre": fibre_type, "Densite fibre (kg/m3)": rho_f,
            "Grammage (g/m2)": grammage, "Nombre de plis": nb_plis,
            "Epaisseur mesuree (mm)": ep_mesuree,
            "Vf (%)": round(v_f * 100, 2), "Epaisseur par pli (mm)": round(ep_par_pli, 4),
        }])
        st.download_button(
            "Exporter Excel", excel_bytes({"Resultats": df_res_vf3}),
            "taux_fibre.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="dl_tab1_m3",
        )


# =============================================================================
# TAB 2 : Entrefer outillage
# =============================================================================
with tab2:
    st.markdown("### Calcul de l'entrefer outillage pour un Vf cible")
    st.markdown(
        "Determine l'ecartement (entrefer) entre moule et contre-moule "
        "pour obtenir le taux de fibre souhaite (RTM, compression, etc.)."
    )

    col_mat2, col_param2 = st.columns(2)
    with col_mat2:
        fibre_type2 = st.selectbox("Type de fibre", list(MATERIAUX_FIBRES.keys()), key="ent_fibre")
        rho_f2 = st.number_input(
            "Densite fibre (kg/m3)",
            value=MATERIAUX_FIBRES[fibre_type2],
            min_value=500,
            max_value=5000,
            key="ent_rho_f",
        )
    with col_param2:
        vf_cible = st.slider("Vf cible (%)", 30.0, 70.0, 60.0, step=0.5, key="ent_vf") / 100
        grammage2 = st.number_input("Grammage fibre (g/m2)", value=300, min_value=50, max_value=3000, key="ent_gram")

    nb_plis2 = st.number_input("Nombre de plis", value=8, min_value=1, max_value=100, key="ent_plis")

    masse_surf = grammage2 * nb_plis2 / 1000  # kg/m2
    entrefer = masse_surf / (rho_f2 * vf_cible) * 1000  # mm
    ep_par_pli2 = entrefer / nb_plis2

    col_r1, col_r2, col_r3 = st.columns(3)
    col_r1.metric("Entrefer (epaisseur)", f"{entrefer:.3f} mm")
    col_r2.metric("Epaisseur par pli", f"{ep_par_pli2:.4f} mm")
    col_r3.metric("Masse surfacique fibres", f"{masse_surf * 1000:.0f} g/m2")

    st.divider()

    st.markdown("#### Tableau entrefer en fonction de Vf et nombre de plis")
    vf_range = np.arange(0.40, 0.71, 0.05)
    plis_range = range(max(1, nb_plis2 - 4), nb_plis2 + 6)
    data_entrefer = {}
    for vf_val in vf_range:
        col_name = f"Vf={vf_val*100:.0f}%"
        data_entrefer[col_name] = [
            f"{(grammage2 * n / 1000) / (rho_f2 * vf_val) * 1000:.3f}"
            for n in plis_range
        ]
    df_entrefer = pd.DataFrame(data_entrefer, index=[f"{n} plis" for n in plis_range])
    st.dataframe(df_entrefer, use_container_width=True)

    st.divider()
    st.markdown("#### Courbe entrefer vs Vf")
    vf_plot = np.linspace(0.30, 0.75, 200)
    entrefer_plot = [masse_surf / (rho_f2 * vf) * 1000 for vf in vf_plot]
    fig2, ax2 = plt.subplots(figsize=(8, 4))
    ax2.plot(vf_plot * 100, entrefer_plot, color="#6C63FF", linewidth=2)
    ax2.axhline(y=entrefer, color="#FF6B6B", linestyle="--", label=f"Entrefer = {entrefer:.3f} mm")
    ax2.axvline(x=vf_cible * 100, color="#FF6B6B", linestyle=":", alpha=0.5)
    ax2.scatter([vf_cible * 100], [entrefer], color="#FF6B6B", s=100, zorder=5)
    ax2.set_xlabel("Vf (%)")
    ax2.set_ylabel("Entrefer (mm)")
    ax2.set_title(f"Entrefer vs Vf ({nb_plis2} plis, grammage {grammage2} g/m2)")
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    st.pyplot(fig2)

    df_res_ent = pd.DataFrame([{
        "Fibre": fibre_type2, "Densite fibre (kg/m3)": rho_f2,
        "Grammage (g/m2)": grammage2, "Nombre de plis": nb_plis2,
        "Vf cible (%)": round(vf_cible * 100, 1),
        "Entrefer (mm)": round(entrefer, 3),
        "Epaisseur par pli (mm)": round(ep_par_pli2, 4),
        "Masse surfacique fibres (g/m2)": round(masse_surf * 1000, 1),
    }])
    df_courbe_ent = pd.DataFrame({"Vf (%)": vf_plot * 100, "Entrefer (mm)": entrefer_plot})
    st.download_button(
        "Exporter Excel",
        excel_bytes({"Resultats": df_res_ent, "Tableau Vf-Plis": df_entrefer.reset_index(), "Courbe": df_courbe_ent}),
        "entrefer.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="dl_tab2",
    )


# =============================================================================
# TAB 3 : Preparation resine
# =============================================================================
with tab3:
    st.markdown("### Preparation de resine")
    st.markdown("Calcul des masses de resine et durcisseur pour la fabrication.")

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        resine_type3 = st.selectbox("Systeme resine", list(RESINES.keys()), key="prep_resine")
        rho_resine = st.number_input(
            "Densite resine melangee (kg/m3)",
            value=RESINES[resine_type3]["densite"],
            min_value=500,
            max_value=2000,
            key="prep_rho",
        )

    with col_r2:
        ratio_phr = st.number_input(
            "Ratio durcisseur (PHR = parts pour 100 parts resine)",
            value=RESINES[resine_type3]["ratio_durcisseur"],
            min_value=0,
            max_value=200,
            key="prep_ratio",
        )
        perte_pct = st.number_input(
            "Marge / pertes (%)",
            value=10,
            min_value=0,
            max_value=100,
            key="prep_perte",
        )

    st.divider()

    mode_prep = st.radio(
        "Mode de calcul :",
        [
            "Masse totale de melange souhaitee",
            "A partir des dimensions et Vf",
        ],
        horizontal=True,
        key="prep_mode",
    )

    if mode_prep == "Masse totale de melange souhaitee":
        masse_totale = st.number_input(
            "Masse totale resine + durcisseur (g)",
            value=500.0,
            min_value=1.0,
            step=10.0,
            key="prep_mtot",
        )
    else:
        col_d1, col_d2, col_d3 = st.columns(3)
        with col_d1:
            fibre_type3 = st.selectbox("Type de fibre", list(MATERIAUX_FIBRES.keys()), key="prep_fibre")
            rho_f3 = MATERIAUX_FIBRES[fibre_type3]
        with col_d2:
            grammage3 = st.number_input("Grammage fibre (g/m2)", value=300, min_value=50, key="prep_gram")
            nb_plis3 = st.number_input("Nombre de plis", value=8, min_value=1, key="prep_plis")
        with col_d3:
            surf3 = st.number_input("Surface piece (m2)", value=0.1, min_value=0.001, step=0.01, format="%.3f", key="prep_surf")
            vf3 = st.slider("Vf cible (%)", 30.0, 70.0, 55.0, step=0.5, key="prep_vf") / 100

        masse_fibre_kg = grammage3 * nb_plis3 / 1000 * surf3  # kg
        ep_composite = (grammage3 * nb_plis3 / 1000) / (rho_f3 * vf3)  # m
        vol_composite = surf3 * ep_composite  # m3
        vol_resine = vol_composite * (1 - vf3)  # m3
        masse_totale = vol_resine * rho_resine  # g (rho en kg/m3 -> * 1000 pour g, mais vol en m3)
        masse_totale = masse_totale * 1000  # conversion en g

        st.info(f"Masse de fibres : {masse_fibre_kg * 1000:.1f} g | Volume resine : {vol_resine * 1e6:.1f} cm3 | Masse resine calculee : {masse_totale:.1f} g")

    masse_avec_perte = masse_totale * (1 + perte_pct / 100)

    if ratio_phr > 0:
        masse_resine_pure = masse_avec_perte / (1 + ratio_phr / 100)
        masse_durcisseur = masse_avec_perte - masse_resine_pure
    else:
        masse_resine_pure = masse_avec_perte
        masse_durcisseur = 0

    st.divider()
    st.markdown("#### Resultat preparation")
    col_p1, col_p2, col_p3, col_p4 = st.columns(4)
    col_p1.metric("Masse resine", f"{masse_resine_pure:.1f} g")
    col_p2.metric("Masse durcisseur", f"{masse_durcisseur:.1f} g")
    col_p3.metric("Masse totale", f"{masse_avec_perte:.1f} g")
    col_p4.metric("Dont marge pertes", f"{masse_avec_perte - masse_totale:.1f} g")

    if ratio_phr > 0:
        fig3, ax3 = plt.subplots(figsize=(4, 4))
        sizes = [masse_resine_pure, masse_durcisseur]
        labels = [f"Resine\n{masse_resine_pure:.1f} g", f"Durcisseur\n{masse_durcisseur:.1f} g"]
        colors = ["#6C63FF", "#FF6B6B"]
        ax3.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=90)
        ax3.set_title("Repartition resine / durcisseur")
        st.pyplot(fig3)

    df_prep = pd.DataFrame([{
        "Systeme resine": resine_type3, "Densite (kg/m3)": rho_resine,
        "Ratio durcisseur (PHR)": ratio_phr, "Marge pertes (%)": perte_pct,
        "Masse resine (g)": round(masse_resine_pure, 2),
        "Masse durcisseur (g)": round(masse_durcisseur, 2),
        "Masse totale avec pertes (g)": round(masse_avec_perte, 2),
        "Masse pertes (g)": round(masse_avec_perte - masse_totale, 2),
    }])
    st.download_button(
        "Exporter Excel", excel_bytes({"Preparation resine": df_prep}),
        "preparation_resine.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="dl_tab3",
    )


# =============================================================================
# TAB 4 : Masse et densite composite
# =============================================================================
with tab4:
    st.markdown("### Determination masse et densite composite")

    methode_densite = st.radio(
        "Methode :",
        [
            "Loi des melanges (theorique)",
            "Double pesee (Archimede)",
        ],
        horizontal=True,
        key="densite_methode",
    )

    if methode_densite == "Loi des melanges (theorique)":
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            fibre_type4 = st.selectbox("Type de fibre", list(MATERIAUX_FIBRES.keys()), key="dens_fibre")
            rho_f4 = st.number_input("Densite fibre (kg/m3)", value=MATERIAUX_FIBRES[fibre_type4], key="dens_rho_f")
        with col_t2:
            resine_type4 = st.selectbox("Type de resine", list(RESINES.keys()), key="dens_resine")
            rho_m4 = st.number_input("Densite matrice (kg/m3)", value=RESINES[resine_type4]["densite"], key="dens_rho_m")

        vf4 = st.slider("Vf (%)", 30.0, 75.0, 60.0, step=0.5, key="dens_vf") / 100

        rho_c4 = rho_f4 * vf4 + rho_m4 * (1 - vf4)

        col_d1, col_d2 = st.columns(2)
        with col_d1:
            surf4 = st.number_input("Surface piece (m2)", value=0.1, min_value=0.001, step=0.01, format="%.3f", key="dens_surf")
        with col_d2:
            ep4 = st.number_input("Epaisseur (mm)", value=2.5, min_value=0.1, step=0.1, format="%.2f", key="dens_ep")

        vol4 = surf4 * ep4 / 1000  # m3
        masse4 = rho_c4 * vol4 * 1000  # g

        col_r1, col_r2, col_r3 = st.columns(3)
        col_r1.metric("Densite composite", f"{rho_c4:.0f} kg/m3")
        col_r2.metric("Masse composite", f"{masse4:.1f} g")
        col_r3.metric("Volume composite", f"{vol4 * 1e6:.2f} cm3")

        st.divider()
        st.markdown("#### Densite composite en fonction de Vf")
        vf_range4 = np.linspace(0.0, 0.80, 200)
        rho_c_range = rho_f4 * vf_range4 + rho_m4 * (1 - vf_range4)
        fig4, ax4 = plt.subplots(figsize=(8, 4))
        ax4.plot(vf_range4 * 100, rho_c_range, color="#6C63FF", linewidth=2)
        ax4.scatter([vf4 * 100], [rho_c4], color="#FF6B6B", s=100, zorder=5)
        ax4.axhline(y=rho_f4, color="gray", linestyle="--", alpha=0.5, label=f"Fibre = {rho_f4}")
        ax4.axhline(y=rho_m4, color="gray", linestyle=":", alpha=0.5, label=f"Matrice = {rho_m4}")
        ax4.set_xlabel("Vf (%)")
        ax4.set_ylabel("Densite composite (kg/m3)")
        ax4.set_title("Loi des melanges")
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        st.pyplot(fig4)

        df_res_dens = pd.DataFrame([{
            "Fibre": fibre_type4, "Densite fibre (kg/m3)": rho_f4,
            "Resine": resine_type4, "Densite matrice (kg/m3)": rho_m4,
            "Vf (%)": round(vf4 * 100, 1),
            "Densite composite (kg/m3)": round(rho_c4, 1),
            "Surface (m2)": surf4, "Epaisseur (mm)": ep4,
            "Volume (cm3)": round(vol4 * 1e6, 2),
            "Masse composite (g)": round(masse4, 1),
        }])
        df_courbe_dens = pd.DataFrame({"Vf (%)": vf_range4 * 100, "Densite composite (kg/m3)": rho_c_range})
        st.download_button(
            "Exporter Excel",
            excel_bytes({"Resultats": df_res_dens, "Courbe densite-Vf": df_courbe_dens}),
            "densite_composite.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="dl_tab4_m1",
        )

    else:
        st.markdown(
            "Methode par double pesee (principe d'Archimede) : "
            "peser l'echantillon dans l'air puis immerge dans un liquide de densite connue."
        )
        rho_liquide = selectionner_liquide("arch")
        nb_echantillons = st.number_input(
            "Nombre d'echantillons",
            value=3,
            min_value=1,
            max_value=20,
            key="arch_nb",
        )

        st.divider()
        masses_air = []
        masses_imm = []
        cols_header = st.columns([1, 2, 2])
        cols_header[0].markdown("**Ech.**")
        cols_header[1].markdown("**Masse air (g)**")
        cols_header[2].markdown("**Masse immergee (g)**")

        for i in range(nb_echantillons):
            cols = st.columns([1, 2, 2])
            cols[0].markdown(f"**{i+1}**")
            m_air = cols[1].number_input(
                f"m_air_{i+1}", value=5.00, min_value=0.01, step=0.01,
                format="%.2f", key=f"arch_air_{i}", label_visibility="collapsed",
            )
            m_imm = cols[2].number_input(
                f"m_imm_{i+1}", value=3.50, min_value=0.01, step=0.01,
                format="%.2f", key=f"arch_imm_{i}", label_visibility="collapsed",
            )
            masses_air.append(m_air)
            masses_imm.append(m_imm)

        st.divider()
        st.markdown("#### Resultats double pesee")
        resultats = []
        for i in range(nb_echantillons):
            delta = masses_air[i] - masses_imm[i]
            if delta > 0:
                rho_ech = masses_air[i] * rho_liquide / delta
                vol_ech = masses_air[i] / rho_ech * 1000  # cm3
            else:
                rho_ech = 0
                vol_ech = 0
            resultats.append({
                "Echantillon": i + 1,
                "Masse air (g)": masses_air[i],
                "Masse imm. (g)": masses_imm[i],
                "Densite (kg/m3)": round(rho_ech, 1),
                "Volume (cm3)": round(vol_ech, 3),
            })

        df_arch = pd.DataFrame(resultats)
        densites = [r["Densite (kg/m3)"] for r in resultats if r["Densite (kg/m3)"] > 0]

        if densites:
            moy = np.mean(densites)
            ecart = np.std(densites)
            df_arch.loc[len(df_arch)] = {
                "Echantillon": "Moyenne",
                "Masse air (g)": "",
                "Masse imm. (g)": "",
                "Densite (kg/m3)": round(moy, 1),
                "Volume (cm3)": "",
            }
        st.dataframe(df_arch, use_container_width=True, hide_index=True)

        if densites and len(densites) > 1:
            col_stat1, col_stat2 = st.columns(2)
            col_stat1.metric("Densite moyenne", f"{moy:.1f} kg/m3")
            col_stat2.metric("Ecart-type", f"{ecart:.1f} kg/m3")

            fig_arch, ax_arch = plt.subplots(figsize=(8, 4))
            x_pos = range(1, len(densites) + 1)
            ax_arch.bar(x_pos, densites, color="#6C63FF", alpha=0.7)
            ax_arch.axhline(y=moy, color="#FF6B6B", linestyle="--", label=f"Moyenne = {moy:.1f}")
            ax_arch.fill_between(
                [0.5, len(densites) + 0.5],
                moy - ecart, moy + ecart,
                alpha=0.15, color="#FF6B6B", label=f"+/- 1 ecart-type",
            )
            ax_arch.set_xlabel("Echantillon")
            ax_arch.set_ylabel("Densite (kg/m3)")
            ax_arch.set_title("Densite par echantillon (double pesee)")
            ax_arch.set_xticks(list(x_pos))
            ax_arch.legend()
            ax_arch.grid(True, alpha=0.3, axis="y")
            st.pyplot(fig_arch)

        st.download_button(
            "Exporter Excel", excel_bytes({"Pesees Archimede": df_arch}),
            "double_pesee.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="dl_tab4_m2",
        )


# =============================================================================
# TAB 5 : Double pesee + Calcination
# =============================================================================
with tab5:
    st.markdown("### Double pesee et calcination")
    st.markdown(
        "Determiner le taux de fibre reel par calcination (perte au feu) : "
        "peser l'echantillon, calciner pour bruler la matrice, puis peser le residu fibreux."
    )

    col_c1, col_c2 = st.columns(2)
    with col_c1:
        fibre_type5 = st.selectbox("Type de fibre", list(MATERIAUX_FIBRES.keys()), key="calc_fibre")
        rho_f5 = st.number_input("Densite fibre (kg/m3)", value=MATERIAUX_FIBRES[fibre_type5], key="calc_rho_f")
    with col_c2:
        resine_type5 = st.selectbox("Type de resine", list(RESINES.keys()), key="calc_resine")
        rho_m5 = st.number_input("Densite matrice (kg/m3)", value=RESINES[resine_type5]["densite"], key="calc_rho_m")

    nb_ech5 = st.number_input("Nombre d'echantillons", value=5, min_value=1, max_value=30, key="calc_nb")

    st.divider()
    st.markdown("#### Liquide double pesee *(optionnel — pour calcul densite et porosite)*")
    rho_liq5 = selectionner_liquide("calc5")

    st.divider()
    st.markdown("#### Saisie des pesees")

    headers = st.columns([1, 2, 2, 2, 2, 2])
    headers[0].markdown("**Ech.**")
    headers[1].markdown("**Creuset vide (g)**")
    headers[2].markdown("**Creuset + ech. avant (g)**")
    headers[3].markdown("**Masse air ech. (g)** *(opt.)*")
    headers[4].markdown("**Masse immergee (g)** *(opt.)*")
    headers[5].markdown("**Creuset + residu apres (g)**")

    m_creuset = []
    m_avant = []
    m_air_opt = []
    m_imm_opt = []
    m_apres = []

    for i in range(nb_ech5):
        cols = st.columns([1, 2, 2, 2, 2, 2])
        cols[0].markdown(f"**{i+1}**")
        mc = cols[1].number_input(
            f"creuset_{i}", value=30.00, step=0.01, format="%.2f",
            key=f"calc_mc_{i}", label_visibility="collapsed",
        )
        ma = cols[2].number_input(
            f"avant_{i}", value=35.00, step=0.01, format="%.2f",
            key=f"calc_ma_{i}", label_visibility="collapsed",
        )
        m_air = cols[3].number_input(
            f"air_{i}", value=0.00, step=0.01, format="%.2f",
            key=f"calc_mair_{i}", label_visibility="collapsed",
            help="Laisser a 0 si pas de double pesee",
        )
        m_imm = cols[4].number_input(
            f"imm_{i}", value=0.00, step=0.01, format="%.2f",
            key=f"calc_mimm_{i}", label_visibility="collapsed",
            help="Masse immergee dans le liquide (0 si non renseignee)",
        )
        mp = cols[5].number_input(
            f"apres_{i}", value=33.00, step=0.01, format="%.2f",
            key=f"calc_mp_{i}", label_visibility="collapsed",
        )
        m_creuset.append(mc)
        m_avant.append(ma)
        m_air_opt.append(m_air)
        m_imm_opt.append(m_imm)
        m_apres.append(mp)

    st.divider()
    st.markdown("#### Resultats calcination")

    results_calc = []
    for i in range(nb_ech5):
        m_ech = m_avant[i] - m_creuset[i]
        m_fibre = m_apres[i] - m_creuset[i]
        m_resine_perdue = m_ech - m_fibre

        if m_ech > 0:
            wf = m_fibre / m_ech * 100
            wm = m_resine_perdue / m_ech * 100
        else:
            wf = 0
            wm = 0

        vf = 0
        rho_c_calc = 0
        vp = 0
        double_pesee_ok = m_air_opt[i] > 0 and m_imm_opt[i] > 0 and (m_air_opt[i] - m_imm_opt[i]) > 0
        if m_ech > 0 and rho_f5 > 0 and rho_m5 > 0:
            vol_f = m_fibre / rho_f5
            vol_m = m_resine_perdue / rho_m5
            vol_total_theo = vol_f + vol_m

            if double_pesee_ok:
                # Archimede : rho = m_air * rho_liq / (m_air - m_imm)
                delta_imm = m_air_opt[i] - m_imm_opt[i]
                rho_c_calc = m_air_opt[i] * rho_liq5 / delta_imm
                vol_total_reel = m_ech / rho_c_calc if rho_c_calc > 0 else vol_total_theo
            else:
                vol_total_reel = vol_total_theo
                rho_c_calc = m_ech / vol_total_theo * 1000 if vol_total_theo > 0 else 0

            vf = vol_f / vol_total_reel * 100 if vol_total_reel > 0 else 0
            vm = vol_m / vol_total_reel * 100 if vol_total_reel > 0 else 0
            vp = 100 - vf - vm if double_pesee_ok else 0

        results_calc.append({
            "Echantillon": i + 1,
            "Masse ech. (g)": round(m_ech, 3),
            "Masse fibre (g)": round(m_fibre, 3),
            "Wf (%)": round(wf, 1),
            "Wm (%)": round(wm, 1),
            "Vf (%)": round(vf, 1),
            "Densite (kg/m3)": round(rho_c_calc, 0),
        })

    df_calc = pd.DataFrame(results_calc)

    vf_values = [r["Vf (%)"] for r in results_calc if r["Vf (%)"] > 0]
    wf_values = [r["Wf (%)"] for r in results_calc if r["Wf (%)"] > 0]

    if vf_values:
        moy_vf = np.mean(vf_values)
        std_vf = np.std(vf_values)
        moy_wf = np.mean(wf_values)
        std_wf = np.std(wf_values)

        summary = pd.DataFrame([{
            "Echantillon": "Moyenne",
            "Masse ech. (g)": "",
            "Masse fibre (g)": "",
            "Wf (%)": round(moy_wf, 1),
            "Wm (%)": round(100 - moy_wf, 1),
            "Vf (%)": round(moy_vf, 1),
            "Densite (kg/m3)": "",
        }, {
            "Echantillon": "Ecart-type",
            "Masse ech. (g)": "",
            "Masse fibre (g)": "",
            "Wf (%)": round(std_wf, 1),
            "Wm (%)": "",
            "Vf (%)": round(std_vf, 1),
            "Densite (kg/m3)": "",
        }])
        df_display = pd.concat([df_calc, summary], ignore_index=True)
    else:
        df_display = df_calc

    st.dataframe(df_display, use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("#### Graphiques")

    if vf_values and len(vf_values) > 1:
        fig5, axes5 = plt.subplots(1, 3, figsize=(16, 5))

        # Vf par echantillon
        x5 = range(1, len(vf_values) + 1)
        axes5[0].bar(x5, vf_values, color="#6C63FF", alpha=0.7)
        axes5[0].axhline(y=moy_vf, color="#FF6B6B", linestyle="--", label=f"Moy = {moy_vf:.1f}%")
        axes5[0].fill_between(
            [0.5, len(vf_values) + 0.5],
            moy_vf - std_vf, moy_vf + std_vf,
            alpha=0.15, color="#FF6B6B",
        )
        axes5[0].set_xlabel("Echantillon")
        axes5[0].set_ylabel("Vf (%)")
        axes5[0].set_title("Taux volumique de fibres")
        axes5[0].set_xticks(list(x5))
        axes5[0].legend()
        axes5[0].grid(True, alpha=0.3, axis="y")

        # Wf par echantillon
        axes5[1].bar(x5, wf_values, color="#4CAF50", alpha=0.7)
        axes5[1].axhline(y=moy_wf, color="#FF6B6B", linestyle="--", label=f"Moy = {moy_wf:.1f}%")
        axes5[1].set_xlabel("Echantillon")
        axes5[1].set_ylabel("Wf (%)")
        axes5[1].set_title("Taux massique de fibres")
        axes5[1].set_xticks(list(x5))
        axes5[1].legend()
        axes5[1].grid(True, alpha=0.3, axis="y")

        # Masses fibre vs resine
        m_fibres_list = [r["Masse fibre (g)"] for r in results_calc if r["Masse ech. (g)"] > 0]
        m_resine_list = [r["Masse ech. (g)"] - r["Masse fibre (g)"] for r in results_calc if r["Masse ech. (g)"] > 0]
        x5b = np.arange(1, len(m_fibres_list) + 1)
        width = 0.35
        axes5[2].bar(x5b - width / 2, m_fibres_list, width, label="Fibres", color="#6C63FF", alpha=0.7)
        axes5[2].bar(x5b + width / 2, m_resine_list, width, label="Resine", color="#FF6B6B", alpha=0.7)
        axes5[2].set_xlabel("Echantillon")
        axes5[2].set_ylabel("Masse (g)")
        axes5[2].set_title("Masse fibre vs resine")
        axes5[2].set_xticks(list(x5b))
        axes5[2].legend()
        axes5[2].grid(True, alpha=0.3, axis="y")

        plt.tight_layout()
        st.pyplot(fig5)

        # Distribution / histogramme
        if len(vf_values) >= 3:
            fig_hist, ax_hist = plt.subplots(figsize=(8, 4))
            ax_hist.hist(vf_values, bins=max(3, len(vf_values) // 2), color="#6C63FF", alpha=0.7, edgecolor="white")
            ax_hist.axvline(x=moy_vf, color="#FF6B6B", linestyle="--", linewidth=2, label=f"Moyenne = {moy_vf:.1f}%")
            ax_hist.set_xlabel("Vf (%)")
            ax_hist.set_ylabel("Frequence")
            ax_hist.set_title("Distribution du taux volumique de fibres")
            ax_hist.legend()
            ax_hist.grid(True, alpha=0.3, axis="y")
            st.pyplot(fig_hist)

    elif vf_values:
        st.info("Ajoutez plus d'echantillons pour voir les graphiques statistiques.")

    st.divider()
    df_pesees_brutes = pd.DataFrame({
        "Echantillon": list(range(1, nb_ech5 + 1)),
        "Creuset vide (g)": m_creuset,
        "Creuset + ech. avant (g)": m_avant,
        "Masse air ech. (g)": m_air_opt,
        "Masse immergee (g)": m_imm_opt,
        "Creuset + residu apres (g)": m_apres,
    })
    st.download_button(
        "Exporter Excel",
        excel_bytes({"Resultats calcination": df_display, "Pesees brutes": df_pesees_brutes}),
        "calcination.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="dl_tab5",
    )


# =============================================================================
# TAB 6 : Epaisseur composite (reprise du code existant ameliore)
# =============================================================================
with tab6:
    st.markdown("### Calcul d'epaisseur pour composites")

    method = st.radio(
        "Methode de calcul :",
        (
            "Methode 1 : Basee sur la masse de fibres",
            "Methode 2 : Basee sur le grammage et le nombre de plis",
        ),
        index=0,
        horizontal=True,
        key="ep_method",
    )

    def calcul_epaisseur_masse(m_f, A, V_f, rho_f):
        V_fibres = m_f / rho_f
        V_total = V_fibres / V_f
        return (V_total / A) * 1000

    def calcul_resine(m_f, V_f, rho_f, rho_m):
        V_fibres = m_f / rho_f
        V_total = V_fibres / V_f
        V_resine = V_total * (1 - V_f)
        return V_resine * rho_m * 1000

    def calcul_epaisseur_inverse(grammage, nb_plis, rho_f, V_f):
        grammage_kg_m2 = grammage / 1000
        V_total_per_m2 = (grammage_kg_m2 * nb_plis) / (rho_f * V_f)
        return V_total_per_m2 * 1000

    if method == "Methode 1 : Basee sur la masse de fibres":
        col1, col2 = st.columns(2)
        with col1:
            fibre_type6 = st.selectbox("Type de fibre", list(MATERIAUX_FIBRES.keys()), key="ep_fibre")
            rho_f6 = st.number_input("Densite fibre (kg/m3)", value=MATERIAUX_FIBRES[fibre_type6], key="ep_rho_f")
        with col2:
            rho_m6 = st.number_input("Densite matrice (kg/m3)", value=1200, min_value=800, max_value=1500, key="ep_rho_m")

        col_a, col_b = st.columns(2)
        with col_a:
            largeur = st.number_input("Largeur (mm)", value=200, min_value=10, key="ep_larg")
        with col_b:
            longueur = st.number_input("Longueur (mm)", value=200, min_value=10, key="ep_long")

        m_f6 = st.number_input("Masse de fibres (g)", value=100.0, min_value=0.1, step=1.0, key="ep_mf")
        V_f6 = st.slider("Fraction volumique de fibres (Vf)", 0.3, 0.7, 0.6, step=0.01, key="ep_vf")

        A = (largeur * longueur) / 1e6
        epaisseur6 = calcul_epaisseur_masse(m_f6 / 1000, A, V_f6, rho_f6)
        masse_resine6 = calcul_resine(m_f6 / 1000, V_f6, rho_f6, rho_m6)

        col_r1, col_r2 = st.columns(2)
        col_r1.metric("Epaisseur calculee", f"{epaisseur6:.2f} mm")
        col_r2.metric("Masse resine necessaire", f"{masse_resine6:.2f} g")

        V_f_values = np.linspace(0.3, 0.7, 100)
        ep_values = [calcul_epaisseur_masse(m_f6 / 1000, A, vf, rho_f6) for vf in V_f_values]
        fig6, ax6 = plt.subplots(figsize=(8, 4))
        ax6.plot(V_f_values, ep_values, color="#6C63FF", linewidth=2)
        ax6.scatter(V_f6, epaisseur6, color="#FF6B6B", s=100, zorder=5, label="Valeur actuelle")
        ax6.set_xlabel("Vf")
        ax6.set_ylabel("Epaisseur (mm)")
        ax6.set_title("Epaisseur en fonction de Vf")
        ax6.legend()
        ax6.grid(True, alpha=0.3)
        st.pyplot(fig6)

        df_res_ep1 = pd.DataFrame([{
            "Fibre": fibre_type6, "Densite fibre (kg/m3)": rho_f6,
            "Densite matrice (kg/m3)": rho_m6,
            "Largeur (mm)": largeur, "Longueur (mm)": longueur,
            "Masse fibres (g)": m_f6, "Vf (%)": round(V_f6 * 100, 1),
            "Epaisseur calculee (mm)": round(epaisseur6, 3),
            "Masse resine (g)": round(masse_resine6, 2),
        }])
        df_courbe_ep1 = pd.DataFrame({"Vf (%)": V_f_values * 100, "Epaisseur (mm)": ep_values})
        st.download_button(
            "Exporter Excel",
            excel_bytes({"Resultats": df_res_ep1, "Courbe Vf": df_courbe_ep1}),
            "epaisseur.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="dl_tab6_m1",
        )

    else:
        col1, col2 = st.columns(2)
        with col1:
            fibre_type6b = st.selectbox("Type de fibre", list(MATERIAUX_FIBRES.keys()), key="ep_fibre2")
            rho_f6b = st.number_input("Densite fibre (kg/m3)", value=MATERIAUX_FIBRES[fibre_type6b], key="ep_rho_f2")
        with col2:
            grammage6 = st.number_input("Grammage surfacique (g/m2)", value=300, min_value=100, max_value=2000, key="ep_gram")

        nb_plis6 = st.number_input("Nombre de plis", min_value=1, max_value=100, value=5, step=1, key="ep_plis")
        V_f6b = st.slider("Fraction volumique de fibres (Vf)", 0.3, 0.7, 0.6, step=0.01, key="ep_vf2")

        epaisseur6b = calcul_epaisseur_inverse(grammage6, nb_plis6, rho_f6b, V_f6b)
        st.metric("Epaisseur calculee", f"{epaisseur6b:.2f} mm")

        nb_plis_values = range(1, nb_plis6 + 10)
        ep_values_b = [calcul_epaisseur_inverse(grammage6, n, rho_f6b, V_f6b) for n in nb_plis_values]
        fig6b, ax6b = plt.subplots(figsize=(8, 4))
        ax6b.plot(list(nb_plis_values), ep_values_b, color="#6C63FF", linewidth=2)
        ax6b.scatter(nb_plis6, epaisseur6b, color="#FF6B6B", s=100, zorder=5, label="Valeur actuelle")
        ax6b.set_xlabel("Nombre de plis")
        ax6b.set_ylabel("Epaisseur (mm)")
        ax6b.set_title("Epaisseur en fonction du nombre de plis")
        ax6b.legend()
        ax6b.grid(True, alpha=0.3)
        st.pyplot(fig6b)

        df_res_ep2 = pd.DataFrame([{
            "Fibre": fibre_type6b, "Densite fibre (kg/m3)": rho_f6b,
            "Grammage (g/m2)": grammage6, "Nombre de plis": nb_plis6,
            "Vf (%)": round(V_f6b * 100, 1),
            "Epaisseur calculee (mm)": round(epaisseur6b, 3),
        }])
        df_courbe_ep2 = pd.DataFrame({"Nombre de plis": list(nb_plis_values), "Epaisseur (mm)": ep_values_b})
        st.download_button(
            "Exporter Excel",
            excel_bytes({"Resultats": df_res_ep2, "Courbe plis": df_courbe_ep2}),
            "epaisseur.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="dl_tab6_m2",
        )
