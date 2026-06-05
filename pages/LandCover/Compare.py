from config import *
from utils.gee_cache import calc_lc_area_year

import streamlit.components.v1 as components

# ===================== INITIALIZATION =======================

YEARS = [2020, 2021, 2022, 2023, 2024, 2025]
_COLOR = LC_COLOR 
load_css()

# ===================== SESSION STATE =======================
_DEFAULTS = {
    "trend_year_a":  2020,
    "trend_year_b":  2025,
    "trend_compare": False, 
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ===================== HEADER TITLE =======================
st.markdown("""
    <span style="font-size:3rem;font-weight:800;color:#1a2332;">Perbandingan Perubahan Tutupan Lahan Distrik Agats</span>
""", unsafe_allow_html=True)

# ===================== FILTER BAR (YEAR) =======================
fc1, fc2, fc3 = st.columns([2, 2, 5])

# LEFT (TAHUN AWAL: YEAR A)
with fc1:
    year_a = st.selectbox(
        "Tahun Awal",YEARS,
        index=YEARS.index(st.session_state.trend_year_a),key="w_year_a",
    )
    # SET SESSION STATE YEAR A
    st.session_state.trend_year_a = year_a

# RIGHT (TAHUN AKHIR: YEAR B)
with fc2:
    # YEAR B OPTION EXCEPT YEAR A
    year_b_options = [y for y in YEARS if y != year_a]

    default_b = st.session_state.trend_year_b
    if default_b not in year_b_options:
        default_b = year_b_options[-1]

    year_b = st.selectbox(
        "Tahun Akhir",year_b_options,
        index=year_b_options.index(default_b),key="w_year_b",
    )
    # SET SESSION STATE YEAR B
    st.session_state.trend_year_b = year_b

# ===================== LOAD IMAGE =======================
desaAgats = ee.FeatureCollection(ASSETS + "DesaAgats")
active_years = sorted({year_a, year_b})

# ===================== CALCULATE AREA BY YEAR =======================
dfs = {}
with st.spinner("Menghitung statistik tutupan lahan..."):
    for yr in active_years:
        dfs[yr] = calc_lc_area_year(yr)

df_year_a = dfs[year_a]
df_year_b = dfs.get(year_b) if year_b else None

# COMBINE BOTH YEAR
df_all = pd.concat(list(dfs.values()), ignore_index=True)


# ===================== LAYOUTING =======================
st.markdown("---")

# LINE CHART: LAND COVER CHANGES YEAR A -> YEAR B
st.subheader(f"Perbandingan Tutupan Lahan {year_a} vs {year_b}")

df_line = pd.concat([
    df_year_a.assign(Tahun=year_a),
    df_year_b.assign(Tahun=year_b)
], ignore_index=True)

# LINE CHART
fig_line = px.line(
    df_line, x="Tahun", y="Area (ha)",
    color="Kelas", markers=True, color_discrete_map=LC_COLOR,
)

fig_line.update_traces(
    line_width=4, marker_size=10
)

fig_line.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    height=500, margin=dict(l=10, r=10, t=10, b=10),

    xaxis=dict(
        tickmode="array", tickvals=[year_a, year_b],
        ticktext=[str(year_a), str(year_b)], title="Tahun",
        showgrid=True, gridcolor="#e2e8f0",
    ),

    yaxis=dict(title="Luas (ha)",showgrid=True,gridcolor="#e2e8f0",),

    legend=dict(
        orientation="h",yanchor="bottom",
        y=1.02,xanchor="center",x=0.5,
    ),

    font=dict(
        family="Segoe UI",size=12,color="#475569"
    ),
)

# ADD CHART TO PAGE
st.plotly_chart(
    fig_line,
    use_container_width=True,
    config={"displayModeBar": False}
)

# ===================== COMPARISON MAP =======================
st.markdown("---")
st.markdown("### Map Perbandingan")

# FILTER BY LAND COVER CLASSES
selected_class = st.selectbox(
"Filter Kelas Tutupan Lahan",
    list(LC_PIXEL_MAP.values()),
    index=0
)

selected_value = next(
    k for k, v in LC_PIXEL_MAP.items()
    if v == selected_class
)


# ===================== LAYOUTING =======================
# MAP YEAR A  | MAP YEAR B
# STATS YEAR A| STATS YEAR B
 
map_left, map_right = st.columns([5, 5], gap="small")

# LOAD IMAGE YEAR A & B
year_a_img = ee.Image(LC_ASSET_BY_YEAR[year_a])
year_b_img = ee.Image(LC_ASSET_BY_YEAR[year_b])

# ===================== MAP YEAR A (LEFT) =======================
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

    # ADD MAP TO PAGE
    st_folium(Map, height=600, width=None, key=f"map_left_{selected_value}_{year_a}")

    # YEAR A STATS
    st.markdown("### Statistik Luas")
    area_a = df_year_a.iloc[selected_value - 1]["Area (ha)"]
    st.metric(
        f"Kelas {selected_class} ({year_a})",
        f"{area_a:,.1f} ha"
    )

# ===================== MAP YEAR B (RIGHT) =======================
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
    # ADD MAP TO PAGE
    st_folium(Map, height=600, width=None, key=f"map_left_{selected_value}_{year_b}")

    # YEAR B STATS
    st.markdown("### Statistik Luas")
    area_b = df_year_b.iloc[selected_value - 1]["Area (ha)"]
    st.metric(
        f"Kelas {selected_class} ({year_b})",
        f"{area_b:,.1f} ha"
    )
