"""
Streamlit Dashboard for Veterinary AI Application
"""

import streamlit as st
import asyncio
from datetime import datetime
from typing import Optional
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def init_backend_components():
    """Lazy initialization of backend components."""
    try:
        from backend.ai_engine import AIEngine
        from backend.database import DatabaseManager
        from backend.cache import CacheManager
        from config.settings import settings
        
        return {
            'AIEngine': AIEngine,
            'DatabaseManager': DatabaseManager,
            'CacheManager': CacheManager,
            'settings': settings
        }
    except Exception as e:
        st.error(f"Failed to initialize backend components: {e}")
        return None


def init_session_state():
    """Initialize Streamlit session state variables."""
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'backend_components' not in st.session_state:
        st.session_state.backend_components = init_backend_components()
    
    # Initialize components lazily
    if st.session_state.backend_components:
        components = st.session_state.backend_components
        
        if 'ai_engine' not in st.session_state:
            try:
                st.session_state.ai_engine = components['AIEngine']()
            except Exception as e:
                st.session_state.ai_engine = None
        
        if 'db_manager' not in st.session_state:
            try:
                st.session_state.db_manager = components['DatabaseManager']()
            except Exception as e:
                st.session_state.db_manager = None
        
        if 'cache_manager' not in st.session_state:
            try:
                st.session_state.cache_manager = components['CacheManager']()
            except Exception as e:
                st.session_state.cache_manager = None
        
        if 'settings' not in st.session_state:
            st.session_state.settings = components['settings']


def render_header():
    """Render the dashboard header."""
    col1, col2, col3 = st.columns([2, 3, 1])
    
    with col1:
        st.title("🏥 VetAI Dashboard")
    
    with col2:
        if hasattr(st.session_state, 'settings'):
            st.markdown(f"**Version:** {st.session_state.settings.APP_VERSION}")
        else:
            st.markdown("**Version:** 2.0.0")
    
    with col3:
        if st.session_state.user:
            st.write(f"👤 {st.session_state.user.get('username', 'User')}")


def render_sidebar():
    """Render the sidebar navigation."""
    st.sidebar.title("Navigation")
    
    pages = {
        "🏠 Home": "home",
        "🔬 New Diagnosis": "diagnosis",
        "📊 Analytics": "analytics",
        "🗂️ Patient Records": "records",
        "⚙️ Settings": "settings",
        "📚 Help": "help",
    }
    
    selected = st.sidebar.radio("Go to", list(pages.keys()))
    
    # System status
    st.sidebar.markdown("---")
    st.sidebar.subheader("System Status")
    
    # Check system health
    db_healthy = False
    cache_healthy = False
    
    if hasattr(st.session_state, 'db_manager') and st.session_state.db_manager:
        try:
            db_healthy = st.session_state.db_manager.health_check()
        except:
            pass
    
    if hasattr(st.session_state, 'cache_manager') and st.session_state.cache_manager:
        try:
            cache_healthy = st.session_state.cache_manager.health_check()
        except:
            pass
    
    st.sidebar.write(f"🗄️ Database: {'✅' if db_healthy else '❌'}")
    st.sidebar.write(f"💾 Cache: {'✅' if cache_healthy else '❌'}")
    
    return pages[selected]


def render_home_page():
    """Render the home page."""
    st.header("Welcome to VetAI")
    
    st.markdown("""
    ### 🎯 AI-Powered Veterinary Diagnostics
    
    VetAI provides advanced AI-powered diagnostic tools for veterinary medicine:
    
    - 📸 **Image Analysis**: X-rays, ultrasounds, dermatological images
    - 🎥 **Video Analysis**: Gait analysis, behavior assessment, movement patterns
    - 🎵 **Audio Analysis**: Heart sounds, breathing patterns, vocalizations
    - 🧠 **Multi-modal AI**: Comprehensive diagnosis using multiple data sources
    """)
    
    # Quick stats
    st.subheader("📈 Quick Stats")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Diagnoses", "0", "+0")
    with col2:
        st.metric("Active Patients", "0", "+0")
    with col3:
        st.metric("AI Models", "4", "0")
    with col4:
        st.metric("Accuracy", "85%", "+2%")


