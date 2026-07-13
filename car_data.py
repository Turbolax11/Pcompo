# -*- coding: utf-8 -*-
"""
Base de donnees marques / modeles / finitions pour le marche francais de
l'occasion (vehicules ~2005-2025).

- MODELES_PAR_MARQUE : marque -> liste des modeles courants
- FINITIONS_PAR_MARQUE : marque -> finitions usuelles (les constructeurs
  utilisent en general les memes noms de finition sur toute la gamme)
- FINITIONS_PAR_MODELE : complements specifiques a certains modeles
  (versions sportives ou series speciales notables)

La saisie libre reste possible dans l'application pour tout ce qui ne figure
pas ici.
"""

MODELES_PAR_MARQUE = {
    "Abarth": ["500", "595", "695", "124 Spider"],
    "Alfa Romeo": ["Giulietta", "Giulia", "Stelvio", "Tonale", "MiTo", "159", "4C"],
    "Audi": ["A1", "A3", "A4", "A5", "A6", "A7", "A8", "Q2", "Q3", "Q5", "Q7",
             "Q8", "TT", "e-tron", "Q4 e-tron", "RS3", "S3"],
    "BMW": ["Serie 1", "Serie 2", "Serie 3", "Serie 4", "Serie 5", "Serie 7",
            "X1", "X2", "X3", "X4", "X5", "X6", "Z4", "i3", "i4", "iX1", "iX3", "M2", "M3", "M4"],
    "Citroen": ["C1", "C3", "C3 Aircross", "C4", "C4 Cactus", "C4 Picasso",
                "C5", "C5 Aircross", "C5 X", "Berlingo", "DS3", "DS4", "DS5",
                "Jumpy", "Spacetourer", "e-C4", "Ami"],
    "Cupra": ["Formentor", "Leon", "Ateca", "Born", "Tavascan"],
    "Dacia": ["Sandero", "Sandero Stepway", "Duster", "Logan", "Spring",
              "Jogger", "Lodgy", "Dokker", "Bigster"],
    "DS": ["DS3", "DS3 Crossback", "DS4", "DS5", "DS7 Crossback", "DS9"],
    "Fiat": ["500", "500X", "500L", "500e", "Panda", "Tipo", "Punto", "Doblo", "600"],
    "Ford": ["Fiesta", "Focus", "Puma", "Kuga", "EcoSport", "Mondeo", "Mustang",
             "Mustang Mach-E", "C-Max", "S-Max", "Galaxy", "Ranger", "Transit Custom"],
    "Honda": ["Jazz", "Civic", "CR-V", "HR-V", "e", "ZR-V"],
    "Hyundai": ["i10", "i20", "i30", "Kona", "Tucson", "Santa Fe", "Ioniq",
                "Ioniq 5", "Ioniq 6", "Bayon", "i40", "ix35"],
    "Jaguar": ["XE", "XF", "F-Pace", "E-Pace", "I-Pace", "F-Type"],
    "Jeep": ["Renegade", "Compass", "Cherokee", "Grand Cherokee", "Wrangler", "Avenger"],
    "Kia": ["Picanto", "Rio", "Ceed", "XCeed", "Stonic", "Niro", "Sportage",
            "Sorento", "EV6", "EV3", "Soul", "Venga"],
    "Land Rover": ["Range Rover Evoque", "Range Rover Velar", "Range Rover Sport",
                   "Range Rover", "Discovery", "Discovery Sport", "Defender", "Freelander"],
    "Lexus": ["CT", "IS", "ES", "NX", "RX", "UX", "LBX", "RZ"],
    "Mazda": ["Mazda2", "Mazda3", "Mazda6", "CX-3", "CX-30", "CX-5", "CX-60", "MX-5", "MX-30"],
    "Mercedes-Benz": ["Classe A", "Classe B", "Classe C", "Classe E", "Classe S",
                      "CLA", "CLS", "GLA", "GLB", "GLC", "GLE", "EQA", "EQB",
                      "EQC", "SLK", "SL", "Vito", "Classe V"],
    "MG": ["MG3", "MG4", "MG5", "ZS", "EHS", "Marvel R"],
    "Mini": ["Cooper 3 portes", "Cooper 5 portes", "Cabrio", "Clubman",
             "Countryman", "Electric", "Aceman"],
    "Mitsubishi": ["Space Star", "ASX", "Eclipse Cross", "Outlander", "L200"],
    "Nissan": ["Micra", "Juke", "Qashqai", "X-Trail", "Leaf", "Ariya", "Note",
               "Navara", "370Z", "GT-R"],
    "Opel": ["Corsa", "Astra", "Mokka", "Crossland", "Grandland", "Insignia",
             "Meriva", "Zafira", "Adam", "Karl", "Combo"],
    "Peugeot": ["108", "208", "2008", "308", "3008", "408", "508", "5008",
                "107", "207", "307", "407", "Rifter", "Partner", "Expert",
                "Traveller", "RCZ", "e-208", "e-2008"],
    "Porsche": ["911", "718 Cayman", "718 Boxster", "Macan", "Cayenne",
                "Panamera", "Taycan"],
    "Renault": ["Twingo", "Clio", "Captur", "Megane", "Megane E-Tech", "Scenic",
                "Kadjar", "Austral", "Arkana", "Koleos", "Talisman", "Espace",
                "Zoe", "Kangoo", "Trafic", "Laguna", "Rafale", "Symbioz"],
    "Seat": ["Ibiza", "Leon", "Arona", "Ateca", "Tarraco", "Alhambra", "Mii", "Toledo"],
    "Skoda": ["Fabia", "Octavia", "Superb", "Kamiq", "Karoq", "Kodiaq",
              "Scala", "Enyaq", "Citigo", "Yeti", "Rapid"],
    "Smart": ["Fortwo", "Forfour", "#1", "#3"],
    "Ssangyong": ["Tivoli", "Korando", "Rexton", "Musso"],
    "Subaru": ["Impreza", "XV", "Forester", "Outback", "BRZ", "Crosstrek"],
    "Suzuki": ["Swift", "Ignis", "Vitara", "S-Cross", "Jimny", "Baleno", "Celerio", "Swace"],
    "Tesla": ["Model 3", "Model Y", "Model S", "Model X"],
    "Toyota": ["Aygo", "Aygo X", "Yaris", "Yaris Cross", "Corolla", "C-HR",
               "RAV4", "Camry", "Prius", "Auris", "Avensis", "Land Cruiser",
               "Hilux", "Proace", "bZ4X", "GR86", "Supra"],
    "Volkswagen": ["Up!", "Polo", "Golf", "Golf Sportsvan", "T-Cross", "T-Roc",
                   "Tiguan", "Touran", "Passat", "Arteon", "Touareg", "Sharan",
                   "Scirocco", "Beetle", "ID.3", "ID.4", "ID.5", "ID. Buzz",
                   "Caddy", "Transporter", "California"],
    "Volvo": ["V40", "V60", "V90", "S60", "S90", "XC40", "XC60", "XC90",
              "C40", "EX30", "EX90"],
}

