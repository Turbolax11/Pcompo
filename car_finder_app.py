# -*- coding: utf-8 -*-
"""
Chasseur d'occasions - recherche multi-sites de voitures d'occasion.

Lancer avec :  streamlit run car_finder_app.py

Principe :
  1. On saisit les criteres (marque, modele, finition, annees, km, prix, ...)
  2. L'app interroge les sites qui le permettent (AutoScout24, Leboncoin,
     ParuVendu) et recupere les annonces.
  3. Elle genere aussi les liens de recherche directs vers tous les grands
     sites (La Centrale, Leboncoin, L'Argus, ...) car certains bloquent les
     robots.
  4. Sur les annonces recuperees, elle estime le prix "normal" du modele
     (regression prix ~ km + age) et met en avant les annonces SOUS-COTEES.
"""

import io
import json
import re
import time
from urllib.parse import quote_plus, urlencode

import numpy as np
import pandas as pd
import requests
import streamlit as st
from bs4 import BeautifulSoup

from car_data import MARQUES, modeles as modeles_de, finitions as finitions_de

st.set_page_config(page_title="Chasseur d'occasions", page_icon="🚗", layout="wide")

st.markdown(
    "<h1 style='text-align: center; color: #6C63FF;'>🚗 Chasseur d'occasions</h1>"
    "<p style='text-align: center;'>Recherche multi-sites et detection des "
    "annonces <b>sous-cotees</b> a finition et options comparables.</p>",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Referentiels
# ---------------------------------------------------------------------------

CARBURANTS = ["Tous", "Essence", "Diesel", "Hybride", "Electrique", "GPL"]
BOITES = ["Toutes", "Manuelle", "Automatique"]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
}

ANNEE_MAX = time.localtime().tm_year


def slug(txt):
    """'Mercedes-Benz Classe A' -> 'mercedes-benz-classe-a' (slug URL)."""
    txt = txt.strip().lower()
    for a, b in [("é", "e"), ("è", "e"), ("ê", "e"), ("à", "a"), ("ç", "c"), ("ë", "e")]:
        txt = txt.replace(a, b)
    txt = re.sub(r"[^a-z0-9]+", "-", txt)
    return txt.strip("-")


def to_int(val):
    """Extrait un entier d'une valeur quelconque ('12 990 €' -> 12990)."""
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return int(val)
    digits = re.sub(r"[^\d]", "", str(val))
    return int(digits) if digits else None


# ---------------------------------------------------------------------------
# Construction des liens de recherche directs (tous sites)
# ---------------------------------------------------------------------------

def liens_recherche(c):
    """Retourne {nom_site: url} avec les criteres pre-remplis."""
    marque, modele = c["marque"], c["modele"]
    texte = " ".join(x for x in [marque, modele, c["finition"]] if x).strip()
    liens = {}

    # --- Leboncoin -----------------------------------------------------
    p = {"category": "2", "text": texte}
    if c["prix_min"] or c["prix_max"]:
        p["price"] = f"{c['prix_min'] or 'min'}-{c['prix_max'] or 'max'}"
    if c["annee_min"] or c["annee_max"]:
        p["regdate"] = f"{c['annee_min'] or 'min'}-{c['annee_max'] or 'max'}"
    if c["km_max"]:
        p["mileage"] = f"min-{c['km_max']}"
    liens["Leboncoin"] = "https://www.leboncoin.fr/recherche?" + urlencode(p)

    # --- La Centrale ---------------------------------------------------
    p = {}
    if marque:
        if modele:
            p["makesModelsCommercialNames"] = f"{marque.upper()}:{modele.upper()}"
        else:
            p["makesModelsCommercialNames"] = marque.upper()
    if c["annee_min"]:
        p["yearMin"] = c["annee_min"]
    if c["annee_max"]:
        p["yearMax"] = c["annee_max"]
    if c["km_max"]:
        p["mileageMax"] = c["km_max"]
    if c["prix_min"]:
        p["priceMin"] = c["prix_min"]
    if c["prix_max"]:
        p["priceMax"] = c["prix_max"]
    liens["La Centrale"] = "https://www.lacentrale.fr/listing?" + urlencode(p)

    # --- AutoScout24 ---------------------------------------------------
    liens["AutoScout24"] = url_autoscout24(c)

    # --- ParuVendu -----------------------------------------------------
    p = {"fulltext": texte}
    if c["prix_min"]:
        p["px0"] = c["prix_min"]
    if c["prix_max"]:
        p["px1"] = c["prix_max"]
    if c["km_max"]:
        p["km1"] = c["km_max"]
    if c["annee_min"]:
        p["an0"] = c["annee_min"]
    liens["ParuVendu"] = (
        "https://www.paruvendu.fr/voiture-occasion/listefo/default/default?"
        + urlencode(p)
    )

    # --- L'Argus ---------------------------------------------------------
    if marque and modele:
        liens["L'Argus occasion"] = (
            f"https://occasion.largus.fr/vehicules/{slug(marque)}/{slug(modele)}/"
        )
    elif marque:
        liens["L'Argus occasion"] = f"https://occasion.largus.fr/vehicules/{slug(marque)}/"

    # --- Aramisauto / Spoticar (recherche texte) -------------------------
    if marque:
        liens["Aramisauto"] = (
            f"https://www.aramisauto.com/achat/{slug(marque)}"
            + (f"/{slug(modele)}" if modele else "")
        )
    liens["Spoticar"] = (
        "https://www.spoticar.fr/voitures-occasion?search=" + quote_plus(texte)
    )
    liens["HeyCar"] = "https://heycar.com/fr/search?q=" + quote_plus(texte)
    return liens


