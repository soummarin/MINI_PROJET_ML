# pages/prediction_tool.py
import streamlit as st
import requests
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random
from datetime import datetime
import json
import numpy as np
import io

# Enhanced color palette
COLOR_PALETTE = [
    "#FF6B6B", "#4ECDC4", "#FFD166", "#06D6A0", "#118AB2", 
    "#EF476F", "#073B4C", "#7209B7", "#F15BB5", "#00BBF9",
    "#00F5D4", "#9B5DE5", "#FEE440", "#00F5D4", "#FB5607",
    "#FF9E6D", "#A78BFA", "#34D399", "#60A5FA", "#F472B6",
    "#818CF8", "#FBBF24", "#10B981", "#8B5CF6", "#EC4899",
    "#14B8A6", "#F97316", "#6366F1", "#84CC16", "#06B6D4"
]

# Mass intervals mapping
MASS_INTERVALS = ["<1g", "1-10g", "10-100g", "100-1kg", "1-10kg", ">10kg"]

# Dictionnaire complet des coordonnées des pays
COUNTRY_COORDINATES = {
    "USA": [37.0902, -95.7129], "Russia": [61.5240, 105.3188], "China": [35.8617, 104.1954],
    "Canada": [56.1304, -106.3468], "Brazil": [-14.2350, -51.9253], "Australia": [-25.2744, 133.7751],
    "India": [20.5937, 78.9629], "Argentina": [-38.4161, -63.6167], "Kazakhstan": [48.0196, 66.9237],
    "Algeria": [28.0339, 1.6596], "DRC": [-4.0383, 21.7587], "Saudi Arabia": [23.8859, 45.0792],
    "Mexico": [23.6345, -102.5528], "Indonesia": [-0.7893, 113.9213], "France": [46.6034, 1.8883],
    "Germany": [51.1657, 10.4515], "United Kingdom": [55.3781, -3.4360], "Japan": [36.2048, 138.2529],
    "Italy": [41.8719, 12.5674], "South Africa": [-30.5595, 22.9375], "Spain": [40.4637, -3.7492],
    "Ukraine": [48.3794, 31.1656], "Poland": [51.9194, 19.1451], "Iran": [32.4279, 53.6880],
    "Thailand": [15.8700, 100.9925], "Egypt": [26.8206, 30.8025], "Vietnam": [14.0583, 108.2772],
    "Turkey": [38.9637, 35.2433], "Congo": [-4.2634, 15.2832], "South Korea": [35.9078, 127.7669],
    "Colombia": [4.5709, -74.2973], "Kenya": [-0.0236, 37.9062], "Iraq": [33.2232, 43.6793],
    "Chile": [-35.6751, -71.5430], "Netherlands": [52.1326, 5.2913], "Ghana": [7.9465, -1.0232],
    "Yemen": [15.5527, 48.5164], "Peru": [-9.1900, -75.0152], "Uzbekistan": [41.3775, 64.5853],
    "Malaysia": [4.2105, 101.9758], "Nepal": [28.3949, 84.1240], "Mozambique": [-18.6657, 35.5296],
    "Madagascar": [-18.7669, 46.8691], "Cameroon": [7.3697, 12.3547], "Ivory Coast": [7.5400, -5.5471],
    "North Korea": [40.3399, 127.5101], "Syria": [34.8021, 38.9968], "Angola": [-11.2027, 17.8739],
    "Sri Lanka": [7.8731, 80.7718], "Tunisia": [33.8869, 9.5375], "Niger": [17.6078, 8.0817],
    "Bolivia": [-16.2902, -63.5887], "Libya": [26.3351, 17.2283], "Kuwait": [29.3117, 47.4818],
    "Panama": [8.5379, -80.7821], "Uruguay": [-32.5228, -55.7658], "Croatia": [45.1000, 15.2000],
    "Mongolia": [46.8625, 103.8467], "Moldova": [47.4116, 28.3699], "Georgia": [42.3154, 43.3569],
    "Eritrea": [15.1794, 39.7823], "Bhutan": [27.5142, 90.4336], "Somalia": [5.1521, 46.1996],
    "Haiti": [18.9712, -72.2852], "Belize": [17.1899, -88.4976], "Djibouti": [11.8251, 42.5903],
    "Luxembourg": [49.8153, 6.1296], "Suriname": [3.9193, -56.0278], "Montenegro": [42.7087, 19.3744],
    "Cape Verde": [16.5388, -23.0418], "Maldives": [3.2028, 73.2207], "Malta": [35.9375, 14.3754],
    "Brunei": [4.5353, 114.7277], "Bahamas": [25.0343, -77.3963], "Iceland": [64.9631, -19.0208],
    "Vanuatu": [-15.3767, 166.9592], "Barbados": [13.1939, -59.5432], "Sao Tome and Principe": [0.1864, 6.6131],
    "Samoa": [-13.7590, -172.1046], "Comoros": [-11.6455, 43.3333], "Kiribati": [-3.3704, -168.7340],
    "Micronesia": [7.4256, 150.5508], "Tonga": [-21.1790, -175.1982], "Seychelles": [-4.6796, 55.4920],
    "Antarctica": [-75.2500, 0.0000], "Nigeria": [9.0820, 8.6753], "Pakistan": [30.3753, 69.3451],
    "Bangladesh": [23.6850, 90.3563], "Philippines": [12.8797, 121.7740], "Myanmar": [21.9162, 95.9560],
    "Ethiopia": [9.1450, 40.4897], "Tanzania": [-6.3690, 34.8888], "Sudan": [12.8628, 30.2176],
    "Uganda": [1.3733, 32.2903], "Morocco": [31.7917, -7.0926], "Afghanistan": [33.9391, 67.7100],
    "Iceland": [64.9631, -19.0208], "Finland": [61.9241, 25.7482], "Norway": [60.4720, 8.4689],
    "Sweden": [60.1282, 18.6435], "Denmark": [56.2639, 9.5018], "Austria": [47.5162, 14.5501],
    "Switzerland": [46.8182, 8.2275], "Portugal": [39.3999, -8.2245], "Greece": [39.0742, 21.8243],
    "Czech Republic": [49.8175, 15.4730], "Romania": [45.9432, 24.9668], "Hungary": [47.1625, 19.5033],
    "Bulgaria": [42.7339, 25.4858], "Serbia": [44.0165, 21.0059], "Slovakia": [48.6690, 19.6990],
    "Ireland": [53.1424, -7.6921], "New Zealand": [-40.9006, 174.8860], "Fiji": [-17.7134, 178.0650],
    "Papua New Guinea": [-6.3149, 143.9555], "Solomon Islands": [-9.6457, 160.1562],
    "Venezuela": [6.4238, -66.5897], "Ecuador": [-1.8312, -78.1834], "Paraguay": [-23.4425, -58.4438],
    "Guyana": [4.8604, -58.9302], "Costa Rica": [9.7489, -83.7534], "Honduras": [15.1990, -86.2419],
    "El Salvador": [13.7942, -88.8965], "Nicaragua": [12.8654, -85.2072], "Guatemala": [15.7835, -90.2308],
    "Cuba": [21.5218, -77.7812], "Dominican Republic": [18.7357, -70.1627], "Puerto Rico": [18.2208, -66.5901],
    "Jamaica": [18.1096, -77.2975], "Trinidad and Tobago": [10.6918, -61.2225], "Bahrain": [26.0667, 50.5577],
    "Qatar": [25.3548, 51.1839], "Oman": [21.5126, 55.9233], "United Arab Emirates": [23.4241, 53.8478],
    "Jordan": [30.5852, 36.2384], "Lebanon": [33.8547, 35.8623], "Israel": [31.0461, 34.8516],
    "Palestine": [31.9522, 35.2332], "Cyprus": [35.1264, 33.4299], "Armenia": [40.0691, 45.0382],
    "Azerbaijan": [40.1431, 47.5769], "Turkmenistan": [38.9697, 59.5563], "Tajikistan": [38.8610, 71.2761],
    "Kyrgyzstan": [41.2044, 74.7661], "Laos": [19.8563, 102.4955], "Cambodia": [12.5657, 104.9910],
    "Singapore": [1.3521, 103.8198], "Timor-Leste": [-8.8742, 125.7275], "Mauritania": [21.0079, -10.9408],
    "Mali": [17.5707, -3.9962], "Burkina Faso": [12.2383, -1.5616], "Niger": [17.6078, 8.0817],
    "Chad": [15.4542, 18.7322], "Sudan": [12.8628, 30.2176], "Eritrea": [15.1794, 39.7823],
    "Somaliland": [9.5000, 44.0000], "Western Sahara": [24.2155, -12.8858], "Namibia": [-22.9576, 18.4904],
    "Botswana": [-22.3285, 24.6849], "Zimbabwe": [-19.0154, 29.1549], "Zambia": [-13.1339, 27.8493],
    "Malawi": [-13.2543, 34.3015], "Lesotho": [-29.6099, 28.2336], "Eswatini": [-26.5225, 31.4659],
    "Rwanda": [-1.9403, 29.8739], "Burundi": [-3.3731, 29.9189], "Benin": [9.3077, 2.3158],
    "Togo": [8.6195, 0.8248], "Sierra Leone": [8.4606, -11.7799], "Liberia": [6.4281, -9.4295],
    "Guinea": [9.9456, -9.6966], "Guinea-Bissau": [11.8037, -15.1804], "Gambia": [13.4432, -15.3101],
    "Senegal": [14.4974, -14.4524], "Mauritius": [-20.3484, 57.5522], "Comoros": [-11.6455, 43.3333],
    "Seychelles": [-4.6796, 55.4920], "Madagascar": [-18.7669, 46.8691], "Malta": [35.9375, 14.3754],
    "Andorra": [42.5063, 1.5218], "Liechtenstein": [47.1660, 9.5554], "Monaco": [43.7384, 7.4246],
    "San Marino": [43.9424, 12.4578], "Vatican City": [41.9029, 12.4534], "Kosovo": [42.6026, 20.9030],
    "Montenegro": [42.7087, 19.3744], "Macedonia": [41.6086, 21.7453], "Albania": [41.1533, 20.1683],
    "Bosnia and Herzegovina": [43.9159, 17.6791], "Slovenia": [46.1512, 14.9955], "Estonia": [58.5953, 25.0136],
    "Latvia": [56.8796, 24.6032], "Lithuania": [55.1694, 23.8813], "Belarus": [53.7098, 27.9534]
}