FINITIONS_PAR_MARQUE = {
    "Abarth": ["595", "Competizione", "Turismo", "Pista", "Esseesse"],
    "Alfa Romeo": ["Super", "Sprint", "Ti", "Veloce", "Competizione",
                   "Quadrifoglio", "Executive", "Lusso"],
    "Audi": ["Attraction", "Ambiente", "Ambition", "Ambition Luxe", "Business line",
             "Design", "Design Luxe", "Avus", "S line", "S Edition", "Competition"],
    "BMW": ["Lounge", "Business Design", "Sport", "Luxury", "M Sport", "xLine",
            "Edition M Sport", "Pack M"],
    "Citroen": ["Live", "Feel", "Feel Pack", "Shine", "Shine Pack", "C-Series",
                "Max", "You", "Plus", "Exclusive", "Confort", "Millenium"],
    "Cupra": ["V", "VZ", "VZ Cup", "Tribe Edition"],
    "Dacia": ["Access", "Essentiel", "Confort", "Prestige", "Expression",
              "Extreme", "Journey", "Laureate", "Ambiance", "SL Techroad", "15 ans"],
    "DS": ["Chic", "So Chic", "Sport Chic", "Performance Line",
           "Performance Line +", "Grand Chic", "Rivoli", "Opera", "Bastille",
           "Esprit de Voyage", "Etoile"],
    "Fiat": ["Pop", "Easy", "Lounge", "Sport", "Star", "Rockstar", "Dolcevita",
             "Cross", "City Cross", "Red", "La Prima"],
    "Ford": ["Trend", "Trend Business", "Titanium", "Titanium X", "ST-Line",
             "ST-Line X", "Vignale", "Active", "Cool & Connect", "ST", "RS"],
    "Honda": ["Comfort", "Elegance", "Executive", "Exclusive", "Sport", "Advance", "Type R"],
    "Hyundai": ["Initia", "Edition #1", "Intuitive", "Creative", "Executive",
                "N Line", "N Line Executive", "Shine", "Techno", "N"],
    "Jaguar": ["Pure", "Prestige", "Portfolio", "R-Sport", "R-Dynamic",
               "R-Dynamic S", "R-Dynamic SE", "HSE"],
    "Jeep": ["Sport", "Longitude", "Limited", "Altitude", "Trailhawk",
             "Overland", "Summit", "S", "80th Anniversary", "Upland"],
    "Kia": ["Motion", "Active", "Design", "Launch Edition", "GT Line",
            "GT Line Premium", "GT", "Premium", "Origins"],
    "Land Rover": ["S", "SE", "HSE", "R-Dynamic S", "R-Dynamic SE",
                   "R-Dynamic HSE", "Autobiography", "Dynamic SE", "X-Dynamic"],
    "Lexus": ["Pack", "Business", "Luxe", "Executive", "F Sport", "F Sport Design"],
    "Mazda": ["Dynamique", "Elegance", "Selection", "Exclusive-Line", "Homura",
              "Takumi", "Signature", "Sportline"],
    "Mercedes-Benz": ["Intuition", "Inspiration", "Sensation", "Business Line",
                      "Style Line", "Progressive Line", "AMG Line", "Fascination",
                      "Avantgarde", "Exclusive", "AMG"],
    "MG": ["Standard", "Comfort", "Luxury", "Trophy", "XPower"],
    "Mini": ["One", "Salt", "Essential", "Classic", "Cooper", "Cooper S",
             "Chili", "Yours", "Resolute", "John Cooper Works"],
    "Mitsubishi": ["Invite", "Intense", "Instyle", "Business", "Kaiteki"],
    "Nissan": ["Visia", "Acenta", "Business Edition", "N-Connecta", "N-Design",
               "N-Sport", "Tekna", "Tekna+", "Nismo"],
    "Opel": ["Edition", "Edition Business", "Elegance", "GS Line", "GS",
             "Ultimate", "Innovation", "Cosmo", "OPC"],
    "Peugeot": ["Access", "Active", "Active Pack", "Style", "Allure",
                "Allure Pack", "GT", "GT Line", "GT Pack", "Feline",
                "Roadtrip", "Crossway", "PSE (Peugeot Sport Engineered)", "GTi"],
    "Porsche": ["Base", "T", "S", "4S", "GTS", "Turbo", "Turbo S", "GT3", "GT4", "e-hybrid"],
    "Renault": ["Life", "Zen", "Business", "Limited", "Intens", "Edition One",
                "Iconic", "GT", "GT Line", "RS Line", "Esprit Alpine",
                "Initiale Paris", "Techno", "Evolution", "Equilibre", "RS", "Alpine"],
    "Seat": ["Reference", "Style", "Style Business", "Urban", "Xcellence",
             "FR", "FR Sport", "Cupra"],
    "Skoda": ["Active", "Ambition", "Business", "Style", "Sportline", "Scout",
              "Laurin & Klement", "Monte-Carlo", "RS"],
    "Smart": ["Pure", "Passion", "Prime", "Pulse", "Brabus", "Pro", "Premium"],
    "Ssangyong": ["Crystal", "Quartz", "Sapphire", "Limited"],
    "Subaru": ["Base", "Luxury", "Premium", "Executive", "Sport"],
    "Suzuki": ["Avantage", "Privilege", "Pack", "Style", "Allgrip"],
    "Tesla": ["Standard", "Standard Plus", "Grande Autonomie", "Performance", "Plaid"],
    "Toyota": ["Active", "Dynamic", "Dynamic Business", "Design", "Collection",
               "Lounge", "GR Sport", "GR", "Trail", "Excel", "Distinctive"],
    "Volkswagen": ["Trendline", "Confortline", "Confortline Business", "Carat",
                   "Carat Exclusive", "Highline", "Life", "Life Plus", "Style",
                   "Active", "R-Line", "Match", "United", "Lounge", "GTI",
                   "GTD", "GTE", "R"],
    "Volvo": ["Kinetic", "Momentum", "Momentum Business", "Inscription",
              "Inscription Luxe", "R-Design", "Core", "Plus", "Ultimate",
              "Polestar Engineered"],
}

