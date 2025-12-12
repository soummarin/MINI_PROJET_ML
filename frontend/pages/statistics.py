# pages/statistics.py (VERSION CORRIGÉE)
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import numpy as np
import json
from datetime import datetime
import re
import io
import math

def parse_year(year_str):
    """Parse une année qui peut être un nombre, une chaîne, ou '20th Century'"""
    if year_str is None:
        return None
    
    # Si c'est déjà un nombre, s'assurer que c'est un int
    if isinstance(year_str, (int, float)):
        # S'assurer que c'est une année valide (entre 1800 et 2025)
        year_int = int(year_str)
        if 1800 <= year_int <= 2025:
            return year_int
        return None
    
    # Si c'est une chaîne
    if isinstance(year_str, str):
        # Enlever les espaces
        year_str = year_str.strip()
        
        # Si vide ou "AI Predicted"
        if year_str in ["", "AI Predicted", "N/A", "None", "Not predicted", "Not provided"]:
            return None
        
        # Si c'est une chaîne vide ou non significative
        if year_str.lower() in ["nan", "none", "null"]:
            return None
        
        # Essayer de convertir directement
        try:
            year_int = int(float(year_str))  # float d'abord au cas où il y a des décimales
            if 1800 <= year_int <= 2025:
                return year_int
        except ValueError:
            pass
        
        # Chercher un pattern d'année (4 chiffres)
        match = re.search(r'\b(\d{4})\b', year_str)
        if match:
            year_int = int(match.group(1))
            if 1800 <= year_int <= 2025:
                return year_int
        
        # Gérer les plages "2000-2010" -> prendre la moyenne
        if '-' in year_str:
            parts = year_str.split('-')
            try:
                start = int(float(parts[0].strip()))
                end = int(float(parts[1].strip()))
                avg_year = (start + end) // 2
                if 1800 <= avg_year <= 2025:
                    return avg_year
            except:
                return None
        
        # Gérer "20th Century" -> 1950 (milieu du siècle)
        if "20th" in year_str or "20e" in year_str or "20ème" in year_str or "20th Century" in year_str:
            return 1950
        
        # Gérer "19th Century" -> 1850
        if "19th" in year_str or "19e" in year_str or "19ème" in year_str or "19th Century" in year_str:
            return 1850
        
        # Gérer "21st Century" -> 2000
        if "21st" in year_str or "21e" in year_str or "21ème" in year_str or "21st Century" in year_str:
            return 2000
        
        # Gérer "Late" ou "Early" centuries
        if "Late 20th" in year_str:
            return 1975
        if "Early 20th" in year_str:
            return 1925
        if "Late 19th" in year_str:
            return 1875
        if "Early 19th" in year_str:
            return 1825
    
    # Si c'est une liste
    if isinstance(year_str, list):
        if len(year_str) > 0:
            # Prendre le premier élément et le parser
            for item in year_str:
                parsed = parse_year(item)
                if parsed is not None:
                    return parsed
    
    return None

def parse_mass(mass_str):
    """Parse une masse qui peut être un intervalle ou une valeur numérique avec unité"""
    if mass_str is None:
        return None
    
    # Si c'est déjà un nombre
    if isinstance(mass_str, (int, float)):
        return float(mass_str)
    
    # Si c'est une chaîne
    if isinstance(mass_str, str):
        mass_str = str(mass_str).strip()
        
        if mass_str in ["", "AI Predicted", "N/A", "None", "Not predicted", "Not provided"]:
            return None
        
        # Essayer de convertir directement
        try:
            return float(mass_str)
        except ValueError:
            pass
        
        # Chercher un pattern numérique avec unités
        patterns = [
            r'([\d\.]+)\s*g',  # 100g
            r'([\d\.]+)\s*kg',  # 1kg
            r'([\d\.]+)\s*grams',  # 100 grams
        ]
        
        for pattern in patterns:
            match = re.search(pattern, mass_str, re.IGNORECASE)
            if match:
                value = float(match.group(1))
                if 'kg' in mass_str.lower():
                    value *= 1000  # Convertir kg en g
                return value
        
        # Si c'est un intervalle comme "10-100g"
        interval_pattern = r'([\d\.]+)\s*-\s*([\d\.]+)\s*(g|kg)'
        match = re.search(interval_pattern, mass_str, re.IGNORECASE)
        if match:
            start = float(match.group(1))
            end = float(match.group(2))
            unit = match.group(3).lower()
            
            if unit == 'kg':
                start *= 1000
                end *= 1000
            
            # Retourner la moyenne de l'intervalle
            return (start + end) / 2
        
        # Gérer les intervalles prédéfinis
        mass_intervals = {
            "<1g": 0.5,
            "1-10g": 5.5,
            "10-100g": 55,
            "100-1kg": 550,
            "1-10kg": 5500,
            ">10kg": 15000
        }
        
        for interval, avg_value in mass_intervals.items():
            if interval.lower() in mass_str.lower():
                return avg_value
    
    # Si c'est une liste
    if isinstance(mass_str, list):
        if len(mass_str) > 0:
            # Prendre le premier élément et le parser
            for item in mass_str:
                parsed = parse_mass(item)
                if parsed is not None:
                    return parsed
    
    return None

