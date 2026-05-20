import ee
import streamlit as st
import geemap.foliumap as geemap
import pandas as pd
import plotly.express as px
import folium
import math

from streamlit_folium import st_folium

# Initialize Earth Engine
try:
    ee.Initialize(project="ee-junitahariyati0717")
except Exception:
    ee.Authenticate()
    ee.Initialize(project="ee-junitahariyati0717")

# Assets ID
ASSETS = "projects/tugasakhir-473409/assets/"

# Map Config
MAP_HEIGHT = 700
DEFAULT_BASEMAP = "SATELLITE"

# Class Options
CLASS_OPTIONS = {
    "Semua Kelas": 0,
    "S1 - Sangat Sesuai": 4,
    "S2 - Cukup Sesuai": 3,
    "S3 - Sesuai Marginal": 2,
    "N - Tidak sesuai": 1
}

# Class Visualization
CLASS_VIS = {
    'min': 1,
    'max': 4,
    'palette': [
        '#E24B4A',
        '#EF9F27',
        '#97C459',
        '#1D9E75'
    ],
    "opacity": 0.7
}

SINGLE_CLASS_PALETTE = {
    1: ["#E24B4A"],
    2: ["#EF9F27"],
    3: ["#97C459"],
    4: ["#1D9E75"]
}

# Legend
LEGEND_DICT = {
    "S1 - Sangat Sesuai": "#1D9E75",
    "S2 - Cukup Sesuai": "#97C459",
    "S3 - Sesuai Marginal": "#EF9F27",
    "N - Tidak Sesuai": "#E24B4A"
}