# Complements specifiques a certains modeles (versions notables recherchees
# en occasion) : ils s'ajoutent aux finitions de la marque dans l'interface.
FINITIONS_PAR_MODELE = {
    ("Renault", "Clio"): ["RS", "RS Trophy", "Initiale Paris"],
    ("Renault", "Megane"): ["RS", "RS Trophy", "GT 220"],
    ("Renault", "Twingo"): ["RS", "GT"],
    ("Peugeot", "208"): ["GTi", "GTi by Peugeot Sport"],
    ("Peugeot", "308"): ["GTi", "GT 205"],
    ("Peugeot", "508"): ["PSE (Peugeot Sport Engineered)"],
    ("Volkswagen", "Polo"): ["GTI"],
    ("Volkswagen", "Golf"): ["GTI", "GTI Performance", "GTI Clubsport", "GTD", "GTE", "R"],
    ("Volkswagen", "Up!"): ["GTI"],
    ("Ford", "Fiesta"): ["ST", "ST-200"],
    ("Ford", "Focus"): ["ST", "RS"],
    ("Ford", "Puma"): ["ST"],
    ("Seat", "Ibiza"): ["Cupra"],
    ("Seat", "Leon"): ["Cupra", "Cupra R"],
    ("Skoda", "Octavia"): ["RS"],
    ("Skoda", "Fabia"): ["Monte-Carlo"],
    ("Mini", "Cooper 3 portes"): ["John Cooper Works", "GP"],
    ("Toyota", "Yaris"): ["GR", "GRMN"],
    ("Toyota", "Corolla"): ["GR Sport"],
    ("Hyundai", "i30"): ["N", "N Performance"],
    ("Hyundai", "i20"): ["N"],
    ("Kia", "Ceed"): ["GT"],
    ("BMW", "Serie 1"): ["M135i", "M140i", "128ti"],
    ("BMW", "Serie 3"): ["M340i"],
    ("Mercedes-Benz", "Classe A"): ["A35 AMG", "A45 AMG", "A45 S AMG"],
    ("Audi", "A1"): ["S line Competition"],
    ("Audi", "A3"): ["S3", "RS3"],
    ("Honda", "Civic"): ["Type R"],
    ("Nissan", "Micra"): ["Nismo"],
    ("Fiat", "500"): ["Abarth"],
    ("Opel", "Corsa"): ["OPC", "GSi"],
    ("Alfa Romeo", "Giulia"): ["Quadrifoglio"],
    ("Alfa Romeo", "Stelvio"): ["Quadrifoglio"],
    ("Dacia", "Duster"): ["Extreme", "Journey", "Mat Edition"],
}

MARQUES = sorted(MODELES_PAR_MARQUE.keys())


def modeles(marque):
    """Modeles connus pour une marque (liste vide si marque inconnue)."""
    return MODELES_PAR_MARQUE.get(marque, [])


def finitions(marque, modele=None):
    """Finitions proposees pour une marque (+ complements du modele)."""
    base = list(FINITIONS_PAR_MARQUE.get(marque, []))
    if modele:
        for extra in FINITIONS_PAR_MODELE.get((marque, modele), []):
            if extra not in base:
                base.append(extra)
    return base