def get_type_color(meteorite_type, color_palette):
    """Get consistent color for meteorite type"""
    if not meteorite_type:
        return "#CCCCCC"
    
    # Calculer un hash simple basé sur le type
    type_str = str(meteorite_type)
    hash_value = sum(ord(c) for c in type_str)
    color_index = hash_value % len(color_palette)
    return color_palette[color_index]

def show_statistics():
    st.title("📈 Advanced Statistics Dashboard")
    
    # Import color palette from prediction_tool if available
    COLOR_PALETTE = [
        "#FF6B6B", "#4ECDC4", "#FFD166", "#06D6A0", "#118AB2", 
        "#EF476F", "#073B4C", "#7209B7", "#F15BB5", "#00BBF9",
        "#00F5D4", "#9B5DE5", "#FEE440", "#00F5D4", "#FB5607",
        "#FF9E6D", "#A78BFA", "#34D399", "#60A5FA", "#F472B6",
        "#818CF8", "#FBBF24", "#10B981", "#8B5CF6", "#EC4899",
        "#14B8A6", "#F97316", "#6366F1", "#84CC16", "#06B6D4"
    ]
    
    if 'predictions' not in st.session_state or not st.session_state.predictions:
        # Empty state with animation
        st.markdown("""
        <div style="text-align: center; padding: 50px;">
            <h2 style="color: #667eea;">📭 No Predictions Yet</h2>
            <p style="color: #b0b0b0; font-size: 16px;">
                Make your first prediction to unlock comprehensive statistics!
            </p>
            <p style="color: #b0b0b0; font-size: 14px;">
                Go to <strong>Prediction Tool</strong> to start analyzing meteorite data
            </p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    predictions = st.session_state.predictions
    
    # KPI Dashboard
    st.markdown("## 📊 Key Performance Indicators")
    
    kpi_cols = st.columns(4)
    
    with kpi_cols[0]:
        total_pred = len(predictions)
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 15px; border: 1px solid rgba(255, 255, 255, 0.1);">
            <div style="font-size: 12px; color: #b0b0b0;">Total Predictions</div>
            <div style="font-size: 32px; font-weight: bold; color: #667eea;">{total_pred}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi_cols[1]:
        avg_conf = sum(p.get('prob', 0) for p in predictions) / len(predictions) if predictions else 0
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 15px; border: 1px solid rgba(255, 255, 255, 0.1);">
            <div style="font-size: 12px; color: #b0b0b0;">Avg Confidence</div>
            <div style="font-size: 32px; font-weight: bold; color: #06D6A0;">{avg_conf:.1%}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi_cols[2]:
        unique_types = len(set(p.get('type', 'Unknown') for p in predictions)) if predictions else 0
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 15px; border: 1px solid rgba(255, 255, 255, 0.1);">
            <div style="font-size: 12px; color: #b0b0b0;">Unique Types</div>
            <div style="font-size: 32px; font-weight: bold; color: #FF6B6B;">{unique_types}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi_cols[3]:
        total_locations = sum(len(p.get('locations', [])) for p in predictions) if predictions else 0
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 15px; border: 1px solid rgba(255, 255, 255, 0.1);">
            <div style="font-size: 12px; color: #b0b0b0;">Total Locations</div>
            <div style="font-size: 32px; font-weight: bold; color: #FFD166;">{total_locations}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📋 Overview", 
        "📈 Type Analysis", 
        "🌍 Geographic",
        "📅 Year Analysis",
        "⚖️ Mass Analysis",
        "🎯 Performance",
        "📤 Export"
    ])
    
    with tab1:
        st.markdown("### 📊 Comprehensive Overview")
        
        # Create summary table
        summary_data = []
        for idx, pred in enumerate(predictions):
            # Compter les pays uniques
            countries = []
            for loc in pred.get('locations', []):
                country = loc.get('country', 'Unknown')
                if country and str(country) not in ['Unknown', 'nan', 'None']:
                    countries.append(str(country))
            
            # Obtenir les informations d'entrée
            input_year = pred.get("input_years", "AI Predicted")
            input_continent = pred.get("input_continent", "AI Predicted")
            input_mass = pred.get("input_mass", "AI Predicted")
            
            # Vérifier si les données ont été fournies ou prédites
            year_source = "Provided" if pred.get("provided_year", False) else "AI Predicted"
            continent_source = "Provided" if pred.get("provided_continent", False) else "AI Predicted"
            mass_source = "Provided" if pred.get("provided_mass", False) else "AI Predicted"
            
            summary_data.append({
                "ID": idx + 1,
                "Type": pred.get("type", "Unknown"),
                "Confidence": f"{pred.get('prob', 0):.1%}",
                "Locations": len(pred.get("locations", [])),
                "Unique Countries": len(set(countries)) if countries else 0,
                "Year": input_year,
                "Year Source": year_source,
                "Continent": input_continent,
                "Continent Source": continent_source,
                "Mass": input_mass,
                "Mass Source": mass_source,
                "Timestamp": pred.get("timestamp", "N/A")
            })
        
        df_summary = pd.DataFrame(summary_data)
        
        # Filtres pour la table
        st.markdown("### 🔍 Filter Data")
        col_filter1, col_filter2, col_filter3 = st.columns(3)
        
        with col_filter1:
            filter_type = st.multiselect(
                "Filter by Type:",
                options=sorted(df_summary["Type"].unique()),
                default=sorted(df_summary["Type"].unique())[:3] if len(df_summary["Type"].unique()) > 3 else sorted(df_summary["Type"].unique())
            )
        
        with col_filter2:
            filter_source = st.multiselect(
                "Filter by Data Source:",
                options=["Provided", "AI Predicted"],
                default=["Provided", "AI Predicted"]
            )
        
        with col_filter3:
            min_confidence = st.slider(
                "Minimum Confidence:",
                min_value=0.0,
                max_value=1.0,
                value=0.0,
                step=0.05,
                format="%.2f"
            )
        
        # Appliquer les filtres
        filtered_df = df_summary.copy()
        if filter_type:
            filtered_df = filtered_df[filtered_df["Type"].isin(filter_type)]
        
        # Convertir la colonne Confidence en numérique pour filtrer
        filtered_df["Confidence_num"] = filtered_df["Confidence"].str.rstrip('%').astype('float') / 100
        filtered_df = filtered_df[filtered_df["Confidence_num"] >= min_confidence]
        filtered_df = filtered_df.drop(columns=["Confidence_num"])
        
        st.dataframe(filtered_df, use_container_width=True, height=400)
        
        # Quick insights
        if len(predictions) > 1:
            st.markdown("### 💡 Quick Insights")
            
            # Top 3 predictions by confidence
            top_3 = sorted(predictions, key=lambda x: x.get('prob', 0), reverse=True)[:3]
            
            cols = st.columns(3)
            for i, pred in enumerate(top_3):
                type_color = get_type_color(pred.get('type', 'Unknown'), COLOR_PALETTE)
                with cols[i]:
                    st.markdown(f"""
                    <div style="background: rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 15px; border: 1px solid rgba(255, 255, 255, 0.1);">
                        <div style="font-size: 12px; color: #b0b0b0;">Top #{i+1} by Confidence</div>
                        <div style="font-size: 18px; font-weight: bold; color: {type_color};">
                            {pred.get('type', 'Unknown')}
                        </div>
                        <div style="font-size: 14px; color: #b0b0b0;">
                            Confidence: {pred.get('prob', 0):.1%}<br>
                            Locations: {len(pred.get('locations', []))}<br>
                            Countries: {len(set(loc.get('country', 'Unknown') for loc in pred.get('locations', [])))}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### 📊 Type Distribution Analysis")
        
        # Type frequency with interactive chart
        type_counts = Counter(p.get('type', 'Unknown') for p in predictions)
        
        if type_counts:
            col_chart1, col_chart2 = st.columns([2, 1])
            
            with col_chart1:
                # Bar chart with type-based colors
                types = list(type_counts.keys())
                counts = list(type_counts.values())
                
                # Créer un DataFrame pour le graphique
                type_df = pd.DataFrame({
                    'Type': types,
                    'Count': counts
                })
                
                fig_types = px.bar(
                    type_df,
                    x='Type',
                    y='Count',
                    labels={'Type': 'Meteorite Type', 'Count': 'Count'},
                    title="Type Frequency Distribution",
                    color='Type',
                    color_discrete_map={t: get_type_color(t, COLOR_PALETTE) for t in types}
                )
                fig_types.update_layout(
                    showlegend=False,
                    xaxis_tickangle=45,
                    height=400
                )
                st.plotly_chart(fig_types, use_container_width=True)
            
            with col_chart2:
                # Donut chart
                fig_donut = px.pie(
                    values=counts,
                    names=types,
                    title="Type Distribution",
                    hole=0.4,
                    color=types,
                    color_discrete_map={t: get_type_color(t, COLOR_PALETTE) for t in types}
                )
                fig_donut.update_traces(textposition='inside', textinfo='percent+label')
                fig_donut.update_layout(height=400)
                st.plotly_chart(fig_donut, use_container_width=True)
            
            # Confidence by type
            if len(predictions) > 1:
                st.markdown("### 📈 Confidence by Type")
                
                conf_by_type = {}
                for pred in predictions:
                    pred_type = pred.get('type', 'Unknown')
                    if pred_type not in conf_by_type:
                        conf_by_type[pred_type] = []
                    conf_by_type[pred_type].append(pred.get('prob', 0))
                
                if conf_by_type:
                    # Créer un DataFrame pour la visualisation
                    box_data = []
                    for type_name, confidences in conf_by_type.items():
                        for conf in confidences:
                            box_data.append({
                                'Type': type_name,
                                'Confidence': conf
                            })
                    
                    if box_data:
                        df_box = pd.DataFrame(box_data)
                        
                        fig_conf_box = px.box(
                            df_box,
                            x='Type',
                            y='Confidence',
                            labels={'Type': 'Meteorite Type', 'Confidence': 'Confidence Score'},
                            title="Confidence Distribution by Type",
                            color='Type',
                            color_discrete_map={t: get_type_color(t, COLOR_PALETTE) for t in df_box['Type'].unique()}
                        )
                        fig_conf_box.update_layout(
                            xaxis_tickangle=45,
                            height=400,
                            yaxis=dict(tickformat=".0%")
                        )
                        st.plotly_chart(fig_conf_box, use_container_width=True)
    
    with tab3:
        st.markdown("### 🌍 Geographic Analysis")
        
        # Country analysis
        all_countries = []
        for pred in predictions:
            for loc in pred.get('locations', []):
                country = loc.get('country')
                if country and str(country) not in ['nan', 'None', 'Unknown', '']:
                    all_countries.append(str(country).strip())
        
        if all_countries:
            country_counts = Counter(all_countries)
            
            # Top countries chart
            top_n = min(20, len(country_counts))
            top_countries = dict(sorted(country_counts.items(), 
                                      key=lambda x: x[1], reverse=True)[:top_n])
            
            # Récupérer les couleurs des pays si disponibles
            country_colors = {}
            if 'country_colors' in st.session_state:
                country_colors = st.session_state.country_colors
            
            # Créer un DataFrame pour le graphique
            country_df = pd.DataFrame({
                'Country': list(top_countries.keys()),
                'Count': list(top_countries.values())
            })
            
            fig_countries = px.bar(
                country_df,
                x='Count',
                y='Country',
                orientation='h',
                labels={'Count': 'Count', 'Country': 'Country'},
                title=f"Top {top_n} Countries by Meteorite Count",
                color='Country',
                color_discrete_map={country: country_colors.get(country, COLOR_PALETTE[i % len(COLOR_PALETTE)]) 
                                  for i, country in enumerate(top_countries.keys())}
            )
            fig_countries.update_layout(
                height=500,
                yaxis={'categoryorder': 'total ascending'}
            )
            st.plotly_chart(fig_countries, use_container_width=True)
            
            # World map visualization
            if len(country_counts) > 1:
                st.markdown("### 🗺️ Global Distribution")
                
                # Préparer les données pour la carte mondiale
                world_data = []
                for country, count in country_counts.items():
                    world_data.append({
                        'Country': country,
                        'Count': count,
                        'LogCount': math.log(count + 1)  # Pour une meilleure visualisation
                    })
                
                df_world = pd.DataFrame(world_data)
                
                fig_world = px.choropleth(
                    df_world,
                    locations='Country',
                    locationmode='country names',
                    color='LogCount',
                    hover_name='Country',
                    hover_data={'Count': True, 'LogCount': False, 'Country': False},
                    title='Meteorite Distribution by Country',
                    color_continuous_scale='Viridis',
                    range_color=(0, df_world['LogCount'].max()),
                    labels={'LogCount': 'Frequency (log scale)'}
                )
                
                fig_world.update_layout(
                    geo=dict(
                        showframe=False,
                        showcoastlines=True,
                        projection_type='equirectangular',
                        showland=True,
                        landcolor='rgb(217, 217, 217)',
                        bgcolor='rgba(0,0,0,0)'
                    ),
                    height=500
                )
                
                st.plotly_chart(fig_world, use_container_width=True)
        else:
            st.info("No country data available in predictions.")
    
    with tab4:
        st.markdown("### 📅 Year Analysis")
        
        # Collect year information from multiple sources
        year_data = []
        for pred_idx, pred in enumerate(predictions):
            # Source 1: Années d'entrée (input_years)
            input_years = pred.get('input_years', '')
            parsed_year = parse_year(input_years)
            if parsed_year is not None:
                year_data.append({
                    "Prediction_ID": pred_idx + 1,
                    "Year": parsed_year,
                    "Source": "User Input",
                    "Type": pred.get('type', 'Unknown'),
                    "Confidence": pred.get('prob', 0),
                    "Original": input_years
                })
            
            # Source 2: Années prédites (predicted_years)
            predicted_years = pred.get('predicted_years', '')
            if predicted_years and predicted_years != "Not predicted":
                parsed_year = parse_year(predicted_years)
                if parsed_year is not None:
                    year_data.append({
                        "Prediction_ID": pred_idx + 1,
                        "Year": parsed_year,
                        "Source": "AI Predicted",
                        "Type": pred.get('type', 'Unknown'),
                        "Confidence": pred.get('prob', 0),
                        "Original": predicted_years
                    })
            
            # Source 3: Années d'échantillon (sample_years)
            sample_years = pred.get('sample_years', [])
            for sample_year in sample_years:
                parsed_year = parse_year(sample_year)
                if parsed_year is not None:
                    year_data.append({
                        "Prediction_ID": pred_idx + 1,
                        "Year": parsed_year,
                        "Source": "Sample Data",
                        "Type": pred.get('type', 'Unknown'),
                        "Confidence": pred.get('prob', 0),
                        "Original": str(sample_year)
                    })
        
        if year_data:
            # Créer le DataFrame
            df_years = pd.DataFrame(year_data)
            
            if not df_years.empty:
                # S'assurer que Year est numérique
                df_years['Year'] = pd.to_numeric(df_years['Year'], errors='coerce')
                df_years = df_years.dropna(subset=['Year'])
                df_years['Year'] = df_years['Year'].astype(int)
                
                # Filtrer les années extrêmes
                df_years = df_years[(df_years['Year'] >= 1800) & (df_years['Year'] <= 2025)]
                
                # Distribution globale des années
                st.markdown("#### 📊 Year Distribution")
                
                fig_hist = px.histogram(
                    df_years, 
                    x='Year',
                    nbins=min(50, len(df_years['Year'].unique())),
                    title="Distribution of All Years",
                    labels={'Year': 'Year', 'count': 'Count'},
                    color_discrete_sequence=['#667eea']
                )
                fig_hist.update_layout(height=400)
                st.plotly_chart(fig_hist, use_container_width=True)
                
                # Distribution par source
                if len(df_years['Source'].unique()) > 1:
                    st.markdown("#### 📈 Year Distribution by Source")
                    
                    fig_source = px.histogram(
                        df_years,
                        x='Year',
                        color='Source',
                        nbins=min(30, len(df_years['Year'].unique())),
                        title="Year Distribution by Data Source",
                        labels={'Year': 'Year', 'count': 'Count'},
                        color_discrete_sequence=['#667eea', '#06D6A0', '#FF6B6B']
                    )
                    fig_source.update_layout(height=400)
                    st.plotly_chart(fig_source, use_container_width=True)
                
                # Année vs Confiance
                st.markdown("#### 📈 Year vs Confidence")
                
                fig_scatter = px.scatter(
                    df_years,
                    x='Year',
                    y='Confidence',
                    color='Type',
                    title="Year vs Confidence by Meteorite Type",
                    labels={'Year': 'Year', 'Confidence': 'Confidence', 'Type': 'Meteorite Type'},
                    hover_data=['Source', 'Original', 'Prediction_ID']
                )
                fig_scatter.update_layout(height=500, yaxis=dict(tickformat=".0%"))
                st.plotly_chart(fig_scatter, use_container_width=True)
                
                # Statistiques résumées
                st.markdown("#### 📋 Year Statistics")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    avg_year = df_years['Year'].mean()
                    st.metric("Average Year", f"{avg_year:.0f}")
                
                with col2:
                    median_year = df_years['Year'].median()
                    st.metric("Median Year", f"{median_year:.0f}")
                
                with col3:
                    if len(df_years) > 1:
                        year_range = df_years['Year'].max() - df_years['Year'].min()
                        st.metric("Year Range", f"{year_range:.0f} years")
                
                with col4:
                    most_common_year = df_years['Year'].mode()[0] if not df_years['Year'].mode().empty else 0
                    count_most_common = (df_years['Year'] == most_common_year).sum()
                    st.metric("Most Common Year", f"{most_common_year} ({count_most_common}x)")
                
                # Données brutes pour débogage
                with st.expander("🔍 View Detailed Year Data"):
                    st.dataframe(df_years[['Prediction_ID', 'Type', 'Year', 'Source', 'Confidence', 'Original']])
            else:
                st.info("No valid numeric year data available after parsing.")
        else:
            st.info("No year data available in predictions.")
    
    with tab5:
        st.markdown("### ⚖️ Mass Analysis")
        
        # Collect mass information
        mass_data = []
        for pred_idx, pred in enumerate(predictions):
            # Source 1: Masse d'entrée (input_mass)
            input_mass = pred.get('input_mass', '')
            parsed_mass = parse_mass(input_mass)
            if parsed_mass is not None:
                mass_data.append({
                    "Prediction_ID": pred_idx + 1,
                    "Mass_grams": parsed_mass,
                    "Source": "User Input",
                    "Type": pred.get('type', 'Unknown'),
                    "Confidence": pred.get('prob', 0),
                    "Original": input_mass
                })
            
            # Source 2: Masse prédite (predicted_mass)
            predicted_mass = pred.get('predicted_mass', [])
            if isinstance(predicted_mass, list):
                for mass_item in predicted_mass:
                    if mass_item != "Not predicted":
                        parsed_mass = parse_mass(mass_item)
                        if parsed_mass is not None:
                            mass_data.append({
                                "Prediction_ID": pred_idx + 1,
                                "Mass_grams": parsed_mass,
                                "Source": "AI Predicted",
                                "Type": pred.get('type', 'Unknown'),
                                "Confidence": pred.get('prob', 0),
                                "Original": str(mass_item)
                            })
        
        if mass_data:
            # Créer le DataFrame
            df_mass = pd.DataFrame(mass_data)
            
            if not df_mass.empty:
                # Distribution des masses
                st.markdown("#### 📊 Mass Distribution")
                
                # Utiliser une échelle logarithmique pour les masses
                df_mass['Log_Mass'] = np.log10(df_mass['Mass_grams'] + 1)
                
                fig_mass = px.histogram(
                    df_mass,
                    x='Log_Mass',
                    nbins=30,
                    title="Distribution of Meteorite Masses (log scale)",
                    labels={'Log_Mass': 'Mass (log10 grams)', 'count': 'Count'},
                    color_discrete_sequence=['#FF6B6B']
                )
                fig_mass.update_layout(height=400)
                st.plotly_chart(fig_mass, use_container_width=True)
                
                # Mass vs Confidence
                st.markdown("#### 📈 Mass vs Confidence")
                
                fig_scatter_mass = px.scatter(
                    df_mass,
                    x='Mass_grams',
                    y='Confidence',
                    color='Type',
                    log_x=True,  # Échelle logarithmique pour l'axe des x
                    title="Mass vs Confidence by Meteorite Type",
                    labels={'Mass_grams': 'Mass (grams, log scale)', 'Confidence': 'Confidence', 'Type': 'Meteorite Type'},
                    hover_data=['Source', 'Original', 'Prediction_ID']
                )
                fig_scatter_mass.update_layout(height=500, yaxis=dict(tickformat=".0%"))
                st.plotly_chart(fig_scatter_mass, use_container_width=True)
                
                # Statistiques résumées
                st.markdown("#### 📋 Mass Statistics")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    avg_mass = df_mass['Mass_grams'].mean()
                    if avg_mass >= 1000:
                        st.metric("Average Mass", f"{avg_mass/1000:.1f} kg")
                    else:
                        st.metric("Average Mass", f"{avg_mass:.0f} g")
                
                with col2:
                    median_mass = df_mass['Mass_grams'].median()
                    if median_mass >= 1000:
                        st.metric("Median Mass", f"{median_mass/1000:.1f} kg")
                    else:
                        st.metric("Median Mass", f"{median_mass:.0f} g")
                
                with col3:
                    min_mass = df_mass['Mass_grams'].min()
                    max_mass = df_mass['Mass_grams'].max()
                    st.metric("Mass Range", f"{min_mass:.0f}g - {max_mass:.0f}g")
                
                with col4:
                    # Catégoriser les masses
                    df_mass['Mass_Category'] = pd.cut(
                        df_mass['Mass_grams'],
                        bins=[0, 1, 10, 100, 1000, 10000, float('inf')],
                        labels=['<1g', '1-10g', '10-100g', '100g-1kg', '1-10kg', '>10kg']
                    )
                    most_common_cat = df_mass['Mass_Category'].mode()[0] if not df_mass['Mass_Category'].mode().empty else 'Unknown'
                    st.metric("Most Common Category", str(most_common_cat))
                
                # Distribution par catégorie
                st.markdown("#### 📊 Mass Category Distribution")
                
                # Calculer les comptes par catégorie
                category_counts = df_mass['Mass_Category'].value_counts().reset_index()
                category_counts.columns = ['Mass_Category', 'Count']
                
                fig_cat = px.bar(
                    category_counts,
                    x='Mass_Category',
                    y='Count',
                    title="Meteorite Count by Mass Category",
                    labels={'Mass_Category': 'Mass Category', 'Count': 'Count'},
                    color='Mass_Category',
                    color_discrete_sequence=COLOR_PALETTE[:6]
                )
                fig_cat.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig_cat, use_container_width=True)
                
                # Données brutes pour débogage
                with st.expander("🔍 View Detailed Mass Data"):
                    st.dataframe(df_mass[['Prediction_ID', 'Type', 'Mass_grams', 'Mass_Category', 'Source', 'Confidence', 'Original']])
            else:
                st.info("No valid mass data available after parsing.")
        else:
            st.info("No mass data available in predictions.")
    
    with tab6:
        st.markdown("### 🎯 Performance Metrics")
        
        if predictions:
            # Performance metrics
            confidence_scores = [p.get('prob', 0) for p in predictions]
            
            col_perf1, col_perf2, col_perf3, col_perf4 = st.columns(4)
            
            with col_perf1:
                mean_conf = np.mean(confidence_scores)
                st.metric("Mean Confidence", f"{mean_conf:.1%}")
            
            with col_perf2:
                median_conf = np.median(confidence_scores)
                st.metric("Median Confidence", f"{median_conf:.1%}")
            
            with col_perf3:
                std_conf = np.std(confidence_scores) if len(confidence_scores) > 1 else 0
                st.metric("Std Deviation", f"{std_conf:.3f}")
            
            with col_perf4:
                min_conf = np.min(confidence_scores)
                max_conf = np.max(confidence_scores)
                st.metric("Confidence Range", f"{min_conf:.1%} - {max_conf:.1%}")
            
            # Performance trends
            if len(predictions) > 2:
                st.markdown("### 📈 Performance Trends")
                
                # Courbe de confiance au fil du temps
                prediction_numbers = list(range(1, len(confidence_scores) + 1))
                
                # Moving average
                window = min(5, len(confidence_scores))
                moving_avg = pd.Series(confidence_scores).rolling(window=window).mean()
                
                fig_trend = go.Figure()
                fig_trend.add_trace(go.Scatter(
                    x=prediction_numbers,
                    y=confidence_scores,
                    mode='lines+markers',
                    name='Confidence',
                    line=dict(color='#667eea', width=2),
                    marker=dict(size=6)
                ))
                fig_trend.add_trace(go.Scatter(
                    x=prediction_numbers[(window-1):],
                    y=moving_avg.dropna(),
                    mode='lines',
                    name=f'{window}-Prediction Moving Avg',
                    line=dict(color='#FF6B6B', width=3, dash='dash')
                ))
                
                fig_trend.update_layout(
                    title='Confidence Trend Over Predictions',
                    xaxis_title="Prediction Number",
                    yaxis_title="Confidence",
                    showlegend=True,
                    hovermode='x unified',
                    height=500,
                    yaxis=dict(tickformat=".0%")
                )
                
                st.plotly_chart(fig_trend, use_container_width=True)
                
                # Analyse des types les plus confiants
                st.markdown("### 🏆 Top Performing Types")
                
                # Grouper par type et calculer la confiance moyenne
                type_performance = {}
                for pred in predictions:
                    pred_type = pred.get('type', 'Unknown')
                    if pred_type not in type_performance:
                        type_performance[pred_type] = []
                    type_performance[pred_type].append(pred.get('prob', 0))
                
                # Calculer les moyennes
                type_avg_conf = {t: np.mean(confs) for t, confs in type_performance.items()}
                
                # Prendre les top 5 types par confiance moyenne
                top_types = sorted(type_avg_conf.items(), key=lambda x: x[1], reverse=True)[:5]
                
                if top_types:
                    types_list = [t[0] for t in top_types]
                    avg_confs = [t[1] for t in top_types]
                    
                    # Créer un DataFrame pour le graphique
                    top_types_df = pd.DataFrame({
                        'Type': types_list,
                        'Average_Confidence': avg_confs
                    })
                    
                    fig_top_types = px.bar(
                        top_types_df,
                        x='Type',
                        y='Average_Confidence',
                        title="Top 5 Meteorite Types by Average Confidence",
                        labels={'Type': 'Meteorite Type', 'Average_Confidence': 'Average Confidence'},
                        color='Type',
                        color_discrete_map={t: get_type_color(t, COLOR_PALETTE) for t in types_list}
                    )
                    fig_top_types.update_layout(
                        showlegend=False,
                        height=400,
                        yaxis=dict(tickformat=".0%")
                    )
                    st.plotly_chart(fig_top_types, use_container_width=True)
    
    with tab7:
        st.markdown("### 📤 Advanced Data Export")
        
        # Export options
        export_options = st.multiselect(
            "Select data to export:",
            ["Predictions Summary", "Location Details", "Country Statistics", 
             "Type Analysis", "Year Analysis", "Mass Analysis", "Performance Metrics", "Full Dataset"],
            default=["Predictions Summary", "Full Dataset"]
        )
        
        if st.button("🔄 Generate Export Package", type="primary", use_container_width=True):
            with st.spinner("📦 Preparing export package..."):
                export_data = {}
                
                # Helper function to safely serialize data
                def safe_serialize(obj):
                    if isinstance(obj, (str, int, float, bool, type(None))):
                        return obj
                    elif isinstance(obj, dict):
                        return {k: safe_serialize(v) for k, v in obj.items()}
                    elif isinstance(obj, list):
                        return [safe_serialize(item) for item in obj]
                    else:
                        return str(obj)
                
                if "Predictions Summary" in export_options:
                    summary_data = []
                    for idx, pred in enumerate(predictions):
                        # Parser l'année pour l'export
                        year_input = pred.get("input_years", "")
                        parsed_year = parse_year(year_input)
                        
                        # Parser la masse pour l'export
                        mass_input = pred.get("input_mass", "")
                        parsed_mass = parse_mass(mass_input)
                        
                        summary_data.append({
                            "ID": idx + 1,
                            "Type": pred.get("type", "Unknown"),
                            "Confidence": pred.get('prob', 0),
                            "Locations": len(pred.get("locations", [])),
                            "Year_Input": year_input,
                            "Year_Parsed": parsed_year if parsed_year is not None else "",
                            "Mass_Input": mass_input,
                            "Mass_Parsed": parsed_mass if parsed_mass is not None else "",
                            "Continent_Input": pred.get("input_continent", "AI Predicted"),
                            "Year_Predicted": pred.get("predicted_years", ""),
                            "Mass_Predicted": pred.get("predicted_mass", []),
                            "Continent_Predicted": pred.get("predicted_continent", []),
                            "Countries_Count": len(pred.get("countries", [])),
                            "Timestamp": pred.get("timestamp", "N/A")
                        })
                    export_data["predictions_summary"] = summary_data
                
                if "Location Details" in export_options:
                    location_data = []
                    for pred_idx, pred in enumerate(predictions):
                        for loc in pred.get("locations", []):
                            location_data.append({
                                "Prediction_ID": pred_idx + 1,
                                "Prediction_Type": pred.get("type", "Unknown"),
                                "Location_Name": loc.get("name", "Unknown"),
                                "Country": loc.get("country", "Unknown"),
                                "Latitude": loc.get("latitude"),
                                "Longitude": loc.get("longitude"),
                                "Color": loc.get("color", "#CCCCCC")
                            })
                    export_data["locations"] = location_data
                
                if "Country Statistics" in export_options:
                    # Compter les pays
                    all_countries = []
                    for pred in predictions:
                        for loc in pred.get('locations', []):
                            country = loc.get('country')
                            if country:
                                all_countries.append(str(country).strip())
                    
                    if all_countries:
                        country_counts = Counter(all_countries)
                        country_stats = [{"Country": k, "Count": v} for k, v in country_counts.items()]
                        export_data["country_statistics"] = country_stats
                
                if "Type Analysis" in export_options:
                    type_counts = Counter(p.get('type', 'Unknown') for p in predictions)
                    type_analysis = [{"Type": k, "Count": v} for k, v in type_counts.items()]
                    export_data["type_analysis"] = type_analysis
                
                if "Year Analysis" in export_options:
                    year_data_export = []
                    for pred_idx, pred in enumerate(predictions):
                        # Collecter toutes les sources d'années
                        sources = [
                            ("input_years", "User Input"),
                            ("predicted_years", "AI Predicted"),
                            ("sample_years", "Sample Data")
                        ]
                        
                        for field, source_name in sources:
                            value = pred.get(field)
                            if value:
                                parsed_year = parse_year(value)
                                if parsed_year is not None:
                                    year_data_export.append({
                                        "Prediction_ID": pred_idx + 1,
                                        "Year": parsed_year,
                                        "Source": source_name,
                                        "Type": pred.get('type', 'Unknown'),
                                        "Original": str(value)
                                    })
                    
                    if year_data_export:
                        export_data["year_analysis"] = year_data_export
                
                if "Mass Analysis" in export_options:
                    mass_data_export = []
                    for pred_idx, pred in enumerate(predictions):
                        # Collecter toutes les sources de masse
                        sources = [
                            ("input_mass", "User Input"),
                            ("predicted_mass", "AI Predicted")
                        ]
                        
                        for field, source_name in sources:
                            value = pred.get(field)
                            if value:
                                parsed_mass = parse_mass(value)
                                if parsed_mass is not None:
                                    mass_data_export.append({
                                        "Prediction_ID": pred_idx + 1,
                                        "Mass_grams": parsed_mass,
                                        "Source": source_name,
                                        "Type": pred.get('type', 'Unknown'),
                                        "Original": str(value)
                                    })
                    
                    if mass_data_export:
                        export_data["mass_analysis"] = mass_data_export
                
                if "Performance Metrics" in export_options:
                    confidence_scores = [p.get('prob', 0) for p in predictions]
                    perf_metrics = {
                        "mean_confidence": float(np.mean(confidence_scores)) if confidence_scores else 0,
                        "median_confidence": float(np.median(confidence_scores)) if confidence_scores else 0,
                        "std_confidence": float(np.std(confidence_scores)) if len(confidence_scores) > 1 else 0,
                        "min_confidence": float(np.min(confidence_scores)) if confidence_scores else 0,
                        "max_confidence": float(np.max(confidence_scores)) if confidence_scores else 0,
                        "total_predictions": len(predictions),
                        "unique_types": len(set(p.get('type', 'Unknown') for p in predictions)),
                        "total_locations": sum(len(p.get('locations', [])) for p in predictions),
                        "average_locations_per_prediction": sum(len(p.get('locations', [])) for p in predictions) / len(predictions) if predictions else 0
                    }
                    export_data["performance_metrics"] = perf_metrics
                
                if "Full Dataset" in export_options:
                    # Export sécurisé de toutes les données
                    full_dataset = []
                    for pred in predictions:
                        # Créer une copie sécurisée
                        safe_pred = {
                            'type': pred.get('type', 'Unknown'),
                            'probability': pred.get('prob', 0),
                            'input_data': {
                                'years': pred.get('input_years', ''),
                                'mass': pred.get('input_mass', ''),
                                'continent': pred.get('input_continent', '')
                            },
                            'predictions': {
                                'years': pred.get('predicted_years', ''),
                                'mass': pred.get('predicted_mass', []),
                                'continent': pred.get('predicted_continent', [])
                            },
                            'sample_data': {
                                'countries': pred.get('countries', []),
                                'names': pred.get('names', []),
                                'sample_years': pred.get('sample_years', [])
                            },
                            'metadata': {
                                'timestamp': pred.get('timestamp', ''),
                                'id': pred.get('id', 0),
                                'locations_count': len(pred.get('locations', []))
                            }
                        }
                        full_dataset.append(safe_pred)
                    
                    export_data["full_dataset"] = full_dataset
                
                # Create timestamp for filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                # Download buttons
                st.markdown("### 📥 Download Options")
                
                col_dl1, col_dl2, col_dl3 = st.columns(3)
                
                with col_dl1:
                    # Export JSON complet
                    json_export = json.dumps(safe_serialize(export_data), indent=2)
                    st.download_button(
                        label="📥 Download JSON (Complete)",
                        data=json_export,
                        file_name=f"meteorite_statistics_complete_{timestamp}.json",
                        mime="application/json",
                        use_container_width=True
                    )
                
                with col_dl2:
                    # Export CSV (summary seulement)
                    if "predictions_summary" in export_data:
                        df_summary_export = pd.DataFrame(export_data["predictions_summary"])
                        csv_summary = df_summary_export.to_csv(index=False)
                        st.download_button(
                            label="📥 Download CSV (Summary)",
                            data=csv_summary,
                            file_name=f"meteorite_summary_{timestamp}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                
                with col_dl3:
                    # Export Excel
                    if "predictions_summary" in export_data:
                        # Créer un fichier Excel avec plusieurs onglets
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            if "predictions_summary" in export_data:
                                pd.DataFrame(export_data["predictions_summary"]).to_excel(
                                    writer, sheet_name='Summary', index=False
                                )
                            if "locations" in export_data:
                                pd.DataFrame(export_data["locations"]).to_excel(
                                    writer, sheet_name='Locations', index=False
                                )
                            if "type_analysis" in export_data:
                                pd.DataFrame(export_data["type_analysis"]).to_excel(
                                    writer, sheet_name='Types', index=False
                                )
                        
                        excel_data = output.getvalue()
                        st.download_button(
                            label="📥 Download Excel",
                            data=excel_data,
                            file_name=f"meteorite_statistics_{timestamp}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                
                st.success(f"✅ Export package generated successfully! ({len(export_data)} datasets included)")
        
        # Session management
        st.markdown("---")
        st.markdown("### ⚙️ Session Management")
        
        col_sess1, col_sess2 = st.columns(2)
        
        with col_sess1:
            if st.button("🗑️ Clear All Data", type="secondary", use_container_width=True):
                st.session_state.predictions = []
                if 'country_colors' in st.session_state:
                    st.session_state.country_colors = {}
                st.success("✅ All data cleared successfully!")
                st.rerun()
        
        with col_sess2:
            if st.button("🔄 Refresh Dashboard", type="primary", use_container_width=True):
                st.rerun()