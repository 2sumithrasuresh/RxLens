import streamlit as st
import streamlit.components.v1 as components
from streamlit_extras.metric_cards import style_metric_cards
import time
import os
import sys
import pandas as pd
import requests
from typing import Dict, Optional

# Add src to python path to allow imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from ml.chat import RxLensChatbot

st.set_page_config(layout="wide", page_title="RxLens")

# API Configuration
API_BASE_URL = os.getenv('API_URL', 'http://127.0.0.1:5000')
API_TIMEOUT = 30

# Get the directory of the current script
# SCRIPT_DIR is already defined above

# Data paths
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(SCRIPT_DIR)), 'data', 'refined')
MEDICINES_CSV = os.path.join(DATA_DIR, 'jan_aushadhi_medicines.csv')
COMPOSITION_CSV = os.path.join(DATA_DIR, 'jan_aushadhi_composition.csv')

@st.cache_resource
def api_health_check():
    """Check if backend API is running"""
    try:
        response = requests.get(f'{API_BASE_URL}/api/health', timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"API health check failed: {e}")
        return False


def analyze_prescription_api(medicines_list: list, top_k: int = 5) -> Dict:
    """
    Analyze prescription by calling the backend API
    
    Args:
        medicines_list: List of medicine names
        top_k: Number of top alternatives to return
    
    Returns:
        Dictionary with analysis results
    """
    try:
        response = requests.post(
            f'{API_BASE_URL}/api/analyze-prescription',
            json={'medicines': medicines_list, 'top_k': top_k},
            timeout=API_TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': f'API Error: {str(e)}. Make sure the backend server is running on {API_BASE_URL}'
        }

def local_css(file_name):
    file_path = os.path.join(SCRIPT_DIR, file_name)
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def scroll_to(anchor_id):
    components.html(f"""
        <script>
            var element = window.parent.document.getElementById("{anchor_id}");
            if (element) {{
                element.scrollIntoView({{behavior: "smooth", block: "start"}});
            }}
        </script>
    """, height=0)

def apply_theme_css(is_dark: bool):
    """Apply professional dark or light theme CSS over the base style.css"""
    if is_dark:
        dark_css = """
        <style>
        /* Main background - Deep premium dark */
        .stApp {
            background: linear-gradient(135deg, #090c10 0%, #161b22 100%) !important;
            color: #f0f6fc !important;
        }
        
        /* Text overrides */
        p, span, div, label {
            color: #c9d1d9 !important;
        }
        
        h1, h2, h3, h4, th {
            color: #ffffff !important;
        }

        /* Logo text glow in dark mode */
        .logo-text {
            background: linear-gradient(135deg, #58a6ff, #a371f7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 20px rgba(88, 166, 255, 0.3);
        }
        
        /* Metric cards - Glassmorphism Dark */
        div[data-testid="stMetric"] {
            background: rgba(22, 27, 34, 0.6) !important;
            backdrop-filter: blur(16px) !important;
            -webkit-backdrop-filter: blur(16px) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-left: 5px solid #58a6ff !important;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4) !important;
        }
        
        div[data-testid="stMetric"]:hover {
            box-shadow: 0 15px 35px rgba(88, 166, 255, 0.15) !important;
        }
        
        [data-testid="stMetricLabel"] p {
            color: #8b949e !important;
        }
        
        [data-testid="stMetricValue"] > div {
            color: #ffffff !important;
        }
        
        /* Inputs & Textareas Dark */
        .stTextArea textarea, [data-testid="stChatInput"] textarea, input {
            background: rgba(13, 17, 23, 0.8) !important;
            color: #f0f6fc !important;
            border: 1px solid #30363d !important;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.2) !important;
        }
        
        .stTextArea textarea:focus, [data-testid="stChatInput"] textarea:focus {
            border-color: #58a6ff !important;
            box-shadow: 0 0 0 4px rgba(88, 166, 255, 0.15) !important;
        }
        
        /* Buttons Dark */
        div.stButton > button {
            background: linear-gradient(135deg, #1f6feb 0%, #388bfd 100%) !important;
            box-shadow: 0 4px 14px rgba(31, 111, 235, 0.4) !important;
        }
        
        button[kind="secondary"] {
            background: rgba(33, 38, 45, 0.8) !important;
            color: #c9d1d9 !important;
            border: 1px solid #30363d !important;
            box-shadow: 0 2px 5px rgba(0,0,0,0.3) !important;
        }
        button[kind="secondary"]:hover {
            background: #30363d !important;
            border-color: #8b949e !important;
        }
        
        /* Data frames Dark */
        [data-testid="stDataFrame"] {
            background-color: #0d1117 !important;
            border-color: #30363d !important;
        }
        
        [data-testid="stDataFrame"] th {
            background-color: #161b22 !important;
            color: #58a6ff !important;
        }
        
        [data-testid="stDataFrame"] td {
            color: #c9d1d9 !important;
            border-color: #30363d !important;
        }
        
        /* Expanders & Dividers Dark */
        [data-testid="stExpander"] {
            background: rgba(22, 27, 34, 0.5) !important;
            border-color: #30363d !important;
        }
        hr {
            border-color: #30363d !important;
        }
        
        /* Sidebar Dark */
        [data-testid="stSidebar"] {
            background-color: #0d1117 !important;
            border-right: 1px solid #30363d !important;
        }
        
        /* Chat UI components Dark */
        [data-testid="stChatMessage"] {
            background: rgba(22, 27, 34, 0.7) !important;
            backdrop-filter: blur(10px) !important;
            border: 1px solid #30363d !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
        }
        
        [data-testid="stChatMessage"] p {
            color: #e1e4e8 !important;
        }
        </style>
        """
        st.markdown(dark_css, unsafe_allow_html=True)