def url_autoscout24(c):
    base = "https://www.autoscout24.fr/lst"
    if c["marque"]:
        base += "/" + slug(c["marque"])
        if c["modele"]:
            base += "/" + slug(c["modele"])
    p = {
        "atype": "C",
        "cy": "F",
        "damaged_listing": "exclude",
        "powertype": "kw",
        "sort": "price",
        "desc": "0",
        "ustate": "N,U",
        "size": "20",
    }
    if c["annee_min"]:
        p["fregfrom"] = c["annee_min"]
    if c["annee_max"]:
        p["fregto"] = c["annee_max"]
    if c["km_max"]:
        p["kmto"] = c["km_max"]
    if c["prix_min"]:
        p["pricefrom"] = c["prix_min"]
    if c["prix_max"]:
        p["priceto"] = c["prix_max"]
    fuel_map = {"Essence": "B", "Diesel": "D", "Hybride": "2,3", "Electrique": "E", "GPL": "L"}
    if c["carburant"] in fuel_map:
        p["fuel"] = fuel_map[c["carburant"]]
    if c["boite"] == "Manuelle":
        p["gear"] = "M"
    elif c["boite"] == "Automatique":
        p["gear"] = "A"
    if c["finition"]:
        p["version0"] = c["finition"]
    return base + "?" + urlencode(p)


# ---------------------------------------------------------------------------
# Scrapers (best effort : les sites changent et certains bloquent les robots)
# ---------------------------------------------------------------------------

def _walk_find_listings(node):
    """Cherche recursivement dans le JSON __NEXT_DATA__ une liste d'annonces."""
    if isinstance(node, dict):
        for key, val in node.items():
            if key == "listings" and isinstance(val, list) and val and isinstance(val[0], dict):
                return val
            found = _walk_find_listings(val)
            if found is not None:
                return found
    elif isinstance(node, list):
        for item in node:
            found = _walk_find_listings(item)
            if found is not None:
                return found
    return None


def _dig(d, *chemins):
    """Renvoie la premiere valeur non vide parmi plusieurs chemins 'a.b.c'."""
    for chemin in chemins:
        cur = d
        ok = True
        for part in chemin.split("."):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                ok = False
                break
        if ok and cur not in (None, "", []):
            return cur
    return None


