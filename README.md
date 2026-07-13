# Pcompo

Deux applications Streamlit :

## 1. Calculs Composites - Atelier (`app.py`)

Application de calculs pour materiaux composites.

```bash
streamlit run app.py
```

## 2. Chasseur d'occasions (`car_finder_app.py`) 🚗

Recherche de voitures d'occasion multi-sites avec detection des annonces
**sous-cotees**.

```bash
pip install -r requirements.txt
streamlit run car_finder_app.py
```

### Fonctionnement

1. **Criteres** : marque, modele, finition/version, options (mots-cles),
   annees, kilometrage, budget, carburant, boite.
2. **Recherche automatique** : l'app interroge les sites qui le permettent
   (AutoScout24 en priorite, Leboncoin et ParuVendu en best-effort) et
   rassemble les annonces dans un tableau unique : titre, prix, annee, km,
   lieu et **lien direct vers l'annonce**.
3. **Liens directs** : pour les sites qui bloquent les robots (La Centrale,
   Leboncoin selon les cas), l'app genere des liens de recherche avec vos
   criteres deja remplis (La Centrale, Leboncoin, AutoScout24, ParuVendu,
   L'Argus, Aramisauto, Spoticar, HeyCar).
4. **Detection des sous-cotes** : sur l'echantillon d'annonces comparables
   (meme modele/finition), l'app estime le prix "normal" par regression
   `prix ~ kilometrage + age` (avec elimination des points aberrants), puis
   marque `SOUS-COTEE` toute annonce dont le prix est inferieur au prix
   estime d'au moins X % (seuil reglable, 10 % par defaut).
5. **Export Excel** du tableau complet + graphique prix / kilometrage.

### Limites connues

- Leboncoin et La Centrale utilisent des protections anti-robot (DataDome) :
  la recherche automatique peut echouer, surtout depuis un serveur cloud.
  Dans ce cas l'app affiche un avertissement et les liens directs pre-remplis
  prennent le relais.
- La structure HTML des sites evolue : les scrapers sont ecrits de facon
  defensive mais peuvent necessiter des mises a jour.
- L'estimation de cote est calculee sur l'echantillon recupere : plus il y a
  d'annonces comparables, plus elle est fiable (regression a partir de 5
  annonces, mediane en dessous).