def get_exact_country_coordinates(country_name):
    """Get exact coordinates with country name normalization"""
    if not country_name or str(country_name) in ["nan", "None", ""]:
        return random.uniform(-60, 60), random.uniform(-180, 180)
    
    # Normalisation des noms de pays
    country_str = str(country_name).strip().title()
    
    # Mapping des noms alternatifs
    country_mapping = {
        "United States": "USA", "Us": "USA", "Usa": "USA", "United States Of America": "USA",
        "United Kingdom": "United Kingdom", "Uk": "United Kingdom", "Great Britain": "United Kingdom",
        "Congo": "DRC", "Democratic Republic Of The Congo": "DRC", "Drc": "DRC", "Congo Drc": "DRC",
        "Ivory Coast": "Ivory Coast", "Cote D'ivoire": "Ivory Coast", "Côte D'ivoire": "Ivory Coast",
        "South Korea": "South Korea", "Republic Of Korea": "South Korea", "Korea, South": "South Korea",
        "North Korea": "North Korea", "Democratic People's Republic Of Korea": "North Korea", "Korea, North": "North Korea",
        "Uae": "United Arab Emirates", "United Arab Emirates": "United Arab Emirates",
        "U.A.E.": "United Arab Emirates", "Emirates": "United Arab Emirates",
        "Myanmar": "Myanmar", "Burma": "Myanmar",
        "Czech Republic": "Czech Republic", "Czechia": "Czech Republic",
        "Macedonia": "Macedonia", "North Macedonia": "Macedonia",
        "Timor-Leste": "Timor-Leste", "East Timor": "Timor-Leste",
        "Eswatini": "Eswatini", "Swaziland": "Eswatini",
        "Cote D Ivoire": "Ivory Coast", "Côte D Ivoire": "Ivory Coast",
        "Palestine": "Palestine", "Palestinian Territories": "Palestine",
        "Taiwan": "China", "Hong Kong": "China", "Macau": "China"
    }
    
    # Appliquer le mapping
    if country_str in country_mapping:
        country_str = country_mapping[country_str]
    
    # Chercher le pays exact
    if country_str in COUNTRY_COORDINATES:
        lat, lon = COUNTRY_COORDINATES[country_str]
        # Petit offset aléatoire pour éviter la superposition exacte
        offset_lat = random.uniform(-0.1, 0.1)
        offset_lon = random.uniform(-0.1, 0.1)
        return lat + offset_lat, lon + offset_lon
    
    # Chercher par similarité
    for known_country, coords in COUNTRY_COORDINATES.items():
        if known_country.lower() in country_str.lower() or country_str.lower() in known_country.lower():
            lat, lon = coords
            offset_lat = random.uniform(-0.1, 0.1)
            offset_lon = random.uniform(-0.1, 0.1)
            return lat + offset_lat, lon + offset_lon
    
    # Fallback: retour au centre du continent le plus probable
    continent_centers = {
        "Africa": [8.7832, 34.5085],
        "Asia": [34.0479, 100.6197],
        "Europe": [54.5260, 15.2551],
        "North America": [54.5260, -105.2551],
        "South America": [-8.7832, -55.4915],
        "Oceania": [-25.2744, 133.7751],
        "Antarctica": [-75.2500, 0.0000]
    }
    
    return random.uniform(-60, 60), random.uniform(-180, 180)

