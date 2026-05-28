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
avocado = st.Page("pages/LSA/Alpukat.py", title="Alpukat")
cashew = st.Page("pages/LSA/Cashew.py", title="Kacang Mete")
citrus = st.Page("pages/LSA/Citrus.py", title="Jeruk")
cocoa = st.Page("pages/LSA/Cocoa.py", title="Kakao")
coconut = st.Page("pages/LSA/Coconut.py", title="Kelapa")
durian = st.Page("pages/LSA/Durian.py", title="Durian")
coffee = st.Page("pages/LSA/Kopi_Liberika.py", title="Kopi Liberika")

# --- Navigation Bar ---
with st.sidebar:

    st.markdown("### Halaman Utama")
    st.page_link(home)

    st.markdown("### Analisis Kesesuaian Wilayah")
    st.page_link(coffee)
    st.page_link(avocado)
    st.page_link(durian)
    st.page_link(cocoa)
    st.page_link(cashew)
    st.page_link(citrus)
    st.page_link(coconut)

# Router
pg = st.navigation([home, coffee, avocado, durian, cocoa, cashew, citrus, coconut])

pg.run()