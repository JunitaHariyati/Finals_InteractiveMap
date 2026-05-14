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

st.title("Interactive GEE GeoTIFF Map")

# Create map
Map = geemap.Map(draw_ctrl=True)

# Load asset
asset_id = 'projects/tugasakhir-473409/assets/compositeFull_2025'
image = ee.Image(asset_id)

# Visualization
viz_params = {
    'bands': ['B4', 'B3', 'B2'],
    'min': 0,
    'max': 0.3
}

Map.addLayer(image, viz_params, 'Agats Composite')

# Center map
Map.centerObject(image, 11)

# Display map
Map.to_streamlit(height=700)