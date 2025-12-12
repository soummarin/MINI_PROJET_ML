import pandas as pd
import requests
from io import StringIO
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim
import time
import geopandas as gpd
from shapely.geometry import Point
import os

url = "https://raw.githubusercontent.com/Amina212004/MINI_PROJET_ML/data_branch/data/dataset.csv"
token = "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"  

headers = {"Authorization": f"token {token}"}
r = requests.get(url, headers=headers)
r.raise_for_status()  

df = pd.read_csv(StringIO(r.text))
df.head()
df["year"] = pd.to_numeric(df["year"], errors='coerce')  # NaN si invalide

# -----------------------------
# 3️⃣ Nettoyage de la masse et gestion des outliers
# -----------------------------
mass_median = df["mass (g)"].median()
df["mass_cleaned"] = df["mass (g)"].fillna(mass_median)
mass_threshold = df["mass_cleaned"].quantile(0.99)
df["mass_cleaned"] = np.where(df["mass_cleaned"] > mass_threshold, mass_threshold, df["mass_cleaned"])



# -----------------------------
# 5️ Bins pour la masse
# -----------------------------
bins_mass = [0, 1, 10, 100, 1000, 10000, mass_threshold]
labels_mass = ["<1g", "1-10g", "10-100g", "100-1kg", "1-10kg", f">10kg"]
df["mass_bin"] = pd.cut(df["mass_cleaned"], bins=bins_mass, labels=labels_mass)
df["mass_bin"] = df["mass_bin"].cat.add_categories("Unknown").fillna("Unknown")

# -----------------------------
# 6️ Bins pour l'année
# -----------------------------
def year_to_period(y):
    if pd.isna(y) or y <= 0 or y > 2025:
        return "Unknown"
    elif y < 1800:
        return "Ancient"
    elif y < 1900:
        return "19th Century"
    elif y < 2000:
        return "20th Century"
    else:
        return "21st Century"

df["year_period"] = df["year"].apply(year_to_period)

# -----------------------------
# 7️ Correction coordonnées invalides
# -----------------------------
df["reclat"] = pd.to_numeric(df["reclat"], errors="coerce")
df["reclong"] = pd.to_numeric(df["reclong"], errors="coerce")
df.loc[(df["reclat"] < -90) | (df["reclat"] > 90), "reclat"] = np.nan
df.loc[(df["reclong"] < -180) | (df["reclong"] > 180), "reclong"] = np.nan

# -----------------------------
# 8️ Récupération pays et continents
# -----------------------------
try:
    url_countries = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/110m_cultural/ne_110m_admin_0_countries.shp"
    world = gpd.read_file(url_countries)[["ADMIN", "CONTINENT", "geometry"]]
    
    df["geometry"] = df.apply(lambda r: Point(r["reclong"], r["reclat"]), axis=1)
    gdf = gpd.GeoDataFrame(df, geometry="geometry", crs=4326)
    
    result = gpd.sjoin(gdf, world, how="left", predicate="intersects")
    df["country"] = result["ADMIN"]
    df["continent"] = result["CONTINENT"]
    
except Exception as e:
    print(f"Erreur géographie: {e}")
    df["country"] = "Unknown"
    df["continent"] = "Unknown"

def latlon_to_continent(lat, lon):
    if pd.isna(lat) or pd.isna(lon):
        return "Unknown"
    if lat < -60:
        return "Antarctica"
    elif lat > 66.5:
        return "Europe"
    elif -60 <= lat <= 60:
        if lon < -30:
            return "North America" if lat >= 0 else "South America"
        elif lon < 60:
            return "Africa"
        else:
            return "Asia"
    return "Unknown"

df['continent'] = df.apply(
    lambda r: r['continent'] if pd.notna(r['continent']) else latlon_to_continent(r['reclat'], r['reclong']),
    axis=1
)
df['country'] = df['country'].fillna("Unknown")

# -----------------------------
# 9️ Nettoyage intelligent recclass
# -----------------------------
def clean_recclass(recclass):
    if pd.isna(recclass):
        return "UNKNOWN"
    rec = str(recclass).strip().upper()

    # -------------------------
    # GROUPE H (plus détaillé)
    # -------------------------
    for h in ["H3", "H4", "H5", "H6", "H7"]:
        if h in rec:
            return h
    if rec.startswith("H"):
        return "H-OTHER"

    # -------------------------
    # GROUPE L
    # -------------------------
    for l in ["L3", "L4", "L5", "L6"]:
        if l in rec:
            return l
    if rec.startswith("L") and not rec.startswith("LL"):
        return "L-OTHER"

    # -------------------------
    # GROUPE LL
    # -------------------------
    for ll in ["LL3", "LL4", "LL5", "LL6"]:
        if ll in rec:
            return ll
    if rec.startswith("LL"):
        return "LL-OTHER"

    # -------------------------
    # CHONDRITES CARBONÉES
    # -------------------------
    carbonaceous_prefixes = ["CI", "CM", "CK", "CV", "CO", "CR", "CB"]
    for prefix in carbonaceous_prefixes:
        if rec.startswith(prefix):
            return "CARBONACEOUS"

    # -------------------------
    # IRONS (métalliques)
    # -------------------------
    if "IRON" in rec or rec.startswith(("IAB", "II", "III", "IVA", "IVB")):
        return "IRON"

    # -------------------------
    # ACHONDRITES
    # -------------------------
    achondrites = ["ACHONDRITE", "EUCRITE", "HOWARDITE", "DIOGENITE", "AUBRITE", "UREILITE"]
    for a in achondrites:
        if a in rec:
            return "ACHONDRITE"

    # -------------------------
    # PALLASITE / MESOSIDERITE
    # -------------------------
    if "PALLASITE" in rec:
        return "PALLASITE"
    if "MESOSIDERITE" in rec:
        return "MESOSIDERITE"

    # -------------------------
    # CHONDRITE générique
    # -------------------------
    if "CHONDRITE" in rec or rec.endswith("ITE"):
        return "CHONDRITE"

    # -------------------------
    # Si vraiment inconnu
    # -------------------------
    return "OTHER"

df["recclass_clean"] = df["recclass"].apply(clean_recclass)


df_clean = df[
    (df["continent"] != "Unknown") &
    (df["country"] != "Unknown") &
    (df["year_period"] != "Unknown") &
    (df["recclass_clean"] != "UNKNOWN") &
    (df["mass_bin"] != "Unknown")
].copy()

# Regrouper catégories rares <500 occurrences
threshold = 500
counts = df_clean['recclass_clean'].value_counts()
rare_classes = counts[counts < threshold].index
df_clean['recclass_clean'] = df_clean['recclass_clean'].apply(lambda x: 'OTHER' if x in rare_classes else x)

# -----------------------------
# 1️⃣1️⃣ Dataset final pour règles
# -----------------------------
df_final = df_clean[[
    'name',
    'year_period',
    'year',
    'recclass',
    'continent',
    'country',
    'mass_cleaned',
    'mass_bin',
    'recclass_clean',
    'fall',
    'reclat',
    'reclong'
]].copy()

os.makedirs("data", exist_ok=True)  # crée le dossier si absent
df_final.to_csv("data/meteorites_final.csv", index=False)
