# pages/ideas.py
import streamlit as st

def show_ideas():
    st.title("💡 Future Improvements & Ideas")
    
    # Categories of improvements
    categories = {
        "🎯 Enhanced Features": [
            "Real-time collaborative predictions with multiple users",
            "Advanced clustering algorithms for meteorite classification",
            "Predictive analytics for future meteorite falls",
            "Integration with satellite data for real-time tracking",
            "Mobile application with push notifications"
        ],
        "📊 Data & Analytics": [
            "Historical trend analysis with time series forecasting",
            "Advanced anomaly detection for rare meteorite types",
            "3D visualization of meteorite trajectories",
            "Machine learning model performance dashboard",
            "Automated report generation with insights"
        ],
        "🌍 User Experience": [
            "Dark/Light theme toggle for better accessibility",
            "Voice commands for hands-free operation",
            "Multi-language support (French, Spanish, Arabic, etc.)",
            "Progressive Web App (PWA) for offline access",
            "Customizable dashboard with drag-and-drop widgets"
        ],
        "🔧 Technical Improvements": [
            "Containerization with Docker for easy deployment",
            "Microservices architecture for scalability",
            "Real-time WebSocket connections for live updates",
            "GraphQL API for flexible data queries",
            "Automated testing with CI/CD pipeline"
        ]
    }
    
    # Display categories
    for category, ideas in categories.items():
        with st.expander(f"{category} ({len(ideas)} ideas)"):
            for idea in ideas:
                st.markdown(f"""
                <div style="display: flex; align-items: start; margin: 10px 0; padding: 10px;
                            background: rgba(255, 255, 255, 0.05); border-radius: 8px;">
                    <div style="color: #667eea; margin-right: 10px;">•</div>
                    <div style="color: white;">{idea}</div>
                </div>
                """, unsafe_allow_html=True)
    
    # Voting system
    st.markdown("---")
    st.markdown("### 🗳️ Feature Voting")
    
    features = [
        "Real-time satellite integration",
        "Mobile application",
        "3D visualization",
        "Multi-language support",
        "Voice commands"
    ]
    
    col_vote1, col_vote2, col_vote3, col_vote4, col_vote5 = st.columns(5)
    vote_cols = [col_vote1, col_vote2, col_vote3, col_vote4, col_vote5]
    
    for i, feature in enumerate(features):
        with vote_cols[i]:
            if st.button(f"👍 {feature}", use_container_width=True):
                st.success(f"Voted for: {feature}")
    
    # Contribution section
    st.markdown("---")
    st.markdown("### 👨‍💻 Contribute")
    
    st.markdown("""
    <div style="background: rgba(102, 126, 234, 0.1); padding: 20px; border-radius: 10px;">
        <h4 style="color: #667eea;">Want to contribute?</h4>
        <p style="color: #b0b0b0;">
            This is an open-source project! You can:
        </p>
        <ul style="color: white;">
            <li>Report bugs and issues</li>
            <li>Suggest new features</li>
            <li>Contribute code improvements</li>
            <li>Improve documentation</li>
            <li>Share the project with others</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)