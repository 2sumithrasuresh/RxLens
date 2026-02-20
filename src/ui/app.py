import streamlit as st
import streamlit.components.v1 as components
from streamlit_extras.metric_cards import style_metric_cards
import time
import os
import sys
import pandas as pd
import requests
from typing import Dict, Optional

st.set_page_config(layout="wide", page_title="RxLens")

# API Configuration
API_BASE_URL = os.getenv('API_URL', 'http://127.0.0.1:5000')
API_TIMEOUT = 30

# Get the directory of the current script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

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
    """Apply professional dark or light theme CSS"""
    if is_dark:
        dark_css = """
        <style>
        /* Main background */
        .stApp {
            background-color: #0f1419 !important;
            color: #e1e4e8 !important;
        }
        
        /* Text elements */
        p, span, div {
            color: #e1e4e8 !important;
        }
        
        /* Headers */
        h1, h2, h3, h4, h5, h6 {
            color: #f0f6fc !important;
        }
        
        /* Metric cards - professional blue accent */
        [data-testid="stMetric"] {
            background: linear-gradient(135deg, #161b22 0%, #0d1117 100%) !important;
            border: 1px solid #30363d !important;
            border-left: 4px solid #1f6feb !important;
            border-radius: 8px !important;
        }
        
        [data-testid="stMetricLabel"] {
            color: #c9d1d9 !important;
        }
        
        [data-testid="stMetricValue"] {
            color: #58a6ff !important;
        }
        
        /* Buttons */
        [data-testid="stButton"] > button {
            background-color: #238636 !important;
            border: 1px solid #238636 !important;
            color: #f0f6fc !important;
            font-weight: 600 !important;
        }
        
        [data-testid="stButton"] > button:hover {
            background-color: #2ea043 !important;
            border-color: #2ea043 !important;
        }
        
        /* Data frames */
        [data-testid="stDataFrame"] {
            background-color: #0d1117 !important;
        }
        
        /* DataFrame text */
        [data-testid="stDataFrame"] th {
            background-color: #161b22 !important;
            color: #58a6ff !important;
            font-weight: 600 !important;
        }
        
        [data-testid="stDataFrame"] td {
            color: #c9d1d9 !important;
            border-color: #30363d !important;
        }
        
        /* Input fields */
        input, textarea, [data-testid="stTextArea"] {
            background-color: #0d1117 !important;
            color: #e1e4e8 !important;
            border: 1px solid #30363d !important;
        }
        
        /* Divider */
        hr {
            border-color: #30363d !important;
        }
        
        /* Expanders */
        [data-testid="stExpander"] {
            border: 1px solid #30363d !important;
        }
        
        /* Success/Info/Warning boxes */
        [data-testid="stSuccess"], [data-testid="stInfo"], 
        [data-testid="stWarning"], [data-testid="stError"] {
            background-color: #161b22 !important;
            border-left: 4px solid #58a6ff !important;
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #0d1117 !important;
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

col_logo, col_nav, col_user = st.columns([2, 4, 2])

with col_logo:
    logo_path = os.path.join(SCRIPT_DIR, "assets/logo.png")
    st.image(logo_path)
    
st.write("\n")
with col_user:
    # Dark mode toggle button in top right
    c1, c2 = st.columns([0.3, 1.7])
    with c1:
        theme_icon = "🌙" if not st.session_state.dark_mode else "☀️"
        if st.button(theme_icon, key="theme_toggle", help="Toggle Dark/Light Mode"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()
    with c2:
        st.markdown('<p class="user-profile">User </p>', unsafe_allow_html=True)

if 'analyzed' not in st.session_state:
    st.session_state.analyzed = False
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None


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