def render_diagnosis_page():
    """Render the new diagnosis page."""
    st.header("🔬 New Diagnosis")
    
    # Patient information
    st.subheader("Patient Information")
    col1, col2 = st.columns(2)
    
    with col1:
        animal_name = st.text_input("Animal Name")
        species = st.selectbox("Species", ["Dog", "Cat", "Horse", "Bird", "Reptile", "Other"])
        age = st.number_input("Age (years)", min_value=0.0, max_value=50.0, step=0.1)
    
    with col2:
        breed = st.text_input("Breed")
        weight = st.number_input("Weight (kg)", min_value=0.0, max_value=1000.0, step=0.1)
        sex = st.selectbox("Sex", ["Male", "Female", "Unknown"])
    
    # Symptoms
    st.subheader("Symptoms & Observations")
    symptoms = st.text_area("Describe symptoms and observations", height=150)
    
    # Media upload
    st.subheader("Upload Media Files")
    
    tab1, tab2, tab3 = st.tabs(["📸 Images", "🎥 Videos", "🎵 Audio"])
    
    with tab1:
        image_files = st.file_uploader(
            "Upload images (X-rays, photos, etc.)",
            type=['jpg', 'jpeg', 'png', 'bmp'],
            accept_multiple_files=True
        )
    
    with tab2:
        video_files = st.file_uploader(
            "Upload videos (gait analysis, behavior)",
            type=['mp4', 'avi', 'mov'],
            accept_multiple_files=True
        )
    
    with tab3:
        audio_files = st.file_uploader(
            "Upload audio (heart sounds, breathing)",
            type=['wav', 'mp3', 'ogg'],
            accept_multiple_files=True
        )
    
    # Submit button
    if st.button("🚀 Start AI Analysis", type="primary"):
        if not animal_name or not species or not symptoms:
            st.error("Please fill in all required fields (Name, Species, Symptoms)")
        elif not (image_files or video_files or audio_files):
            st.error("Please upload at least one media file")
        else:
            with st.spinner("Processing with AI..."):
                st.success("Analysis started! (Demo mode - full implementation pending)")
                st.info("In production, this would analyze the uploaded media using AI models")


def render_analytics_page():
    """Render the analytics page."""
    st.header("📊 Analytics")
    
    st.info("Analytics dashboard coming soon!")
    
    # Placeholder metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Diagnosis Trends")
        st.line_chart({"Diagnoses": [10, 15, 13, 17, 20, 25, 23]})
    
    with col2:
        st.subheader("Common Conditions")
        st.bar_chart({"Count": [5, 8, 3, 12, 7]})


def render_records_page():
    """Render the patient records page."""
    st.header("🗂️ Patient Records")
    
    st.info("Patient records management coming soon!")
    
    # Search
    search = st.text_input("🔍 Search patients", placeholder="Enter name, ID, or species")
    
    # Placeholder table
    if search:
        st.write("Search results will appear here")
    else:
        st.write("No patients found. Create a new diagnosis to add patients.")


def render_settings_page():
    """Render the settings page."""
    st.header("⚙️ Settings")
    
    tab1, tab2, tab3 = st.tabs(["General", "AI Models", "System"])
    
    with tab1:
        st.subheader("General Settings")
        theme = st.selectbox("Theme", ["Light", "Dark", "Auto"])
        language = st.selectbox("Language", ["English", "Spanish", "French"])
    
    with tab2:
        st.subheader("AI Model Configuration")
        
        # Get current model status
        if hasattr(st.session_state, 'ai_engine') and st.session_state.ai_engine:
            try:
                model_status = st.session_state.ai_engine.get_model_status()
                st.json(model_status)
            except Exception as e:
                st.error(f"Failed to get model status: {e}")
        else:
            st.info("AI Engine not initialized")
    
    with tab3:
        st.subheader("System Information")
        
        col1, col2 = st.columns(2)
        with col1:
            if hasattr(st.session_state, 'settings'):
                st.write("**Application Version:**", st.session_state.settings.APP_VERSION)
                st.write("**Environment:**", st.session_state.settings.ENVIRONMENT)
            else:
                st.write("**Application Version:**", "2.0.0")
                st.write("**Environment:**", "Unknown")
        
        with col2:
            if hasattr(st.session_state, 'cache_manager') and st.session_state.cache_manager:
                try:
                    cache_stats = st.session_state.cache_manager.get_stats()
                    st.write("**Cache Status:**", "✅ Enabled" if cache_stats.get("enabled") else "❌ Disabled")
                except:
                    st.write("**Cache Status:**", "❌ Error")
            else:
                st.write("**Cache Status:**", "❌ Not initialized")


def render_help_page():
    """Render the help page."""
    st.header("📚 Help & Documentation")
    
    st.markdown("""
    ### Getting Started
    
    1. **Create a new diagnosis**: Go to "New Diagnosis" and fill in patient information
    2. **Upload media**: Add images, videos, or audio files for AI analysis
    3. **Review results**: AI will analyze the media and provide diagnostic insights
    4. **Save and track**: All diagnoses are saved for future reference
    
    ### Supported Media Types
    
    - **Images**: X-rays, ultrasounds, dermatological photos (.jpg, .png)
    - **Videos**: Gait analysis, behavior videos (.mp4, .avi, .mov)
    - **Audio**: Heart sounds, breathing, vocalizations (.wav, .mp3)
    
    ### Contact Support
    
    For technical support, please contact: support@vetai.example.com
    """)


def main():
    """Main application function."""
    # Page config
    st.set_page_config(
        page_title="VetAI Dashboard",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    init_session_state()
    
    # Render header
    render_header()
    
    # Render sidebar and get selected page
    current_page = render_sidebar()
    
    # Render the selected page
    if current_page == "home":
        render_home_page()
    elif current_page == "diagnosis":
        render_diagnosis_page()
    elif current_page == "analytics":
        render_analytics_page()
    elif current_page == "records":
        render_records_page()
    elif current_page == "settings":
        render_settings_page()
    elif current_page == "help":
        render_help_page()


if __name__ == "__main__":
    main()