local_css("style.css")

# Initialize theme state
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# Apply theme
apply_theme_css(st.session_state.dark_mode)

col_logo, col_nav, col_user = st.columns([2, 3.5, 1.5], gap="large")

with col_logo:
    logo_path = os.path.join(SCRIPT_DIR, "assets/logo.png")
    st.image(logo_path, width=220)
    
with col_user:
    st.write("") # Add a tiny bit of vertical spacing
    theme_text = "🌙 Dark Mode" if not st.session_state.dark_mode else "☀️ Light Mode"
    if st.button(theme_text, key="theme_toggle", use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

if 'analyzed' not in st.session_state:
    st.session_state.analyzed = False
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'chatbot' not in st.session_state:
    st.session_state.chatbot = RxLensChatbot()


st.markdown('<p class = "head-text">Enter prescription</p>', unsafe_allow_html=True)
prescription_list = st.text_area(label="Enter Prescription List",label_visibility="collapsed", placeholder="Enter medicine names (one per line)\nExample:\nParacetamol\nAspirin\nIbuprofen")

col_btn1, col_btn2 = st.columns([1, 0.125]) 

with col_btn1:
    if st.button("Analyze Prescription"):
        # Check if API is running
        if not api_health_check():
            st.error(f"⚠️ Backend API is not running. Please start the backend server at {API_BASE_URL}")
            st.info("To start the backend server, run: python src/core/api.py")
        else:
            with st.spinner('Analyzing your prescription...'):
                prescription_lines = [line.strip() for line in prescription_list.strip().split('\n') if line.strip()]
                
                # Call API to analyze prescription
                api_response = analyze_prescription_api(prescription_lines, top_k=5)
                
                if api_response.get('success'):
                    st.session_state.analysis_results = api_response['results']
                    st.session_state.analyzed = True
                else:
                    st.error(f"Error analyzing prescription: {api_response.get('error', 'Unknown error')}")
                    st.session_state.analyzed = False
            

with col_btn2:
    if st.session_state.analyzed:
        if st.button("Clear Results"):
            st.session_state.analyzed = False
            st.rerun()


if st.session_state.analyzed and st.session_state.analysis_results:
    results = st.session_state.analysis_results
    
    # Count from API response if available, otherwise calculate
    found_medicines = {k: v for k, v in results.items() if v.get('status') == 'found'}
    not_found_medicines = {k: v for k, v in results.items() if v.get('status') == 'not_found'}
    
    successful_medicines = len(found_medicines)
    total_alternatives = sum(len(v.get('substitutes', [])) for v in found_medicines.values())
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Medicines Analyzed", successful_medicines)
        if st.button("View Details", key="view_branded"):
            scroll_to("branded-section")

    with col2:
        st.metric("Active Alternatives", total_alternatives)
        if st.button("View Alternatives", key="view_ingredients"):
            scroll_to("generics-section")

    with col3:
        st.metric("Not Found", len(not_found_medicines))
        if st.button("View Issues", key="view_issues"):
            scroll_to("issues-section")
    
    style_metric_cards(border_left_color="#007bff")

    st.write("\n" * 10) 

    # Branded Drugs Details
    st.markdown('<div id="branded-section"></div>', unsafe_allow_html=True)
    st.header("Input Medicines Details", anchor="branded-section")
    
    for med_name, result in found_medicines.items():
        if result['status'] == 'found':
            med = result['original_medicine']
            match_similarity = result.get('similarity_score', 100)
            st.subheader(f"💊 {med_name} (Matched: {med['name']})")
            st.caption(f"Match Similarity: {match_similarity}%")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Medicine ID", med['medicine_id'])
            with col2:
                st.metric("Price (MRP)", f"₹{med['price']:.2f}")
            with col3:
                st.metric("Category", med['category'])
            with col4:
                st.metric("Group", med['group_name'])
            
            # Show composition
            if med['composition']:
                st.write("**Composition:**")
                comp_data = []
                for c in med['composition']:
                    comp_data.append({
                        'Drug ID': c['drug_id'],
                        'Amount': c['amount'],
                        'Unit': c['unit']
                    })
                st.dataframe(pd.DataFrame(comp_data))
            st.divider()

    # Generic/Alternative Medicines
    st.write("\n" * 10)
    st.markdown('<div id="generics-section"></div>', unsafe_allow_html=True)
    st.header("Generic & Alternative Medicines", anchor="generics-section")
    
    for med_name, result in found_medicines.items():
        if result['status'] == 'found' and result.get('substitutes'):
            st.subheader(f"Alternatives for {med_name}")
            
            alt_data = []
            for sub in result['substitutes']:
                alt_data.append({
                    'Medicine Name': sub['medicine']['name'],
                    'ID': sub['medicine']['medicine_id'],
                    'Price': f"₹{sub['medicine']['price']:.2f}",
                    'Similarity': f"{sub['comp_similarity']:.1%}",
                    'Overall Score': f"{sub['score']:.3f}",
                    'Category': sub['medicine']['category']
                })
            
            st.dataframe(pd.DataFrame(alt_data), use_container_width=True)
            
            # Show details of top alternative
            if result['substitutes']:
                top_alt = result['substitutes'][0]
                with st.expander(f"ℹ️ Details of {top_alt['medicine']['name']} (Top Match)"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Price:** ₹{top_alt['medicine']['price']:.2f}")
                        st.write(f"**Group:** {top_alt['medicine']['group_name']}")
                    with col2:
                        st.write(f"**Composition Match:** {top_alt['comp_similarity']:.1%}")
                        st.write(f"**Price Score:** {top_alt['price_score']:.3f}")
                    
                    if top_alt['medicine']['composition']:
                        st.write("**Composition:**")
                        comp_data = []
                        for c in top_alt['medicine']['composition']:
                            comp_data.append({
                                'Drug ID': c['drug_id'],
                                'Amount': c['amount'],
                                'Unit': c['unit']
                            })
                        st.dataframe(pd.DataFrame(comp_data))
            st.divider()
    
    # Issues
    if not_found_medicines:
        st.write("\n" * 10)
        st.markdown('<div id="issues-section"></div>', unsafe_allow_html=True)
        st.header("Not Found", anchor="issues-section")
        for med_name, result in not_found_medicines.items():
            st.warning(f"**{med_name}**: {result.get('error', 'Unknown error')}")

    st.write("\n" * 10)
    st.divider()

    # --- Chatbot UI ---
    st.markdown('<div id="chatbot-section"></div>', unsafe_allow_html=True)
    st.header("Explanation Engine", anchor="chatbot-section")
    st.write("Ask me anything about your medicines or health conditions.")

    chat_container = st.container()
    
    # Display chat history (limit to last 10 messages for UI brevity if desired, but here we show all)
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask about side effects, interactions, or ingredients..."):
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Add to session history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.chatbot.generate_response(prompt)
                st.markdown(response)
                
        # Add to session history
        st.session_state.messages.append({"role": "assistant", "content": response})