def get_country_color(country_name):
    """Assign a consistent color to each country"""
    if not country_name or str(country_name).strip().lower() in ["", "nan", "none", "unknown"]:
        return "#CCCCCC"  # Gris pour pays inconnus
    
    country_str = str(country_name).strip()
    
    # Initialiser le dictionnaire des couleurs par pays si nécessaire
    if 'country_colors' not in st.session_state:
        st.session_state.country_colors = {}
    
    # Si le pays n'a pas encore de couleur, lui en assigner une
    if country_str not in st.session_state.country_colors:
        # Calculer un index basé sur le nom du pays pour une couleur cohérente
        hash_value = sum(ord(c) for c in country_str)
        color_index = hash_value % len(COLOR_PALETTE)
        st.session_state.country_colors[country_str] = COLOR_PALETTE[color_index]
    
    return st.session_state.country_colors[country_str]

def convert_mass_to_interval(mass_grams):
    """Convertir une masse en grammes vers une catégorie d'intervalle"""
    try:
        mass = float(mass_grams)
        
        if mass < 1:
            return "<1g", "Très petit (<1g)"
        elif 1 <= mass < 10:
            return "1-10g", "Petit (1-10g)"
        elif 10 <= mass < 100:
            return "10-100g", "Moyen (10-100g)"
        elif 100 <= mass < 1000:
            return "100-1kg", "Grand (100g-1kg)"
        elif 1000 <= mass < 10000:
            return "1-10kg", "Très grand (1-10kg)"
        else:
            return ">10kg", "Extra large (>10kg)"
    except:
        return None, "Invalide"

