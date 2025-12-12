# pages/home.py
import streamlit as st

def show_home():
    st.markdown("# 🌠 Welcome to Meteorite Type Predictor")
    
    # Hero section
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
                border-radius: 20px; padding: 30px; margin: 20px 0; border: 1px solid rgba(255, 255, 255, 0.1);">
        <h2 style="color: white; text-align: center;">
            Advanced Meteorite Analysis Platform
        </h2>
        <p style="text-align: center; color: #b0b0b0; font-size: 18px;">
            Powered by Machine Learning • Real-time Predictions • Global Database
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Features grid
    st.markdown("## 🚀 Key Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 16px; color: #667eea; font-weight: bold;">🎯 Smart Prediction</div>
            <div style="font-size: 14px; color: #b0b0b0; margin-top: 10px;">
                Leave any field empty and let AI predict the missing values based on patterns
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 16px; color: #06D6A0; font-weight: bold;">🌍 Global Coverage</div>
            <div style="font-size: 14px; color: #b0b0b0; margin-top: 10px;">
                Database with 200+ countries and exact geographic coordinates for precise mapping
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 16px; color: #FF6B6B; font-weight: bold;">📈 Advanced Analytics</div>
            <div style="font-size: 14px; color: #b0b0b0; margin-top: 10px;">
                Comprehensive statistics, trend analysis, and performance metrics
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # How to use section
    st.markdown("## 📖 How to Use")
    
    steps = [
        ("1️⃣", "Go to **Prediction Tool** page", "#667eea"),
        ("2️⃣", "Select filters (year, continent, mass) - leave empty for AI prediction", "#06D6A0"),
        ("3️⃣", "Click **Predict** to get instant results", "#FF6B6B"),
        ("4️⃣", "View predictions on interactive maps", "#FFD166"),
        ("5️⃣", "Analyze results in **Statistics** dashboard", "#9B5DE5"),
        ("6️⃣", "Export data for further analysis", "#00BBF9")
    ]
    
    for icon, text, color in steps:
        st.markdown(f"""
        <div style="display: flex; align-items: center; margin: 15px 0; padding: 15px; 
                    background: rgba(255, 255, 255, 0.05); border-radius: 10px;
                    border-left: 4px solid {color};">
            <span style="font-size: 24px; margin-right: 15px;">{icon}</span>
            <span style="color: white; font-size: 16px;">{text}</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick start buttons
    st.markdown("## 🎮 Quick Start")
    
    col_start1, col_start2, col_start3 = st.columns(3)
    
    with col_start1:
        if st.button("🚀 Launch Prediction Tool", use_container_width=True):
            st.session_state.current_page = "Prediction Tool"
            st.rerun()
    
    with col_start2:
        if st.button("📊 View Statistics", use_container_width=True):
            st.session_state.current_page = "Statistics"
            st.rerun()
    
    with col_start3:
        if st.button("🌍 Explore Dataset", use_container_width=True):
            st.session_state.current_page = "Data Overview"
            st.rerun()
    
    # Tech stack
    st.markdown("## 🔧 Technology Stack")
    
    tech_cols = st.columns(4)
    techs = [
        ("Python", "https://img.icons8.com/color/48/000000/python.png"),
        ("Streamlit", "https://streamlit.io/images/brand/streamlit-mark-color.png"),
        ("Flask", "https://img.icons8.com/color/48/000000/flask.png"),
        ("Plotly", "https://img.icons8.com/color/48/000000/chart.png"),
        ("Folium", "https://leafletjs.com/docs/images/logo.png"),
        ("Pandas", "https://img.icons8.com/color/48/000000/pandas.png"),
        ("Scikit-learn", "https://scikit-learn.org/stable/_static/scikit-learn-logo-small.png"),
        ("Machine Learning", "https://img.icons8.com/color/48/000000/artificial-intelligence.png")
    ]
    
    for i, (name, icon) in enumerate(techs):
        with tech_cols[i % 4]:
            st.markdown(f"""
            <div style="text-align: center; padding: 10px;">
                <img src="{icon}" width="40" height="40">
                <div style="color: white; margin-top: 5px; font-size: 12px;">{name}</div>
            </div>
            """, unsafe_allow_html=True)