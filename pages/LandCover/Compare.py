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
    font-size: 1.15rem !important;
    font-weight: 700 !important;
    color: #1a2332 !important;
}}
[data-testid="stMetricLabel"] {{
    font-size: .7rem !important;
    color: #64748b !important;
}}
[data-testid="stMetric"] {{
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 10px !important;
    padding: 8px 12px !important;
}}

div[data-baseweb="select"] > div {{
    background: #ffffff !important;
    border-color: #e2e8f0 !important;
    color: #1a2332 !important;
    border-radius: 8px !important;
}}
div[data-baseweb="select"] > div:hover {{ border-color: #3b82f6 !important; }}
[data-baseweb="popover"] {{ background: #ffffff !important; }}

.stRadio label {{
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 6px !important;
    color: #475569 !important;
    font-size: .8rem !important;
}}
.stRadio label:hover {{ border-color: #3b82f6 !important; color: #3b82f6 !important; }}

.stButton > button {{
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    color: #475569 !important;
    border-radius: 8px !important;
    font-size: .8rem !important;
}}
.stButton > button:hover {{
    background: #eff6ff !important;
    border-color: #3b82f6 !important;
    color: #3b82f6 !important;
}}

hr {{ border-color: #e2e8f0 !important; }}
::-webkit-scrollbar {{ width: 5px; }}
::-webkit-scrollbar-track {{ background: #f1f5f9; }}
::-webkit-scrollbar-thumb {{ background: #cbd5e1; border-radius: 3px; }}
[data-testid="stDataFrame"] {{ border: 1px solid #e2e8f0 !important; border-radius: 8px !important; }}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
    <span style="font-size:3rem;font-weight:800;color:#1a2332;">Tren Perubahan Tutupan Lahan Distrik Agats</span>
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

col_left, col_right = st.columns([7, 3], gap="small")
# ─────────────────────────────────────────────────────────────────────────────
# KOLOM KIRI — TREN
# ─────────────────────────────────────────────────────────────────────────────

with col_left:

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

# ─────────────────────────────────────────────────────────────────────────────
# KOLOM KANAN — STATISTIK
# ─────────────────────────────────────────────────────────────────────────────
def _section_label(text: str, margin_top: str = "10px"):
    st.markdown(f"""
    <div style="font-size:1rem;font-weight:700;text-transform:uppercase;
                letter-spacing:1px;color:#1a2332;margin:{margin_top} 0 5px;
                padding-bottom:3px;border-bottom:1px solid #e2e8f0;">
        {text}
    </div>""", unsafe_allow_html=True)

with col_right:
    stat_cont = st.container(height=650)
    with stat_cont:
        st.markdown("### Statistik Wilayah")
        total_a = df_year_a["Area (ha)"].sum()
        total_b = df_year_b["Area (ha)"].sum()

        st.metric(
            f"Total {year_b}",
            f"{total_b:,.1f} ha"
        )

        pivot_df = (
            df_all
            .pivot(
                index="Kelas",
                columns="Tahun",
                values="Area (ha)"
            )
        )

        change_df = pivot_df[year_b] - pivot_df[year_a]

        # ── Luas per kelas (tahun A)
        _section_label(f"Luas Kelas - {year_a}" + (f" vs {year_b}"))

        df_a_sorted = df_year_a.sort_values("Area (ha)", ascending=False)

        df_b_lookup = df_year_b.set_index("Kelas")["Area (ha)"].to_dict()

        html_cards = """
        <style>
            * {
                font-family: "Source Sans", sans-serif;
            }
        </style>
        """
        for _, row in df_a_sorted.iterrows():
            cls    = row["Kelas"]
            ha_a   = row["Area (ha)"]
            ha_b   = df_b_lookup.get(cls, 0.0)
            delta  = round(ha_b - ha_a, 2)

            color  = _COLOR.get(cls, "#888")
            arrow  = "▲" if delta > 0 else ("▼" if delta < 0 else "-")
            d_col  = "#15803d" if delta > 0 else ("#b91c1c" if delta < 0 else "#64748b")
            
            html_cards += f"""
            <div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:8px;
                        padding:10px 12px;margin-bottom:6px;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
                    <div style="display:flex;align-items:center;gap:8px;">
                        <div style="width:10px;height:10px;border-radius:2px;background:{color};"></div>
                        <span style="font-size:0.85rem;font-weight:600;color:#1a2332;">{cls}</span>
                    </div>
                    <span style="font-size:0.8rem;font-weight:700;color:{d_col};">
                        {arrow} {abs(delta):,.1f} ha
                    </span>
                </div>
                <div style="font-size:0.72rem;color:#64748b;display:flex;justify-content:space-between;">
                    <span>{year_a}: {ha_a:,.1f} ha</span>
                    <span>{year_b}: {ha_b:,.1f} ha</span>
                </div>
            </div>
            """

        components.html(html_cards, height=len(change_df) * 65, scrolling=True)