def show_prediction_tool():
    st.title("🎯 Advanced Meteorite Prediction Tool")
    
    # Introduction with cards
    col_intro1, col_intro2, col_intro3 = st.columns(3)
    with col_intro1:
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 15px; border: 1px solid rgba(255, 255, 255, 0.1);">
            <div style="font-size: 14px; color: #b0b0b0;">💡 Smart Prediction</div>
            <div style="font-size: 16px; color: #667eea;">Leave fields empty for AI prediction</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_intro2:
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 15px; border: 1px solid rgba(255, 255, 255, 0.1);">
            <div style="font-size: 14px; color: #b0b0b0;">🌍 Global Coverage</div>
            <div style="font-size: 16px; color: #764ba2;">200+ countries database</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_intro3:
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 15px; border: 1px solid rgba(255, 255, 255, 0.1);">
            <div style="font-size: 14px; color: #b0b0b0;">🎯 High Accuracy</div>
            <div style="font-size: 16px; color: #06D6A0;">Machine learning powered</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'predictions' not in st.session_state:
        st.session_state.predictions = []
    if 'max_results' not in st.session_state:
        st.session_state.max_results = 20  # Augmenté à 20 pour afficher plus de résultats
    if 'country_colors' not in st.session_state:
        st.session_state.country_colors = {}
    
    # Create main layout
    col_left, col_right = st.columns([3, 2])
    
    with col_left:
        st.markdown("### 📅 Year Selection")
        
        year_option = st.radio("**Year Input Mode:**", 
                              ["🎯 Provide specific year", 
                               "📅 Provide year range", 
                               "🤖 Let AI predict year (leave empty)"], 
                              horizontal=True)
        
        if year_option == "🎯 Provide specific year":
            year_val = st.slider("Select year:", 920, 2012, 2000, 1,
                               help="Select a specific year for prediction")
            if year_val > 2012 or year_val < 920:
                st.warning("⚠️ Year outside typical meteorite discovery range")
            year_payload = [int(year_val)]
            year_display = str(year_val)
            year_provided = True
            
        elif year_option == "📅 Provide year range":
            col_year1, col_year2 = st.columns(2)
            with col_year1:
                start_year = st.number_input("Start Year", 920, 2012, 1990, 1)
            with col_year2:
                end_year = st.number_input("End Year", 920, 2012, 2010, 1)
            
            if start_year > end_year:
                st.error("Start year must be before end year!")
                year_payload = None
                year_display = "Invalid range"
                year_provided = False
            else:
                year_payload = [[int(start_year), int(end_year)]]
                year_display = f"{start_year}-{end_year}"
                year_provided = True
        else:  # AI predict - LAISSER VIDE
            year_payload = None
            year_display = "AI Predicted"
            year_provided = False
           
        
        st.markdown("### 🌍 Continent Selection")
        continents = ["", "Africa", "Antarctica", "Asia", "Europe", 
                     "North America", "Oceania", "South America"]
        continent = st.selectbox("Select continent:", continents,
                               help="Select a continent or leave empty for AI prediction")
        continent_payload = [continent] if continent else []
        continent_display = continent if continent else "AI Predicted"
        continent_provided = bool(continent)
        
        st.markdown("### ⚖️ Mass Input")
        
        # MODIFICATION 1 & 4: Masse peut être vide (None) OU une valeur numérique
        mass_input_option = st.radio("**Mass Input Mode:**", 
                                    ["⚖️ Enter exact mass in grams", 
                                     "🤖 Let AI predict mass (leave empty)"], 
                                    horizontal=True)
        
        if mass_input_option == "⚖️ Enter exact mass in grams":
            # MODIFICATION 4: Retirer la limite max
            mass_input = st.number_input(
                "Enter meteorite mass (grams):", 
                min_value=0.0, 
                value=100.0,
                step=0.1,
                help="Enter the exact mass in grams. The system will automatically determine the appropriate category."
            )
            
            if mass_input > 0:
                # MODIFICATION 1: Convertir automatiquement la masse en intervalle
                mass_interval, mass_description = convert_mass_to_interval(mass_input)
                if mass_interval:
                    mass_payload = [mass_interval]
                    mass_display = f"{mass_input}g ({mass_description})"
                    
                    mass_provided = True
                else:
                    mass_payload = []
                    mass_display = "Invalid mass"
                    mass_provided = False
            else:
                mass_payload = []
                mass_display = "Not provided"
                mass_provided = False
                st.info("💡 **Enter a value > 0 to specify mass**")
        else:  # AI predict
            mass_payload = None
            mass_display = "AI Predicted"
            mass_provided = False
            
       
        
        # Advanced options expander
        with st.expander("⚙️ Advanced Options"):
            # MODIFICATION 3: Retirer le confidence threshold
            st.session_state.max_results = st.slider("Max results to display", 1, 50, 20, 1,
                                                    help="Maximum number of meteorite locations to display")
    
    with col_right:
        st.markdown("### 🎮 Controls")
        
        # Show what will be predicted
        st.markdown("### 🔮 What will be predicted?")
        
        predictions_needed = []
        if not mass_provided:
            predictions_needed.append("📊 **Mass interval**")
        if not year_provided:
            predictions_needed.append("📅 **Year**")
        if not continent_provided:
            predictions_needed.append("🌍 **Continent**")
        
        # Toujours prédire le type
        predictions_needed.append("🎯 **Meteorite Type**")
        
        if predictions_needed:
            st.markdown("#### AI will predict:")
            for item in predictions_needed:
                st.markdown(f"- {item}")
        
        # Prediction button with animation
        predict_clicked = st.button("🚀 **LAUNCH PREDICTION**", 
                                   type="primary",
                                   use_container_width=True,
                                   help="Click to analyze and predict meteorite type")
        
        # Clear button
        if st.button("🗑️ **CLEAR SESSION**", 
                    type="secondary", 
                    use_container_width=True):
            st.session_state.predictions = []
            st.session_state.country_colors = {}
            st.success("✅ Session cleared successfully!")
            st.rerun()
        
        # Quick stats
        if st.session_state.predictions:
            st.markdown("---")
            st.markdown("### 📈 Current Session")
            
            pred_count = len(st.session_state.predictions)
            last_pred = st.session_state.predictions[-1]
            
            st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 15px; border: 1px solid rgba(255, 255, 255, 0.1);">
                <div style="font-size: 12px; color: #b0b0b0;">Total Predictions</div>
                <div style="font-size: 28px; font-weight: bold; color: #667eea;">{pred_count}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 15px; border: 1px solid rgba(255, 255, 255, 0.1); margin-top: 10px;">
                <div style="font-size: 12px; color: #b0b0b0;">Last Prediction</div>
                <div style="font-size: 20px; font-weight: bold; color: #06D6A0;">{last_pred['type']}</div>
                <div style="font-size: 14px; color: #b0b0b0;">Confidence: {last_pred['prob']:.1%}</div>
            </div>
            """, unsafe_allow_html=True)

    # Handle prediction
    if predict_clicked:
        with st.spinner("🔍 Analyzing patterns..."):
            # Prepare payload - ENVOYER SEULEMENT CE QUI EST FOURNI
            payload = {
                "years": year_payload if year_provided else None,
                "mass": mass_payload if mass_provided else None,
                "continents": continent_payload if continent_provided else None
            }
            
           
            
            try:
                # Call backend
                response = requests.post("https://mini-projet-ml-backend1.onrender.com/predict",
                        json=payload, timeout=60)  # Augmenté à 60 secondes
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Extract data
                    pred_type = result.get("top_type", "Unknown")
                    confidence = result.get("probability", 0.0)
                    names = result.get("names", [])
                    countries = result.get("countries", [])
                    
                    # MODIFICATION 2: Afficher TOUS les résultats disponibles
                    # Pas de limite, sauf si spécifié dans max_results
                    locations = []
                    max_results = min(st.session_state.max_results, len(countries)) if countries else st.session_state.max_results
                    
                    for i, country in enumerate(countries[:max_results]):
                        if country and str(country) not in ["nan", "None"]:
                            country_str = str(country).strip()
                            lat, lon = get_exact_country_coordinates(country_str)
                            
                            # Get meteorite name if available
                            meteorite_name = names[i] if i < len(names) else f"Meteorite-{i+1}"
                            
                            # Get color for this country
                            country_color = get_country_color(country_str)
                            
                            locations.append({
                                "name": meteorite_name,
                                "country": country_str,
                                "latitude": lat,
                                "longitude": lon,
                                "type": pred_type,
                                "confidence": confidence,
                                "color": country_color
                            })
                    
                    # Si pas assez de locations mais qu'on a des noms, créer plus de locations
                    if len(locations) < max_results and names:
                        # Utiliser les pays disponibles ou créer des localisations aléatoires
                        for i in range(len(locations), min(max_results, len(names))):
                            country_str = "Unknown"
                            if countries and i < len(countries):
                                country_str = str(countries[i]).strip()
                            
                            lat, lon = get_exact_country_coordinates(country_str)
                            meteorite_name = names[i] if i < len(names) else f"Meteorite-{i+1}"
                            country_color = get_country_color(country_str)
                            
                            locations.append({
                                "name": meteorite_name,
                                "country": country_str,
                                "latitude": lat,
                                "longitude": lon,
                                "type": pred_type,
                                "confidence": confidence,
                                "color": country_color
                            })
                    
                    # Save prediction
                    prediction_data = {
                        "type": pred_type,
                        "prob": confidence,
                        "locations": locations,
                        "input_years": year_display,
                        "input_mass": mass_display,
                        "input_continent": continent_display,
                        "predicted_years": result.get("predicted_years", "Not predicted"),
                        "predicted_mass": result.get("predicted_mass", ["Not predicted"]),
                        "predicted_continent": result.get("predicted_continent", ["Not predicted"]),
                        "countries": countries[:max_results] if countries else [],
                        "names": names[:max_results] if names else [],
                        "sample_years": result.get("sample_years", []),
                        "timestamp": datetime.now().strftime("%H:%M:%S"),
                        "id": len(st.session_state.predictions) + 1,
                        "provided_mass": mass_provided,
                        "provided_year": year_provided,
                        "provided_continent": continent_provided
                    }
                    
                    st.session_state.predictions.append(prediction_data)
                    
                    # Display success with animation
                    st.success(f"✅ **Prediction #{len(st.session_state.predictions)} Complete!**")
                    
                    # Show results in a nice grid
                    col_res1, col_res2, col_res3 = st.columns(3)
                    with col_res1:
                        st.markdown(f"""
                        <div style="background: rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 15px; border: 1px solid rgba(255, 255, 255, 0.1);">
                            <div style="font-size: 12px; color: #b0b0b0;">Predicted Type</div>
                            <div style="font-size: 24px; font-weight: bold; color: #4ECDC4;">{pred_type}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_res2:
                        st.markdown(f"""
                        <div style="background: rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 15px; border: 1px solid rgba(255, 255, 255, 0.1);">
                            <div style="font-size: 12px; color: #b0b0b0;">Confidence Score</div>
                            <div style="font-size: 24px; font-weight: bold; 
                                color: {'#06D6A0' if confidence > 0.7 else '#FFD166' if confidence > 0.5 else '#FF6B6B'}">
                                {confidence:.1%}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_res3:
                        st.markdown(f"""
                        <div style="background: rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 15px; border: 1px solid rgba(255, 255, 255, 0.1);">
                            <div style="font-size: 12px; color: #b0b0b0;">Locations Found</div>
                            <div style="font-size: 24px; font-weight: bold; color: #118AB2;">{len(countries) if countries else 0}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Show input summary
                    st.markdown("### 📋 Input Summary & AI Predictions")
                    summary_cols = st.columns(3)
                    
                    with summary_cols[0]:
                        if year_provided:
                            st.markdown(f"**Year:** {year_display}")
                        else:
                            predicted_year = result.get("predicted_years", "N/A")
                            st.markdown(f"**Year:** 🧠 **AI Predicted:** {predicted_year}")
                    
                    with summary_cols[1]:
                        if continent_provided:
                            st.markdown(f"**Continent:** {continent_display}")
                        else:
                            predicted_continent = result.get("predicted_continent", ["N/A"])
                            if isinstance(predicted_continent, list) and len(predicted_continent) > 0:
                                st.markdown(f"**Continent:** 🧠 **AI Predicted:** {predicted_continent[0]}")
                            else:
                                st.markdown(f"**Continent:** 🧠 **AI Predicted:** {predicted_continent}")
                    
                    with summary_cols[2]:
                        if mass_provided:
                            st.markdown(f"**Mass:** {mass_display}")
                        else:
                            predicted_mass = result.get("predicted_mass", ["N/A"])
                            if isinstance(predicted_mass, list) and len(predicted_mass) > 0:
                                st.markdown(f"**Mass:** 🧠 **AI Predicted:** {predicted_mass[0]}")
                            else:
                                st.markdown(f"**Mass:** 🧠 **AI Predicted:** {predicted_mass}")
                    
                    # Show AI predictions in a nice way
                    if not year_provided or not continent_provided or not mass_provided:
                        st.markdown("### 🤖 AI Predictions Summary")
                        
                        ai_predictions = []
                        if not year_provided and "predicted_years" in result:
                            ai_predictions.append(f"📅 **Year:** {result['predicted_years']}")
                        if not continent_provided and "predicted_continent" in result:
                            pred_cont = result['predicted_continent']
                            if isinstance(pred_cont, list) and len(pred_cont) > 0:
                                ai_predictions.append(f"🌍 **Continent:** {pred_cont[0]}")
                            else:
                                ai_predictions.append(f"🌍 **Continent:** {pred_cont}")
                        if not mass_provided and "predicted_mass" in result:
                            pred_mass = result['predicted_mass']
                            if isinstance(pred_mass, list) and len(pred_mass) > 0:
                                ai_predictions.append(f"⚖️ **Mass interval:** {pred_mass[0]}")
                            else:
                                ai_predictions.append(f"⚖️ **Mass interval:** {pred_mass}")
                        
                        if ai_predictions:
                            for pred in ai_predictions:
                                st.markdown(f"- {pred}")
                    
                    # Show sample meteorites
                    if names:
                        st.markdown(f"### 📄 Sample Meteorites Found ({len(names)} total)")
                        # Afficher plus de noms
                        sample_names = names[:10]  # Augmenté à 10 noms
                        for i, name in enumerate(sample_names):
                            st.markdown(f"{i+1}. {name}")
                        if len(names) > 10:
                            st.markdown(f"... and {len(names) - 10} more")
                    
                    # Afficher les pays
                    if countries:
                        st.markdown(f"### 🌍 Countries with Similar Meteorites ({len(countries)} countries)")
                        unique_countries = list(set(countries))
                        for i, country in enumerate(unique_countries[:10]):
                            st.markdown(f"📍 {country}")
                        if len(unique_countries) > 10:
                            st.markdown(f"... and {len(unique_countries) - 10} more countries")
                    
                else:
                    st.error(f"❌ Backend error: {response.status_code}")
                    try:
                        st.json(response.json())
                    except:
                        st.write(f"Response: {response.text}")
                    
            except requests.exceptions.ConnectionError:
                st.error("""
                ❌ **Cannot connect to backend server!**
                
                **Troubleshooting steps:**
                1. Make sure the backend is running: `python backend/app.py`
                2. Check if port 5001 is available
                3. Verify the server is running at https://mini-projet-mlbackend.onrender.com
                """)
            except Exception as e:
                st.error(f"❌ **Error:** {str(e)}")

    # Display results if we have predictions
    if st.session_state.predictions:
        st.markdown("---")
        st.markdown("## 🌍 **Interactive Visualization**")
        
        # Create tabs for different views
        map_tab, plotly_tab, data_tab, analysis_tab = st.tabs([
            "🗺️ Folium Map", 
            "📊 Plotly Map", 
            "📋 Data Table",
            "📈 Analysis"
        ])
        
        with map_tab:
            # Get the latest prediction
            latest_pred = st.session_state.predictions[-1]
            
            # Create Folium map with dark theme
            m = folium.Map(location=[20, 0], 
                          zoom_start=2, 
                          tiles='CartoDB dark_matter',
                          control_scale=True)
            
            # Add marker cluster
            marker_cluster = MarkerCluster(name="Meteorite Clusters")
            
            # Add markers for latest prediction
            for loc_idx, loc in enumerate(latest_pred["locations"]):
                lat, lon = loc.get("latitude"), loc.get("longitude")
                
                if lat is not None and lon is not None:
                    # Create custom HTML popup
                    popup_html = f"""
                    <div style="font-family: Arial; min-width: 250px;">
                        <div style="background: {loc['color']}; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                            <h4 style="color: white; margin: 0;">{loc.get('name', 'Meteorite')}</h4>
                        </div>
                        <p><strong>📍 Country:</strong> {loc.get('country', 'Unknown')}</p>
                        <p><strong>🎯 Type:</strong> {latest_pred['type']}</p>
                        <p><strong>📊 Confidence:</strong> {latest_pred['prob']:.1%}</p>
                        <hr>
                        <p style="font-size: 10px; color: #666;">Lat: {lat:.4f}, Lon: {lon:.4f}</p>
                    </div>
                    """
                    
                    # Create marker with custom icon
                    marker = folium.Marker(
                        location=[lat, lon],
                        popup=folium.Popup(popup_html, max_width=300),
                        tooltip=f"{loc.get('name')} - {latest_pred['type']} - {loc.get('country')}",
                        icon=folium.Icon(color='white', icon_color=loc['color'], 
                                       icon='circle', prefix='fa')
                    )
                    
                    marker.add_to(marker_cluster)
            
            # Add cluster to map
            marker_cluster.add_to(m)
            
            # Add layer control
            folium.LayerControl().add_to(m)
            
            # Display the map
            st_folium(m, width=900, height=500, returned_objects=[])
        
        with plotly_tab:
            # Prepare data for Plotly (latest prediction only)
            plotly_data = []
            latest_pred = st.session_state.predictions[-1]
            
            for loc in latest_pred["locations"]:
                plotly_data.append({
                    "Type": latest_pred["type"],
                    "Confidence": latest_pred["prob"],
                    "Country": loc.get("country", "Unknown"),
                    "Latitude": loc.get("latitude"),
                    "Longitude": loc.get("longitude"),
                    "Color": loc.get("color", "#CCCCCC"),
                    "Name": loc.get("name", "Unknown")
                })
            
            if plotly_data:
                df_plotly = pd.DataFrame(plotly_data)
                
                # Créer un graphique avec couleur par pays
                fig = go.Figure()
                
                # Grouper par pays pour avoir une couleur unique par pays
                countries = df_plotly['Country'].unique()
                for country in countries:
                    df_country = df_plotly[df_plotly['Country'] == country]
                    color = df_country.iloc[0]['Color']
                    
                    fig.add_trace(go.Scattergeo(
                        lon = df_country['Longitude'],
                        lat = df_country['Latitude'],
                        text = df_country['Country'] + '<br>Type: ' + df_country['Type'] + 
                               '<br>Confidence: ' + (df_country['Confidence'] * 100).round(1).astype(str) + '%',
                        mode = 'markers',
                        marker = dict(
                            size = 15,
                            color = color,
                            line = dict(width=1, color='white'),
                            opacity = 0.8
                        ),
                        name = country,
                        hoverinfo = 'text'
                    ))
                
                fig.update_layout(
                    title = f'🌍 Latest Prediction: {latest_pred["type"]} (Confidence: {latest_pred["prob"]:.1%})',
                    geo = dict(
                        showland = True,
                        landcolor = "rgb(40, 40, 40)",
                        subunitcolor = "rgb(100, 100, 100)",
                        countrycolor = "rgb(80, 80, 80)",
                        showlakes = True,
                        lakecolor = "rgb(30, 30, 30)",
                        showsubunits = True,
                        showcountries = True,
                        resolution = 50,
                        projection = dict(type="natural earth")
                    ),
                    height = 600,
                    template = "plotly_dark",
                    showlegend = True,
                    legend = dict(
                        title = "Countries",
                        font = dict(size=10),
                        yanchor = "top",
                        y = 0.99,
                        xanchor = "left",
                        x = 0.01
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        with data_tab:
            # Show detailed data for all predictions
            for pred_idx, pred in enumerate(st.session_state.predictions):
                with st.expander(f"Prediction #{pred_idx + 1} - {pred['type']} (Confidence: {pred['prob']:.1%})"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"**Type:** {pred['type']}")
                        st.markdown(f"**Confidence:** {pred['prob']:.1%}")
                        st.markdown(f"**Timestamp:** {pred['timestamp']}")
                    
                    with col2:
                        st.markdown(f"**Year:** {pred['input_years']}")
                        if pred['predicted_years'] != "Not predicted":
                            st.markdown(f"**AI Predicted Year:** {pred['predicted_years']}")
                    
                    with col3:
                        st.markdown(f"**Continent:** {pred['input_continent']}")
                        if isinstance(pred['predicted_continent'], list) and pred['predicted_continent'][0] != "Not predicted":
                            st.markdown(f"**AI Predicted Continent:** {pred['predicted_continent'][0]}")
                    
                    # Show mass info
                    st.markdown(f"**Mass:** {pred['input_mass']}")
                    if isinstance(pred['predicted_mass'], list) and pred['predicted_mass'][0] != "Not predicted":
                        st.markdown(f"**AI Predicted Mass Interval:** {pred['predicted_mass'][0]}")
                    
                    # Show locations table
                    if pred['locations']:
                        st.markdown("### 📍 Locations")
                        loc_data = []
                        for loc in pred['locations']:
                            loc_data.append({
                                "Name": loc['name'],
                                "Country": loc['country'],
                                "Latitude": f"{loc['latitude']:.4f}",
                                "Longitude": f"{loc['longitude']:.4f}"
                            })
                        st.dataframe(pd.DataFrame(loc_data), use_container_width=True)
                    
                    st.markdown("---")
            
            # Export options for all predictions
            st.markdown("### 📤 Export All Data")
            all_data = []
            for pred in st.session_state.predictions:
                for loc in pred['locations']:
                    all_data.append({
                        "Prediction ID": pred['id'],
                        "Type": pred['type'],
                        "Confidence": pred['prob'],
                        "Year Input": pred['input_years'],
                        "Continent Input": pred['input_continent'],
                        "Mass Input": pred['input_mass'],
                        "AI Predicted Year": pred['predicted_years'],
                        "AI Predicted Continent": pred['predicted_continent'][0] if isinstance(pred['predicted_continent'], list) and len(pred['predicted_continent']) > 0 else pred['predicted_continent'],
                        "AI Predicted Mass": pred['predicted_mass'][0] if isinstance(pred['predicted_mass'], list) and len(pred['predicted_mass']) > 0 else pred['predicted_mass'],
                        "Meteorite Name": loc['name'],
                        "Country": loc['country'],
                        "Latitude": loc['latitude'],
                        "Longitude": loc['longitude'],
                        "Timestamp": pred['timestamp']
                    })
            
            if all_data:
                df_all = pd.DataFrame(all_data)
                col_exp1, col_exp2, col_exp3 = st.columns(3)
                
                with col_exp1:
                    csv = df_all.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name="meteorite_predictions.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                with col_exp2:
                    json_data = json.dumps(all_data, indent=2)
                    st.download_button(
                        label="📥 Download JSON",
                        data=json_data,
                        file_name="meteorite_predictions.json",
                        mime="application/json",
                        use_container_width=True
                    )
                
                with col_exp3:
                    # For Excel export
                    import io
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df_all.to_excel(writer, index=False, sheet_name='Predictions')
                    excel_data = output.getvalue()
                    st.download_button(
                        label="📥 Download Excel",
                        data=excel_data,
                        file_name="meteorite_predictions.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
        
        with analysis_tab:
            # Analysis dashboard
            st.markdown("### 📊 Prediction Analysis")
            
            # Create analysis metrics
            total_predictions = len(st.session_state.predictions)
            total_locations = sum(len(p['locations']) for p in st.session_state.predictions)
            avg_confidence = sum(p['prob'] for p in st.session_state.predictions) / total_predictions if total_predictions > 0 else 0
            
            col_ana1, col_ana2, col_ana3 = st.columns(3)
            with col_ana1:
                st.metric("Total Predictions", total_predictions)
            with col_ana2:
                st.metric("Total Locations", total_locations)
            with col_ana3:
                st.metric("Avg Confidence", f"{avg_confidence:.1%}")
            
            # Confidence distribution
            conf_values = [p['prob'] for p in st.session_state.predictions]
            fig_conf = px.histogram(
                x=conf_values,
                nbins=10,
                labels={'x': 'Confidence', 'y': 'Count'},
                title="Confidence Distribution",
                color_discrete_sequence=['#667eea']
            )
            fig_conf.update_layout(template="plotly_dark")
            st.plotly_chart(fig_conf, use_container_width=True)
            
            # Type distribution
            type_counts = {}
            for pred in st.session_state.predictions:
                pred_type = pred['type']
                type_counts[pred_type] = type_counts.get(pred_type, 0) + 1
            
            if type_counts:
                types_df = pd.DataFrame(list(type_counts.items()), columns=['Type', 'Count'])
                fig_types = px.pie(types_df, values='Count', names='Type', 
                                 title="Predicted Type Distribution",
                                 color_discrete_sequence=COLOR_PALETTE[:len(type_counts)])
                fig_types.update_layout(template="plotly_dark")
                st.plotly_chart(fig_types, use_container_width=True)