def scrape_autoscout24(c, nb_pages=2):
    """AutoScout24 expose ses resultats dans le JSON __NEXT_DATA__ de la page."""
    annonces = []
    for page in range(1, nb_pages + 1):
        url = url_autoscout24(c) + f"&page={page}"
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")
        script = soup.find("script", id="__NEXT_DATA__")
        listings = None
        if script and script.string:
            try:
                listings = _walk_find_listings(json.loads(script.string))
            except json.JSONDecodeError:
                listings = None
        if not listings:
            break
        for it in listings:
            href = _dig(it, "url")
            annonces.append({
                "Site": "AutoScout24",
                "Titre": " ".join(
                    str(x) for x in [
                        _dig(it, "vehicle.make", "tracking.make"),
                        _dig(it, "vehicle.model", "tracking.model"),
                        _dig(it, "vehicle.modelVersionInput", "vehicle.modelVersion"),
                    ] if x
                ) or _dig(it, "title") or "Annonce",
                "Prix": to_int(_dig(
                    it, "tracking.price", "price.priceFormatted",
                    "prices.public.priceRaw", "price",
                )),
                "Annee": to_int(str(_dig(
                    it, "vehicle.firstRegistrationDateRaw",
                    "tracking.firstRegistration", "vehicle.firstRegistration",
                ) or "")[:4]),
                "Km": to_int(_dig(it, "tracking.mileage", "vehicle.mileageInKmRaw",
                                  "vehicle.mileageInKm")),
                "Carburant": _dig(it, "vehicle.fuelType", "tracking.fuelType"),
                "Boite": _dig(it, "vehicle.transmissionType", "tracking.gearType"),
                "Lieu": _dig(it, "location.city", "seller.city", "location.zip"),
                "Lien": ("https://www.autoscout24.fr" + href) if href and href.startswith("/") else href,
            })
        time.sleep(0.8)
    return annonces


def scrape_leboncoin(c, limite=35):
    """Tente l'API de recherche Leboncoin (souvent protegee par DataDome)."""
    texte = " ".join(x for x in [c["marque"], c["modele"], c["finition"]] if x).strip()
    ranges = {}
    if c["prix_min"] or c["prix_max"]:
        ranges["price"] = {k: v for k, v in
                           [("min", c["prix_min"]), ("max", c["prix_max"])] if v}
    if c["annee_min"] or c["annee_max"]:
        ranges["regdate"] = {k: v for k, v in
                             [("min", c["annee_min"]), ("max", c["annee_max"])] if v}
    if c["km_max"]:
        ranges["mileage"] = {"max": c["km_max"]}
    body = {
        "filters": {
            "category": {"id": "2"},
            "keywords": {"text": texte},
            "ranges": ranges,
        },
        "limit": limite,
        "sort_by": "price",
        "sort_order": "asc",
    }
    r = requests.post(
        "https://api.leboncoin.fr/finder/search",
        json=body,
        headers={**HEADERS, "Content-Type": "application/json",
                 "Origin": "https://www.leboncoin.fr",
                 "Referer": "https://www.leboncoin.fr/"},
        timeout=20,
    )
    if r.status_code != 200:
        raise RuntimeError(f"Acces refuse (HTTP {r.status_code}) - protection anti-robot probable")
    data = r.json()
    annonces = []
    for ad in data.get("ads", []):
        attrs = {a.get("key"): a.get("value") for a in ad.get("attributes", [])}
        prix = ad.get("price")
        if isinstance(prix, list):
            prix = prix[0] if prix else None
        annonces.append({
            "Site": "Leboncoin",
            "Titre": ad.get("subject", "Annonce"),
            "Prix": to_int(prix),
            "Annee": to_int(attrs.get("regdate")),
            "Km": to_int(attrs.get("mileage")),
            "Carburant": attrs.get("fuel"),
            "Boite": attrs.get("gearbox"),
            "Lieu": (ad.get("location") or {}).get("city"),
            "Lien": ad.get("url") or f"https://www.leboncoin.fr/ad/voitures/{ad.get('list_id')}",
        })
    return annonces


def scrape_paruvendu(c, nb_pages=1):
    """ParuVendu : parsing HTML best-effort."""
    texte = " ".join(x for x in [c["marque"], c["modele"], c["finition"]] if x).strip()
    p = {"fulltext": texte}
    if c["prix_min"]:
        p["px0"] = c["prix_min"]
    if c["prix_max"]:
        p["px1"] = c["prix_max"]
    if c["km_max"]:
        p["km1"] = c["km_max"]
    if c["annee_min"]:
        p["an0"] = c["annee_min"]
    url = ("https://www.paruvendu.fr/voiture-occasion/listefo/default/default?"
           + urlencode(p))
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")
    annonces, vus = [], set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/a/voiture-occasion/" not in href and "/voiture-occasion/annonce" not in href:
            continue
        if href.startswith("/"):
            href = "https://www.paruvendu.fr" + href
        if href in vus:
            continue
        vus.add(href)
        bloc = a
        for _ in range(3):
            if bloc.parent is not None:
                bloc = bloc.parent
        texte_bloc = " ".join(bloc.get_text(" ", strip=True).split())
        m_prix = re.search(r"(\d[\d\s .]{2,})\s*€", texte_bloc)
        m_km = re.search(r"(\d[\d\s .]{2,})\s*km", texte_bloc, re.I)
        m_an = re.search(r"\b(19[89]\d|20[0-4]\d)\b", texte_bloc)
        titre = a.get_text(" ", strip=True) or texte_bloc[:80]
        annonces.append({
            "Site": "ParuVendu",
            "Titre": titre[:90],
            "Prix": to_int(m_prix.group(1)) if m_prix else None,
            "Annee": to_int(m_an.group(1)) if m_an else None,
            "Km": to_int(m_km.group(1)) if m_km else None,
            "Carburant": None,
            "Boite": None,
            "Lieu": None,
            "Lien": href,
        })
    return [x for x in annonces if x["Prix"]]


