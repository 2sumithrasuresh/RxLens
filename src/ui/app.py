import streamlit as st
import streamlit.components.v1 as components
from streamlit_extras.metric_cards import style_metric_cards
import time
import sys
import os

# Add src to python path to allow imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from ml.chat import RxLensChatbot

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


local_css("style.css")

col_logo, col_nav, col_user = st.columns([2, 4, 2])

with col_logo:
    st.image("assets/logo.png")
    
st.write("\n")
with col_user:
    st.markdown('<p class="user-profile">User </p>', unsafe_allow_html=True)

if 'analyzed' not in st.session_state:
    st.session_state.analyzed = False

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'chatbot' not in st.session_state:
    st.session_state.chatbot = RxLensChatbot()


st.markdown('<p class = "head-text">Enter prescription</p>', unsafe_allow_html=True)
prescription_list = st.text_area(label="Enter Prescription List",label_visibility="collapsed",)

col_btn1, col_btn2 = st.columns([1, 0.125]) 

with col_btn1:
    if st.button("Analyze Prescription"):
        with st.spinner('Analyzing your prescription...'):
            time.sleep(2)
            st.session_state.analyzed = True
            

with col_btn2:
    if st.session_state.analyzed:
        if st.button("Clear Results"):
            st.session_state.analyzed = False
            st.rerun()


if st.session_state.analyzed:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Branded Drugs Analyzed", "4")
        if st.button("View Branded Details", key="view_branded"):
            scroll_to("branded-section")

    with col2:
        st.metric("Unique Active Ingredients", "2")
        if st.button("View Ingredient Details", key="view_ingredients"):
            scroll_to("ingredients-section")

    with col3:
        st.metric("Generic Alternatives Found", "3")
        if st.button("View Generic Details", key="view_generics"):
            scroll_to("generics-section")
    style_metric_cards(border_left_color="#007bff")

    st.write("\n" * 10) 


    st.markdown('<div id="alternatives-section"></div>', unsafe_allow_html=True)
    st.header("Drug analysis", anchor="branded-section")
    st.write("<breakdown of branded drugs>")

    st.write("\n" * 20)

    st.markdown('<div id="ingredients-section"></div>', unsafe_allow_html=True)
    st.header("Active Ingredients", anchor="ingredients-section")
    st.write("<breakdown of ingredients>")

    st.write("\n" * 20) 

    st.markdown('<div id="generics-section"></div>', unsafe_allow_html=True)
    st.header("Generic Alternatives", anchor="generics-section")
    st.write("<generic alternatives>")
    
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