# pages/overview.py
import streamlit as st
import pandas as pd
import plotly.express as px
import requests

@st.cache_data
def load_meteorite_data():
    # Load meteorite data from NASA Socrata API (limit to 10000 records for speed)
    url = "https://data.nasa.gov/resource/y77d-th95.json?$limit=10000"
    df = pd.DataFrame(requests.get(url).json())
    # Clean and convert types
    df = df.dropna(subset=['year', 'mass', 'reclat', 'reclong'])
    df['year'] = pd.to_datetime(df['year']).dt.year
    df['mass'] = pd.to_numeric(df['mass'], errors='coerce')
    return df

def show_dataset_overview():
    st.title("📊 Dataset Overview")
    st.write("Summary statistics and visualizations of the meteorite dataset.")

    # Load data (cached)
    df = load_meteorite_data()

    # Display basic info
    st.subheader("Data Sample")
    st.write(df.head(5))
    st.write(f"Total meteorites: {len(df)}")

    # Mass distribution histogram
    st.subheader("Mass Distribution (g)")
    fig_mass = px.histogram(df, x="mass", nbins=50, labels={'mass':'Mass (g)'}, title="Meteorite Mass Histogram")
    st.plotly_chart(fig_mass, use_container_width=True)

    # Year of fall histogram
    st.subheader("Year of Fall")
    fig_year = px.histogram(df, x="year", nbins=50, labels={'year':'Year'}, title="Year of Fall Histogram")
    st.plotly_chart(fig_year, use_container_width=True)