SCRAPERS = {
    "AutoScout24": scrape_autoscout24,
    "Leboncoin": scrape_leboncoin,
    "ParuVendu": scrape_paruvendu,
}


# ---------------------------------------------------------------------------
# Analyse : detection des annonces sous-cotees
# ---------------------------------------------------------------------------

def analyser(df, seuil_pct):
    """Ajoute Prix estime / Ecart % / Verdict au DataFrame des annonces.

    Le prix 'normal' est estime par regression lineaire prix ~ km + age sur
    l'echantillon recupere (meme modele / finition), puis chaque annonce est
    comparee a cette estimation. En dessous de -seuil_pct %, elle est marquee
    'SOUS-COTEE'.
    """
    df = df.copy()
    df["Prix estime"] = np.nan
    df["Ecart %"] = np.nan
    df["Verdict"] = ""

    comp = df.dropna(subset=["Prix", "Km", "Annee"])
    comp = comp[(comp["Prix"] > 500) & (comp["Km"] < 500_000)]

    if len(comp) >= 5:
        age = ANNEE_MAX - comp["Annee"].astype(float)
        X = np.column_stack([
            np.ones(len(comp)),
            comp["Km"].astype(float) / 10_000.0,
            age,
        ])
        y = comp["Prix"].astype(float).values
        beta, *_ = np.linalg.lstsq(X, y, rcond=None)

        # Deux passes : on retire les points aberrants puis on re-estime
        pred = X @ beta
        resid = y - pred
        garde = np.abs(resid) <= 2.5 * (resid.std() or 1.0)
        if garde.sum() >= 5:
            beta, *_ = np.linalg.lstsq(X[garde], y[garde], rcond=None)

        idx = comp.index
        age_all = ANNEE_MAX - df.loc[idx, "Annee"].astype(float)
        X_all = np.column_stack([
            np.ones(len(idx)),
            df.loc[idx, "Km"].astype(float) / 10_000.0,
            age_all,
        ])
        est = X_all @ beta
        est = np.clip(est, 500, None)
        df.loc[idx, "Prix estime"] = est.round(0)
        ecart = (df.loc[idx, "Prix"] - est) / est * 100.0
        df.loc[idx, "Ecart %"] = ecart.round(1)
        df.loc[idx, "Verdict"] = np.where(
            ecart <= -seuil_pct, "💰 SOUS-COTEE",
            np.where(ecart >= seuil_pct, "⚠️ Chere", "Dans le marche"),
        )
        methode = f"regression sur {int(len(idx))} annonces comparables"
    elif len(comp) >= 2:
        mediane = comp["Prix"].median()
        idx = comp.index
        df.loc[idx, "Prix estime"] = mediane
        ecart = (df.loc[idx, "Prix"] - mediane) / mediane * 100.0
        df.loc[idx, "Ecart %"] = ecart.round(1)
        df.loc[idx, "Verdict"] = np.where(
            ecart <= -seuil_pct, "💰 SOUS-COTEE",
            np.where(ecart >= seuil_pct, "⚠️ Chere", "Dans le marche"),
        )
        methode = f"mediane simple sur {len(comp)} annonces (echantillon reduit)"
    else:
        methode = "echantillon insuffisant pour estimer la cote"
    return df, methode


def export_excel(df):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Annonces")
    buf.seek(0)
    return buf


# ---------------------------------------------------------------------------
# Interface
# ---------------------------------------------------------------------------

