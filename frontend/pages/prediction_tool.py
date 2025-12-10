# pages/prediction_tool.py
import streamlit as st
import requests
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
from branca.element import Template, MacroElement

# A list of distinct colors for multiple predictions
COLOR_PALETTE = ["red", "blue", "green", "orange", "purple", "cyan", "magenta"]

def show_prediction_tool():
    st.title("🔎 Prediction Tool")
    st.write("Select filters in the sidebar and click **Predict** to see results.")

    # Initialize session state for predictions if not present
    if 'predictions' not in st.session_state:
        st.session_state['predictions'] = []   # Stores dicts: {"type", "prob", "locations", "color"}
        st.session_state['color_index'] = 0    # To pick next color

    # Sidebar inputs for filters
    with st.sidebar:
        st.header("Filters")
        # Year selection: range or single
        year_option = st.selectbox("Year Filter Mode", ["Range", "Single Year"])
        if year_option == "Range":
            year_range = st.slider("Select Year Range", 1900, 2022, (2000, 2020))
            year_payload = {"start": year_range[0], "end": year_range[1]}
        else:
            year_val = st.slider("Select Year", 1900, 2022, 2000)
            year_payload = {"start": year_val, "end": year_val}
        
        # Continent dropdown (include option for All)
        continents = ["All", "Africa", "Antarctica", "Asia", "Europe", "North America", "Oceania", "South America"]
        continent = st.selectbox("Continent", continents)
        
        # Mass range slider
        mass_range = st.slider("Mass Range (grams)", 0, 1000000, (0, 50000))
        mass_payload = {"min": mass_range[0], "max": mass_range[1]}

        # Predict and Clear buttons
        predict_clicked = st.button("Predict", type="primary")
        clear_clicked = st.button("Clear All", type="secondary")

    # Handle clearing predictions
    if clear_clicked:
        st.session_state['predictions'] = []
        st.session_state['color_index'] = 0
        st.success("Cleared all predictions.")

    # If Predict button is clicked, call the backend API
    if predict_clicked:
        # Prepare payload for backend
        payload = {
            "year": year_payload,
            "continent": continent,
            "mass": mass_payload
        }
        try:
            # Replace 'http://localhost:5000' with actual backend URL if deployed
            response = requests.post("http://localhost:5000/predict", json=payload)
            response.raise_for_status()
            result = response.json()
        except Exception as e:
            st.error(f"Error contacting prediction API: {e}")
            result = None

        if result:
            pred_type = result.get("predicted_type", "Unknown")
            confidence = result.get("probability", 0.0)
            locations = result.get("locations", [])

            # Assign a new color for this prediction
            color = COLOR_PALETTE[st.session_state['color_index'] % len(COLOR_PALETTE)]
            st.session_state['color_index'] += 1

            # Save this prediction to session state
            st.session_state['predictions'].append({
                "type": pred_type,
                "prob": confidence,
                "locations": locations,
                "color": color
            })

            st.success(f"Predicted type: **{pred_type}** (Confidence: {confidence:.2%})")
            st.write(f"Locations found: {len(locations)}")
    
    # Build the map with all predictions
    if st.session_state['predictions']:
        # Initialize Folium map centered at an average location
        m = folium.Map(location=[20, 0], zoom_start=2)
        # Add a marker cluster to group nearby points
        marker_cluster = MarkerCluster().add_to(m)

        # Add markers for each prediction in its color
        for pred in st.session_state['predictions']:
            color = pred["color"]
            for loc in pred["locations"]:
                lat, lon = loc.get("latitude"), loc.get("longitude")
                if lat is not None and lon is not None:
                    folium.CircleMarker(
                        location=[lat, lon],
                        radius=5,
                        color=color,
                        fill=True,
                        fill_color=color,
                        fill_opacity=0.7,
                        stroke=False,
                    ).add_to(marker_cluster)

        # Create HTML legend using branca Template
        legend_items = ""
        for pred in st.session_state['predictions']:
            legend_items += f"<li><span style='background:{pred['color']};opacity:0.75;'></span> {pred['type']}</li>"
        legend_html = f"""
        {{% macro html(this, kwargs) %}}
        <div class='maplegend' 
             style='position: fixed; z-index:9999; background:white; padding:10px; border:2px solid grey; border-radius:5px; top: 10px; right: 10px; font-size:12px;'>
          <div class='legend-title'><b>Predictions</b></div>
          <ul class='legend-labels'>{legend_items}</ul>
        </div>
        <style>
          .maplegend .legend-labels li {{ list-style: none; line-height: 18px; margin-bottom: 4px; }}
          .maplegend .legend-labels li span {{ display: inline-block; width: 18px; height: 18px; margin-right: 6px; }}
        </style>
        {{% endmacro %}}
        """
        legend = MacroElement()
        legend._template = Template(legend_html)
        m.get_root().add_child(legend)

        # Display the map
        st_folium(m, width=700, height=500)
