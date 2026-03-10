import streamlit as st
import streamlit.components.v1 as components
from streamlit_extras.metric_cards import style_metric_cards
import time
import sys
import os

# Add src to python path to allow imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from ml.chat import RxLensChatbot
from ml.model import MedicineMatcher

st.set_page_config(layout="wide", page_title="RxLens")

def local_css(file_name):
    with open(file_name) as f:
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


local_css(os.path.join(os.path.dirname(__file__), "style.css"))

@st.cache_resource
def load_model():
    model_path = os.path.join(os.path.dirname(__file__), '..', 'ml', 'medicine_matcher.pkl')
    if os.path.exists(model_path):
        return MedicineMatcher.load(model_path)
    return None

matcher = load_model()

# Header Layout
col_logo, col_space, col_user = st.columns([2, 5, 2])
with col_logo:
    st.image(os.path.join(os.path.dirname(__file__), "assets/logo.png"), width=200)

with col_user:
    st.markdown('<p class="user-profile">Hello, User 👋</p>', unsafe_allow_html=True)
    
st.divider()

if 'analyzed' not in st.session_state:
    st.session_state.analyzed = False
    
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = []

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'chatbot' not in st.session_state:
    st.session_state.chatbot = RxLensChatbot()


st.markdown('<p class="head-text">Upload Prescription List</p>', unsafe_allow_html=True)
prescription_list = st.text_area(label="Enter Prescription List (Each medicine on a new line)",label_visibility="collapsed", height=150)

col_btn1, col_btn2 = st.columns([1.5, 8.5]) 
with col_btn1:
    if st.button("🔍 Analyze Prescription", use_container_width=True):
        if not prescription_list.strip():
            st.warning("Please enter at least one medicine.")
        elif matcher is None:
            st.error("ML Model not found. Please train and save the model first.")
        else:
            with st.spinner('Analyzing your prescription using AI...'):
                queries = [q.strip() for q in prescription_list.split('\n') if q.strip()]
                results = []
                for query in queries:
                    matches, branded_info = matcher.find_matches(query, top_k=3)
                    results.append({
                        'query': query,
                        'matches': matches,
                        'branded_info': branded_info
                    })
                st.session_state.analysis_results = results
                st.session_state.analyzed = True

with col_btn2:
    if st.session_state.analyzed:
        if st.button("🗑️ Clear Results", use_container_width=False):
            st.session_state.analyzed = False
            st.session_state.analysis_results = []
            st.rerun()

st.write("") # small gap

if st.session_state.analyzed:
    results = st.session_state.analysis_results
    total_drugs = len(results)
    
    # Calculate unique ingredients
    unique_ingredients = set()
    total_alternatives = 0
    
    for res in results:
        total_alternatives += len(res['matches'])
        if res['branded_info']:
            comp = res['branded_info'].get('composition', '')
            ingredients = [i.strip() for i in comp.split('+') if i.strip()]
            unique_ingredients.update(ingredients)
        elif not res['matches'].empty:
            comp = res['matches'].iloc[0].get('composition', '')
            ingredients = [i.strip() for i in comp.split('+') if i.strip()]
            unique_ingredients.update(ingredients)

    st.markdown("### Summary Metrics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Drugs Analyzed", str(total_drugs))

    with col2:
        st.metric("Estimated Active Ingredients", str(len(unique_ingredients)))

    with col3:
        st.metric("Generic Alternatives Found", str(total_alternatives))

    st.write("") 
    st.markdown('<div id="alternatives-section"></div>', unsafe_allow_html=True)
    st.header("🧬 Drug Analysis Breakdown", anchor="branded-section")
    
    for res in results:
        with st.expander(f"Analysis for: {res['query']}", expanded=True):
            if res['branded_info']:
                st.info(f"**Direct Brand Match:** {res['branded_info']['medicine_name']}  \n**Composition:** {res['branded_info']['composition']}")
            else:
                 st.info(f"Could not find exact brand match. Searching generics directly via text similarity.")
            
            if res['matches'].empty:
                st.warning("No generic alternatives found.")
            else:
                st.success(f"Discovered **{len(res['matches'])}** potentially cheaper Jan Aushadhi Generic Alternative(s):")
                match_df = res['matches'][['medicine_name', 'mrp', 'unit_size', 'similarity_score']]
                match_df.rename(columns={'medicine_name': 'Generic Name', 'mrp': 'MRP (₹)', 'unit_size': 'Unit', 'similarity_score': 'Match Score'}, inplace=True)
                st.dataframe(match_df, hide_index=True, use_container_width=True)

    st.divider()

    # --- Chatbot UI ---
    st.markdown('<div id="chatbot-section"></div>', unsafe_allow_html=True)
    st.header("🤖 Explanation Engine", anchor="chatbot-section")
    st.markdown("Have questions about your prescription or side effects? Ask the Clinical AI!")
    
    st.write("")

    chat_container = st.container(border=True)
    
    # Display chat history
    with chat_container:
        if not st.session_state.messages:
             st.caption("Chat history will appear here...")
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("E.g., What are the side effects of Paracetamol?"):
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Add to session history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing medical context..."):
                response = st.session_state.chatbot.generate_response(prompt)
                st.markdown(response)
                
        # Add to session history
        st.session_state.messages.append({"role": "assistant", "content": response})