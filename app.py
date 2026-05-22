import ee
import streamlit as st
import geemap.foliumap as geemap

st.set_page_config(page_title="My Streamlit App", layout="wide")

# Initialize Earth Engine
try:
    ee.Initialize(project="ee-junitahariyati0717")
except Exception:
    ee.Authenticate()
    ee.Initialize(project="ee-junitahariyati0717")

st.markdown("""
<style>

/* Hide default multipage navigation */
[data-testid="stSidebarNav"] {
    display: none;
}

</style>
""", unsafe_allow_html=True)

# --- Pages ---
home = st.Page("pages/Home.py", title="Home", default=True)
coffee = st.Page("pages/LSA/Kopi_Liberika.py", title="Kopi")
avocado = st.Page("pages/LSA/Alpukat.py", title="Alpukat")

# --- Navigation Bar ---
with st.sidebar:

    st.markdown("### Halaman Utama")
    st.page_link(home)

    st.markdown("### Analisis Kesesuaian Wilayah")
    st.page_link(coffee)
    st.page_link(avocado)

# Router
pg = st.navigation([home, coffee, avocado])

pg.run()