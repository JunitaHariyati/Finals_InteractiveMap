from config import (
    ee, st, pd, px, geemap, folium, st_folium,
    ASSETS, MAP_HEIGHT, DEFAULT_BASEMAP,
    LC_PIXEL_MAP, LC_COLOR, LC_VIS, LC_LEGEND,
)

import streamlit.components.v1 as components

# ══════════════════════════════════════════════════════════════════════════════
# KONSTANTA LOKAL
# ══════════════════════════════════════════════════════════════════════════════

YEARS = [2020, 2021, 2022, 2023, 2024, 2025]

LC_ASSET_BY_YEAR = {
    2020: ASSETS + "LC_2020",
    2021: ASSETS + "LC_2021",
    2022: ASSETS + "LC_2022",
    2023: ASSETS + "LC_2023",
    2024: ASSETS + "LC_2024",
    2025: ASSETS + "LC_2025", 
}

_COLOR = LC_COLOR 

# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════

_DEFAULTS = {
    "trend_year_a":  2020,
    "trend_year_b":  2025,
    "trend_compare": False, 
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ══════════════════════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════════════════════

st.markdown(f"""
<style>
#MainMenu, footer, header {{ visibility: hidden; }}
.stDeployButton {{ display: none; }}
[data-testid="stToolbar"] {{ display: none; }}

[data-testid="stMetricValue"] {{
    font-size: 1.5rem;
    font-weight: 700;
    color: #1a2332;
}}
[data-testid="stMetricLabel"] {{
    font-size: 1rem;
    color: #64748b;
}}
[data-testid="stMetric"] {{
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 8px 12px;
}}
            
div[data-baseweb="select"] {{
    max-width: 250px;
}}
            
[data-testid="stWidgetLabel"] p {{
    font-size: 1.3rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
}}

div[data-baseweb="select"] > div {{
    background: #ffffff;
    border-color: #e2e8f0;
    color: #1a2332;
    border-radius: 8px;
}}
div[data-baseweb="select"] > div:hover {{ border-color: #3b82f6; }}
[data-baseweb="popover"] {{ background: #ffffff; }}

.stRadio label {{
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    color: #475569;
    font-size: .8rem;
}}
.stRadio label:hover {{ border-color: #3b82f6; color: #3b82f6; }}

.stButton > button {{
    background: #ffffff;
    border: 1px solid #e2e8f0;
    color: #475569;
    border-radius: 8px;
    font-size: .8rem;
}}
.stButton > button:hover {{
    background: #eff6ff;
    border-color: #3b82f6;
    color: #3b82f6;
}}
        

hr {{ border-color: #e2e8f0; }}
::-webkit-scrollbar {{ width: 5px; }}
::-webkit-scrollbar-track {{ background: #f1f5f9; }}
::-webkit-scrollbar-thumb {{ background: #cbd5e1; border-radius: 3px; }}
[data-testid="stDataFrame"] {{ border: 1px solid #e2e8f0; border-radius: 8px; }}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
    <span style="font-size:3rem;font-weight:800;color:#1a2332;">Perbandingan Perubahan Tutupan Lahan Distrik Agats</span>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# FILTER BAR
# ══════════════════════════════════════════════════════════════════════════════

fc1, fc2 = st.columns(2)

with fc1:
    year_a = st.selectbox(
        "Tahun Awal",
        YEARS,
        index=YEARS.index(st.session_state.trend_year_a),
        key="w_year_a",
    )
    st.session_state.trend_year_a = year_a

with fc2:
    year_b_options = [y for y in YEARS if y != year_a]

    default_b = st.session_state.trend_year_b
    if default_b not in year_b_options:
        default_b = year_b_options[-1]

    year_b = st.selectbox(
        "Tahun Akhir",
        year_b_options,
        index=year_b_options.index(default_b),
        key="w_year_b",
    )
    st.session_state.trend_year_b = year_b

# ══════════════════════════════════════════════════════════════════════════════
# GEE — AREA
# ══════════════════════════════════════════════════════════════════════════════

desaAgats = ee.FeatureCollection(ASSETS + "DesaAgats")

@st.cache_data(show_spinner=False, ttl=3600)
def calc_lc_area_year(year: int) -> pd.DataFrame:
    img      = ee.Image(LC_ASSET_BY_YEAR[year])
    area_img = ee.Image.pixelArea().divide(10000).rename("area")
    rows = []
    for val, label in LC_PIXEL_MAP.items():
        try:
            ha = round(
                ee.Number(
                    area_img.updateMask(img.eq(val)).reduceRegion(
                        reducer=ee.Reducer.sum(),
                        geometry=desaAgats.geometry(),
                        scale=90,
                        maxPixels=1e13,
                        bestEffort=True,
                    ).get("area")
                ).getInfo(),
                2,
            )
        except Exception:
            ha = 0.0
        rows.append({"Kelas": label, "Area (ha)": ha, "Tahun": year})
    return pd.DataFrame(rows)

active_years = sorted({year_a, year_b})

dfs = {}
with st.spinner("Menghitung statistik tutupan lahan..."):
    for yr in active_years:
        dfs[yr] = calc_lc_area_year(yr)

df_year_a = dfs[year_a]
df_year_b = dfs.get(year_b) if year_b else None

# Gabungkan semua tahun untuk grafik tren
df_all = pd.concat(list(dfs.values()), ignore_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# LAYOUT UTAMA: TREN | STATISTIK 
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
# ─────────────────────────────────────────────────────────────────────────────
# KOLOM KIRI — TREN
# ─────────────────────────────────────────────────────────────────────────────

st.subheader(f"Perbandingan Tutupan Lahan {year_a} vs {year_b}")

df_line = pd.concat([
df_year_a.assign(Tahun=year_a),
df_year_b.assign(Tahun=year_b)
], ignore_index=True)

fig_line = px.line(
    df_line,
    x="Tahun",
    y="Area (ha)",
    color="Kelas",
    markers=True,
    color_discrete_map=LC_COLOR,
)

fig_line.update_traces(
    line_width=4,
    marker_size=10
)

fig_line.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    height=500,
    margin=dict(l=10, r=10, t=10, b=10),

    xaxis=dict(
        tickmode="array",
        tickvals=[year_a, year_b],
        ticktext=[str(year_a), str(year_b)],
        title="Tahun",
        showgrid=True,
        gridcolor="#e2e8f0",
    ),

    yaxis=dict(
        title="Luas (ha)",
        showgrid=True,
        gridcolor="#e2e8f0",
    ),

    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5,
    ),

    font=dict(
        family="Segoe UI",
        size=12,
        color="#475569"
    ),
)

st.plotly_chart(
    fig_line,
    use_container_width=True,
    config={"displayModeBar": False}
)

# ══════════════════════════════════════════════════════════════════════════════
# MAP PERBANDINGAN
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("### Map Perbandingan")

# Filter Kelas Tutupan Lahan
selected_class = st.selectbox(
"Filter Kelas Tutupan Lahan",
    list(LC_PIXEL_MAP.values()),
    index=0
)

selected_value = next(
    k for k, v in LC_PIXEL_MAP.items()
    if v == selected_class
)

# Layout 
map_left, map_right = st.columns([5, 5], gap="small")

# Load Image Year A & Year B
year_a_img = ee.Image(LC_ASSET_BY_YEAR[year_a])
year_b_img = ee.Image(LC_ASSET_BY_YEAR[year_b])

with map_left:
    st.markdown("Peta Tutupan Lahan "+str(year_a))

    Map = geemap.Map(
        draw_ctrl=False, measure_ctrl=False,
        fullscreen_ctrl=True, zoom_control=True,
    )
    Map.options["doubleClickZoom"] = False

    Map.addLayer(
    year_a_img.updateMask(year_a_img.eq(selected_value)),
    {
        "min": selected_value,
        "max": selected_value,
        "palette": [
            LC_COLOR[selected_class].replace("#", "")
        ]
    }, selected_class)
    Map.add_legend(title="Tutupan Lahan "+str(year_a), legend_dict=LC_LEGEND)
    Map.centerObject(desaAgats, 11)

    # BATAS DESA
    Map.addLayer(
        desaAgats.style(color="00e676", fillColor="00000000", width=1),
        {}, "Batas Desa",
    )
    st_folium(Map, height=MAP_HEIGHT, width=None, key=f"map_left_{year_a}")

    st.markdown("### Statistik Luas")

    area_a = df_year_a.iloc[selected_value - 1]["Area (ha)"]
    
    st.metric(
        f"Kelas {selected_class} ({year_a})",
        f"{area_a:,.1f} ha"
    )

with map_right:
    st.markdown("Peta Tutupan Lahan "+str(year_b))

    Map = geemap.Map(
        draw_ctrl=False, measure_ctrl=False,
        fullscreen_ctrl=True, zoom_control=True,
    )
    Map.options["doubleClickZoom"] = False

    Map.addLayer(
    year_b_img.updateMask(year_b_img.eq(selected_value)),
    {
        "min": selected_value,
        "max": selected_value,
        "palette": [
            LC_COLOR[selected_class].replace("#", "")
        ]
    }, selected_class)
    Map.add_legend(title="Tutupan Lahan "+str(year_b), legend_dict=LC_LEGEND)
    Map.centerObject(desaAgats, 11)

    # BATAS DESA
    Map.addLayer(
        desaAgats.style(color="00e676", fillColor="00000000", width=1),
        {}, "Batas Desa",
    )
 
    st_folium(Map, height=MAP_HEIGHT, width=None, key=f"map_left_{year_b}")

    st.markdown("### Statistik Luas")

    area_b = df_year_b.iloc[selected_value - 1]["Area (ha)"]
    
    st.metric(
        f"Kelas {selected_class} ({year_b})",
        f"{area_b:,.1f} ha"
    )
