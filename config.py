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

LC_COLOR = {
    "Hutan":              "#1b7a2f",
    "Vegetasi Tergenang": "#0097a7",
    "Tanaman":            "#8bc34a",
    "Lahan Terbuka":      "#a1887f",
    "Padang Rumput":      "#689f38",
    "Wilayah Terbangun":  "#e53935",
    "Badan Air":          "#1565c0",
}
 
LC_VIS = {
    "min":     1,
    "max":     7,
    "palette": ["1b7a2f","0097a7","8bc34a","a1887f","689f38","e53935","1565c0"],
    "opacity": 0.85,
}
 
LC_LEGEND = {
    "Hutan":              "#1b7a2f",
    "Vegetasi Tergenang": "#0097a7",
    "Tanaman":            "#8bc34a",
    "Lahan Terbuka":      "#a1887f",
    "Padang Rumput":      "#689f38",
    "Wilayah Terbangun":  "#e53935",
    "Badan Air / Sungai": "#1565c0",
}
 
LC_PIXEL_MAP = {
    1: "Hutan", 2: "Vegetasi Tergenang", 3: "Tanaman",
    4: "Lahan Terbuka", 5: "Padang Rumput", 6: "Wilayah Terbangun", 7: "Badan Air",
}
 
BASEMAP_MAP = {
    "SATELLITE": "Esri WorldImagery",
    "HYBRID":    "Esri WorldImagery",
    "ROADMAP":   "OpenStreetMap",
    "TERRAIN":   "Stamen Terrain",
}

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

CLASS_COLOR = {
    "S1": "#1D9E75",
    "S2": "#97C459",
    "S3": "#EF9F27",
    "N":  "#E24B4A",
}

# Legend
LEGEND_DICT = {
    "S1 - Sangat Sesuai": "#1D9E75",
    "S2 - Cukup Sesuai": "#97C459",
    "S3 - Sesuai Marginal": "#EF9F27",
    "N - Tidak Sesuai": "#E24B4A"
}

PARAM_BAND_NAMES = {
        "Rainfall_Annual": "Curah Hujan (mm/tahun)",
        "Temp_Annual":     "Suhu (°C)",
        "RH_Annual":       "Kelembaban (%)",
        "elevation":       "Elevasi (mdpl)",
        "slope_pct":       "Lereng (%)",
        "cec":             "CEC (mmol/kg)",
        "cn_ratio":        "C/N Ratio",
        "ph":              "pH Tanah",
        "clay_pct":        "Kadar Liat (%)",
        "sand_pct":        "Kadar Pasir (%)",
        "silt_pct":        "Kadar Debu (%)",
    }

CLASS_DESC = {
    "S1": {
        "title": "S1 – Sangat Sesuai",
        "desc":  "Lahan tanpa pembatas berarti atau hanya memiliki pembatas sangat ringan "
                 "yang tidak menurunkan produktivitas secara signifikan.",
    },
    "S2": {
        "title": "S2 – Cukup Sesuai",
        "desc":  "Lahan dengan pembatas sedang yang mempengaruhi produktivitas. "
                 "Diperlukan input atau tindakan pengelolaan tertentu.",
    },
    "S3": {
        "title": "S3 – Sesuai Marginal",
        "desc":  "Lahan dengan pembatas berat yang secara signifikan mengurangi "
                 "produktivitas. Input dan pengelolaan intensif diperlukan.",
    },
    "N": {
        "title": "N – Tidak Sesuai",
        "desc":  "Lahan memiliki pembatas sangat berat yang tidak dapat diatasi "
                 "dalam kondisi pengelolaan normal.",
    },
}

VAL_TO_LABEL = {1: "N", 2: "S3", 3: "S2", 4: "S1"}