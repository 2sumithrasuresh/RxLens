import streamlit as st

st.set_page_config(page_title="RxLens draft", layout="wide")

st.title("💊 RxLens ")
st.caption("Prescription Analysis")

st.divider()

col1, col2 = st.columns([1, 1])

with col1:
    st.header("Input Prescription", help="enter text or image")
    #st.info("Enter details (Text or Image)")
    
    
    #INPUT
    med_input = st.multiselect(
        "Enter Medicines:", 
        ["Medicine A", "Medicine B", "Medicine C"], 
        help="from DB"
    )
    
    st.button("Analyze Prescription", type="primary")

with col2:
    st.header("Analysis Results")
    #OUTPUT
    if not med_input:
        st.write("Results will appear here")
    else:
        st.warning("Checking for Salt Duplicates...")
        st.subheader("Composition Breakdown")
        st.table({"Medicine": med_input, "Salts": ["Salt X, Salt Y", "Pending...", "Pending..."]})

#SIDEBAR
with st.sidebar:
    st.title("Settings & Tools")
    st.radio("Mode", ["Manual Entry", "OCR Scanner"])
    st.divider()
    