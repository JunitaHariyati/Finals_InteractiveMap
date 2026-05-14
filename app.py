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

# --- Pages ---
home = st.Page("pages/Home.py", title="Home", default=True)
coffee = st.Page("pages/LSA/Kopi_Liberika.py", title="Kopi")
avocado = st.Page("pages/LSA/Alpukat.py", title="Alpukat")

# --- Navigation Bar ---
pg = st.navigation(
        {
            "Halaman Utama": [home],
            "Analisis Kesesuaian Wilayah": [coffee, avocado]
        }
)

pg.run()