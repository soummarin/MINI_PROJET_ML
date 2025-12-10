# app.py
import streamlit as st
from streamlit_option_menu import option_menu

# Import our page modules
from pages import home, prediction_tool, overview, ideas

# Configure the page
st.set_page_config(page_title="Meteorite Type Predictor", layout="wide")

# Sidebar navigation menu
with st.sidebar:
    selected = option_menu(
        menu_title=None,  # No menu title for a cleaner look
        options=["Home", "Prediction Tool", "Data Overview", "Ideas/Improvements"],
        icons=["house", "cursor-fill", "bar-chart-line", "lightbulb-fill"],
        menu_icon="cast",
        default_index=0,
    )

# Route to the selected page
if selected == "Home":
    home.show_home()
elif selected == "Prediction Tool":
    prediction_tool.show_prediction_tool()
elif selected == "Data Overview":
    overview.show_dataset_overview()
elif selected == "Ideas/Improvements":
    ideas.show_ideas()
