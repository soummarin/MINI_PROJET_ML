# app.py (frontend)
import streamlit as st

# Import our page modules
from pages import home, prediction_tool, ideas, statistics

# Configure the page
st.set_page_config(
    page_title="🌠 Meteorite Type Predictor",
    page_icon="🌠",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo',
        'Report a bug': 'https://github.com/your-repo/issues',
        'About': '# Meteorite Prediction System v2.0'
    }
)

# Custom CSS for modern, professional styling
st.markdown("""
<style>
    /* Main theme */
    .main {
        background-color: #0E1117;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
        padding: 20px 15px;
        border-right: 1px solid #2d3746;
        width: 260px !important;
        min-width: 260px !important;
        max-width: 260px !important;
    }
    
    /* Hide default sidebar elements */
    [data-testid="stSidebarNav"] {
        display: none;
    }
    
    /* Sidebar titles */
    .sidebar-title {
        color: #ffffff;
        font-size: 28px;
        font-weight: 700;
        margin-bottom: 30px;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 10px;
    }
    
    /* Navigation buttons */
    .nav-button {
        width: 100%;
        padding: 12px 20px;
        margin: 8px 0;
        border-radius: 10px;
        border: none;
        background: rgba(255, 255, 255, 0.05);
        color: #e0e0e0;
        text-align: left;
        font-size: 16px;
        font-weight: 500;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        gap: 12px;
        cursor: pointer;
    }
    
    .nav-button:hover {
        background: linear-gradient(90deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
        transform: translateX(5px);
        color: #ffffff;
        border-left: 3px solid #667eea;
    }
    
    .nav-button.active {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    /* Metrics cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin: 10px 0;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        background: rgba(255, 255, 255, 0.08);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
    }
    
    /* Main content area */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #ffffff !important;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700 !important;
    }
    
    /* Dataframe styling */
    .dataframe {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255, 255, 255, 0.05);
        padding: 8px;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 10px 24px;
        background: transparent !important;
        border-radius: 8px;
        color: #b0b0b0;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    /* Input fields */
    .stSelectbox, .stNumberInput, .stTextInput {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 10px !important;
        color: white !important;
    }
    
    /* Success/Info/Warning boxes */
    .stAlert {
        border-radius: 10px;
        border: none;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize page in session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Home"

# Sidebar navigation with enhanced design
with st.sidebar:
    # Hide default sidebar navigation
    st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {
            display: none;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Animated title
    st.markdown("""
    <div class="sidebar-title">
        🌠 Meteorite<br>Predictor
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation buttons with icons
    pages = {
        "🏠 Home": "Home",
        "🎯 Prediction Tool": "Prediction Tool", 
        "📊 Statistics": "Statistics",
      
        "💡 Ideas": "Ideas/Improvements"
    }
    
    for display_name, page_name in pages.items():
        is_active = st.session_state.current_page == page_name
        
        # Create button
        if st.button(display_name, key=f"nav_{page_name}", use_container_width=True, 
                    type="primary" if is_active else "secondary"):
            st.session_state.current_page = page_name
            st.rerun()
    
    st.markdown("---")
    
    # Enhanced session info cards
    if 'predictions' in st.session_state and st.session_state.predictions:
        st.markdown("""
        <div style="color: white; margin-top: 20px;">
            <h4 style="color: #667eea; margin-bottom: 15px;">📊 Session Stats</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Create metrics cards
        predictions_count = len(st.session_state.predictions)
        unique_types = len(set(p['type'] for p in st.session_state.predictions))
        avg_confidence = sum(p['prob'] for p in st.session_state.predictions) / predictions_count if predictions_count > 0 else 0
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 12px; color: #b0b0b0;">Predictions</div>
                <div style="font-size: 24px; font-weight: bold; color: #667eea;">{predictions_count}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 12px; color: #b0b0b0;">Unique Types</div>
                <div style="font-size: 24px; font-weight: bold; color: #764ba2;">{unique_types}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 12px; color: #b0b0b0;">Avg Confidence</div>
            <div style="font-size: 24px; font-weight: bold; color: #00d4aa;">{avg_confidence:.1%}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Add footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #888; font-size: 12px; margin-top: 30px;">
        <div>🚀 Meteorite Prediction System</div>
        <div style="margin-top: 5px;">v2.0 • Advanced Analytics</div>
    </div>
    """, unsafe_allow_html=True)

# Route to the selected page
if st.session_state.current_page == "Home":
    home.show_home()
elif st.session_state.current_page == "Prediction Tool":
    prediction_tool.show_prediction_tool()
elif st.session_state.current_page == "Statistics":
    statistics.show_statistics()
elif st.session_state.current_page == "Ideas/Improvements":
    ideas.show_ideas()