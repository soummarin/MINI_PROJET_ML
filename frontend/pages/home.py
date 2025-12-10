# pages/home.py
import streamlit as st

def show_home():
    st.markdown("# 🌠 Meteorite Type Predictor")
    st.write("""
        Welcome to the **Meteorite Type Predictor** app! This tool allows you to select criteria
        (year, continent, and mass range) to predict the most likely meteorite type that fits those criteria.
        You can then view the locations of matching meteorite landings on an interactive map.

        **How to use this app:**
        - Go to the **Prediction Tool** page to select your filters.
        - Click the **Predict** button to get the top predicted meteorite type.
        - The map will display markers (color-coded) for all meteorites matching the prediction.
        - You can make multiple predictions; each will use a new color on the map and be added to the legend.
        - Use the **Clear All** button to reset and start over.

        Navigate between pages using the sidebar menu. Enjoy exploring meteorite data!
    """)
