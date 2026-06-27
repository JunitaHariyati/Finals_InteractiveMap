import ee
import streamlit as st
import geemap.foliumap as geemap
import pandas as pd
import plotly.express as px
import folium
import math
from streamlit_folium import st_folium

# INITIALIZE EARTH ENGINE
try:
    ee.Initialize(project="ee-junitahariyati0717")
except Exception:
    ee.Authenticate()
    ee.Initialize(project="ee-junitahariyati0717")

# ASSET ID
ASSETS = "projects/tugasakhir-473409/assets/"

# FUNCTION TO LOAD CSS
def load_css(path="utils/style.css"):
    with open(path, encoding="utf-8") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )

# ALL LAND COVER ASSETS
LC_ASSET_BY_YEAR = {
    2020: ASSETS + "LC_2020",
    2021: ASSETS + "LC_2021",
    2022: ASSETS + "LC_2022",
    2023: ASSETS + "LC_2023",
    2024: ASSETS + "LC_2024",
    2025: ASSETS + "LC_2025", 
}

# LAND COVER VISUALIZATION
LC_COLOR = {
    "Hutan": "#228B22",                  
    "Vegetasi Tergenang": "#00CED1",     
    "Pertanian": "#FFD700",                
    "Lahan Terbuka": "#A0522D",          
    "Padang Rumput": "#ADFF2F",          
    "Wilayah Terbangun": "#DC143C",      
    "Badan Air": "#1E90FF",              
}

# BAR CHART COLOR
LC_COLOR_DARK = {
    "Hutan": "#1b5e20",
    "Vegetasi Tergenang": "#00695c",
    "Pertanian": "#ef6c00",
    "Lahan Terbuka": "#6d4c41",
    "Padang Rumput": "#827717",
    "Wilayah Terbangun": "#b71c1c",
    "Badan Air": "#1565c0",
}

LC_COLOR_LIGHT = {
    "Hutan": "#66bb6a",
    "Vegetasi Tergenang": "#4db6ac",
    "Pertanian": "#ffb74d",
    "Lahan Terbuka": "#bcaaa4",
    "Padang Rumput": "#dce775",
    "Wilayah Terbangun": "#ef9a9a",
    "Badan Air": "#64b5f6",
}
 
LC_VIS = {
    "min":     1,
    "max":     7,
    "palette": ["228B22","00CED1","FFD700","A0522D","ADFF2F","DC143C","1E90FF"],
    "opacity": 0.85,
}
 
LC_LEGEND = {
    "Hutan":              "#228B22",
    "Vegetasi Tergenang": "#00CED1",
    "Pertanian":            "#FFD700",
    "Lahan Terbuka":      "#A0522D",
    "Padang Rumput":      "#ADFF2F",
    "Wilayah Terbangun":  "#DC143C",
    "Badan Air / Sungai": "#1E90FF",
}
 
LC_PIXEL_MAP = {
    1: "Hutan", 2: "Vegetasi Tergenang", 3: "Pertanian",
    4: "Lahan Terbuka", 5: "Padang Rumput", 6: "Wilayah Terbangun", 7: "Badan Air",
}

LC_LAYERS = {
    1: ("Hutan", "#228B22"),
    2: ("Vegetasi Tergenang", "#00CED1"),
    3: ("Pertanian", "#FFD700"),
    4: ("Lahan Terbuka", "#A0522D"),
    5: ("Padang Rumput", "#ADFF2F"),
    6: ("Wilayah Terbangun", "#DC143C"),
    7: ("Badan Air", "#1E90FF"),
}

 
# MAP CONFIG
MAP_HEIGHT = 700

# LAND SUITABILITY LAYERS
LSA_LAYERS = {
    4: ("S1 - Sangat Sesuai", "#1D9E75"),
    3: ("S2 - Cukup Sesuai", "#1976D2"),
    2: ("S3 - Sesuai Marginal", "#F9A825"),
    1: ("N - Tidak Sesuai", "#D32F2F"),
}

# LAND SUITABILITY CLASS 
CLASS_OPTIONS = {
    "Semua Kelas": 0,
    "S1 - Sangat Sesuai": 4,
    "S2 - Cukup Sesuai": 3,
    "S3 - Sesuai Marginal": 2,
    "N - Tidak sesuai": 1
}

VAL_TO_LABEL = {1: "N", 2: "S3", 3: "S2", 4: "S1"}

# LAND SUITABILITY VISUALIZATION
CLASS_VIS = {
    "min": 1,
    "max": 4,
    "palette": [
        "#D32F2F",  # N
        "#F9A825",  # S3
        "#1976D2",  # S2
        "#1D9E75"   # S1
    ],
    "opacity": 0.7
}

SINGLE_CLASS_PALETTE = {
    1: ["#D32F2F"],  # N
    2: ["#F9A825"],  # S3
    3: ["#1976D2"],  # S2
    4: ["#1D9E75"]   # S1
}

CLASS_COLOR = {
    "S1": "#1D9E75",
    "S2": "#1976D2",
    "S3": "#F9A825",
    "N":  "#D32F2F",
}

# LAND SUITABILITY LEGEND
LEGEND_DICT = {
    "S1 - Sangat Sesuai": "#1D9E75",
    "S2 - Cukup Sesuai": "#1976D2",
    "S3 - Sesuai Marginal": "#F9A825",
    "N - Tidak Sesuai": "#D32F2F",
}

# PARAMETER BAND NAMES
PARAM_BAND_NAMES = {
    "Rainfall_Annual": "Curah Hujan (mm/tahun)",
    "Temp_Annual": "Suhu (C)",
    "RH_Annual": "Kelembapan (%)",
    "elevation": "Elevasi (mdpl)",
    "slope_pct": "Lereng (%)",
    "cec": "CEC (mmol/kg)",
    "cn_ratio": "C/N Ratio",
    "ph": "pH Tanah",
    "clay_pct": "Kadar Liat (%)",
    "sand_pct": "Kadar Pasir (%)",
    "silt_pct": "Kadar Debu (%)",
}

CLASS_DESC = {
    "S1": {
        "title": "S1 - Sangat Sesuai",
        "desc":  "Lahan tanpa pembatas berarti atau hanya memiliki pembatas sangat ringan "
                 "yang tidak menurunkan produktivitas secara signifikan.",
    },
    "S2": {
        "title": "S2 - Cukup Sesuai",
        "desc":  "Lahan dengan pembatas sedang yang mempengaruhi produktivitas. "
                 "Diperlukan input atau tindakan pengelolaan tertentu.",
    },
    "S3": {
        "title": "S3 - Sesuai Marginal",
        "desc":  "Lahan dengan pembatas berat yang secara signifikan mengurangi "
                 "produktivitas. Input dan pengelolaan intensif diperlukan.",
    },
    "N": {
        "title": "N - Tidak Sesuai",
        "desc":  "Lahan memiliki pembatas sangat berat yang tidak dapat diatasi "
                 "dalam kondisi pengelolaan normal.",
    },
}