with st.sidebar:
    st.header("🔎 Criteres de recherche")
    AUTRE = "Autre (saisie libre)..."
    marque = st.selectbox("Marque", [""] + MARQUES, index=0,
                          help="Laisser vide pour chercher toutes marques")

    choix_modeles = modeles_de(marque)
    if choix_modeles:
        modele_sel = st.selectbox("Modele", [""] + choix_modeles + [AUTRE])
        modele = st.text_input("Modele (saisie libre)") if modele_sel == AUTRE \
            else modele_sel
    else:
        modele = st.text_input("Modele", placeholder="ex : Clio, 308, Golf ...")

    choix_finitions = finitions_de(marque, modele or None)
    if choix_finitions:
        finition_sel = st.selectbox(
            "Finition / version", [""] + choix_finitions + [AUTRE],
            help="Finitions usuelles de la marque + versions specifiques du modele",
        )
        finition = st.text_input("Finition (saisie libre)") \
            if finition_sel == AUTRE else finition_sel
    else:
        finition = st.text_input("Finition / version",
                                 placeholder="ex : Intens, GT Line, Allure ...")
    options_txt = st.text_input(
        "Options recherchees (mots-cles, separes par des virgules)",
        placeholder="ex : toit ouvrant, camera, CarPlay",
    )
    col1, col2 = st.columns(2)
    with col1:
        annee_min = st.number_input("Annee min", 1990, ANNEE_MAX, 2015)
        prix_min = st.number_input("Prix min (€)", 0, 500_000, 0, step=500)
    with col2:
        annee_max = st.number_input("Annee max", 1990, ANNEE_MAX, ANNEE_MAX)
        prix_max = st.number_input("Prix max (€)", 0, 500_000, 20_000, step=500)
    km_max = st.number_input("Kilometrage max", 0, 500_000, 120_000, step=5_000)
    carburant = st.selectbox("Carburant", CARBURANTS)
    boite = st.selectbox("Boite de vitesses", BOITES)

    st.divider()
    st.header("⚙️ Parametres")
    sites_actifs = st.multiselect(
        "Sites a interroger automatiquement",
        list(SCRAPERS.keys()),
        default=["AutoScout24"],
        help="Leboncoin et La Centrale bloquent souvent les robots : "
             "utilisez alors les liens directs generes plus bas.",
    )
    seuil = st.slider("Seuil 'sous-cotee' (%)", 5, 30, 10,
                      help="Une annonce est marquee sous-cotee si son prix est "
                           "inferieur d'au moins ce pourcentage au prix estime.")
    lancer = st.button("🚀 Lancer la recherche", type="primary", use_container_width=True)

criteres = {
    "marque": marque,
    "modele": modele.strip(),
    "finition": finition.strip(),
    "options": [o.strip().lower() for o in options_txt.split(",") if o.strip()],
    "annee_min": int(annee_min) if annee_min > 1990 else None,
    "annee_max": int(annee_max) if annee_max < ANNEE_MAX else None,
    "km_max": int(km_max) or None,
    "prix_min": int(prix_min) or None,
    "prix_max": int(prix_max) or None,
    "carburant": carburant if carburant != "Tous" else None,
    "boite": boite if boite != "Toutes" else None,
}

# --- Liens directs (toujours affiches) -------------------------------------
st.subheader("🔗 Liens de recherche directs")
st.caption(
    "Ces liens ouvrent chaque site avec vos criteres pre-remplis - utile pour "
    "les sites qui bloquent la recherche automatique (La Centrale, Leboncoin...)."
)
liens = liens_recherche(criteres)
cols = st.columns(4)
for i, (nom, url) in enumerate(liens.items()):
    with cols[i % 4]:
        st.link_button(nom, url, use_container_width=True)

st.divider()

# --- Recherche automatique ---------------------------------------------------
if lancer:
    if not (criteres["marque"] or criteres["modele"]):
        st.warning("Indiquez au moins une marque ou un modele.")
        st.stop()

    toutes = []
    erreurs = []
    barre = st.progress(0.0, text="Recherche en cours...")
    for i, site in enumerate(sites_actifs):
        barre.progress(i / max(len(sites_actifs), 1), text=f"Interrogation de {site}...")
        try:
            resultats = SCRAPERS[site](criteres)
            toutes.extend(resultats)
            st.toast(f"{site} : {len(resultats)} annonces", icon="✅")
        except Exception as exc:  # noqa: BLE001 - on veut continuer sur les autres sites
            erreurs.append((site, str(exc)))
    barre.progress(1.0, text="Termine")
    barre.empty()

    for site, msg in erreurs:
        st.warning(
            f"**{site}** n'a pas pu etre interroge automatiquement ({msg}). "
            f"Utilisez le lien direct ci-dessus."
        )

    if not toutes:
        st.error(
            "Aucune annonce recuperee automatiquement. Les sites bloquent "
            "peut-etre la recherche robot depuis ce serveur : ouvrez les liens "
            "directs ci-dessus, vos criteres y sont deja remplis."
        )
        st.stop()

    df = pd.DataFrame(toutes)

    # Filtre finition / options sur le titre
    if criteres["finition"]:
        masque = df["Titre"].str.contains(criteres["finition"], case=False, na=False)
        if masque.any():
            df = df[masque]
    for opt in criteres["options"]:
        masque = df["Titre"].str.contains(opt, case=False, na=False)
        if masque.any():
            df = df[masque]

    df = df.drop_duplicates(subset=["Lien"]).reset_index(drop=True)

    # Analyse sous-cote
    df, methode = analyser(df, seuil)
    df = df.sort_values(["Ecart %"], na_position="last").reset_index(drop=True)

    bonnes = df[df["Verdict"] == "💰 SOUS-COTEE"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Annonces trouvees", len(df))
    c2.metric("Sous-cotees", len(bonnes))
    prix_med = df["Prix"].median()
    c3.metric("Prix median", f"{prix_med:,.0f} €".replace(",", " ") if pd.notna(prix_med) else "-")
    km_med = df["Km"].median()
    c4.metric("Km median", f"{km_med:,.0f} km".replace(",", " ") if pd.notna(km_med) else "-")
    st.caption(f"Estimation de la cote : {methode}.")

    if len(bonnes):
        st.subheader("💰 Bonnes affaires detectees")
        st.dataframe(
            bonnes,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Lien": st.column_config.LinkColumn("Annonce", display_text="Voir ➜"),
                "Prix": st.column_config.NumberColumn(format="%d €"),
                "Prix estime": st.column_config.NumberColumn(format="%d €"),
                "Km": st.column_config.NumberColumn(format="%d km"),
                "Annee": st.column_config.NumberColumn(format="%d"),
            },
        )

    st.subheader("📋 Toutes les annonces")
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Lien": st.column_config.LinkColumn("Annonce", display_text="Voir ➜"),
            "Prix": st.column_config.NumberColumn(format="%d €"),
            "Prix estime": st.column_config.NumberColumn(format="%d €"),
            "Km": st.column_config.NumberColumn(format="%d km"),
            "Annee": st.column_config.NumberColumn(format="%d"),
        },
    )

    st.download_button(
        "📥 Exporter en Excel",
        data=export_excel(df),
        file_name="annonces_occasion.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    # Graphique prix vs km
    trace = df.dropna(subset=["Prix", "Km"])
    if len(trace) >= 3:
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(9, 4.5))
        normales = trace[trace["Verdict"] != "💰 SOUS-COTEE"]
        deals = trace[trace["Verdict"] == "💰 SOUS-COTEE"]
        ax.scatter(normales["Km"], normales["Prix"], alpha=0.6, label="Annonces")
        if len(deals):
            ax.scatter(deals["Km"], deals["Prix"], color="#2ca02c", s=90,
                       marker="*", label="Sous-cotees")
        est = trace.dropna(subset=["Prix estime"]).sort_values("Km")
        if len(est) >= 2:
            ax.plot(est["Km"], est["Prix estime"], "--", color="#6C63FF",
                    label="Prix estime")
        ax.set_xlabel("Kilometrage")
        ax.set_ylabel("Prix (€)")
        ax.legend()
        ax.grid(alpha=0.3)
        st.pyplot(fig)
else:
    st.info(
        "Renseignez vos criteres dans la barre laterale puis cliquez sur "
        "**Lancer la recherche**. Les annonces recuperees seront comparees "
        "entre elles pour reperer celles vendues **sous la cote** (meme "
        "modele, finition et options comparables)."
    )

st.divider()
st.caption(
    "⚠️ Outil d'aide a la recherche : verifiez toujours l'annonce sur le site "
    "d'origine (historique, entretien, controle technique). Certains sites "
    "limitent la consultation automatisee ; dans ce cas les liens directs "
    "pre-remplis restent disponibles."
)
