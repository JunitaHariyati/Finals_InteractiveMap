from config import *
from utils.gee_cache import get_desa_list, calculate_area_stats

# -------------------- INITIALIZATION ---------------------

LC_ASSETS = ASSETS + "final_landcover_v1_2025" 

# -------------------- CSS ---------------------
st.markdown(f"""
<style>


/* ── Hide chrome ── */
#MainMenu, footer, header {{ visibility: hidden; }}
.stDeployButton {{ display: none; }}
[data-testid="stToolbar"] {{ display: none; }}
 
/* ── Kolom peta sticky ── */
[data-testid="stHorizontalBlock"] > div:first-child {{
    top: 0;
    align-self: flex-start;
    z-index: 1;
}}
 
/* ── Kolom kanan scroll mandiri ── */
[data-testid="stHorizontalBlock"] > div:last-child {{
    padding-right: 4px;
}}
[data-testid="stHorizontalBlock"] > div:last-child::-webkit-scrollbar {{ width: 4px; }}
[data-testid="stHorizontalBlock"] > div:last-child::-webkit-scrollbar-track {{ background: transparent; }}
[data-testid="stHorizontalBlock"] > div:last-child::-webkit-scrollbar-thumb {{
    background: #cbd5e1; border-radius: 2px;
}}
 
/* ── Metric ── */
[data-testid="stMetricValue"] {{
    font-size: 1.25rem !important;
    font-weight: 700 !important;
    color: #1a2332 !important;
}}
[data-testid="stMetricLabel"] {{
    font-size: .72rem !important;
    color: #64748b !important;
}}
[data-testid="stMetric"] {{
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 10px !important;
    padding: 10px 14px !important;
}}
 
/* ── Selectbox & radio ── */
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
 
/* ── Button ── */
.stButton > button {{
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    color: #475569 !important;
    border-radius: 8px !important;
    font-size: .8rem !important;
}}
.stButton > button:hover {{
    background: #f0f9ff !important;
    border-color: #3b82f6 !important;
    color: #3b82f6 !important;
}}
 
/* ── Divider ── */
hr {{ border-color: #e2e8f0 !important; }}
 
/* ── Scrollbar global ── */
::-webkit-scrollbar {{ width: 5px; }}
::-webkit-scrollbar-track {{ background: #f1f5f9; }}
::-webkit-scrollbar-thumb {{ background: #cbd5e1; border-radius: 3px; }}
 
/* ── Dataframe ── */
[data-testid="stDataFrame"] {{ border: 1px solid #e2e8f0 !important; border-radius: 8px !important; }}
</style>
""", unsafe_allow_html=True)

# ----------------- HEADER -----------------

st.markdown("""
    <span style="font-size:3rem;font-weight:800;color:#1a2332;">WebGIS Kesesuaian Lahan Distrik Agats</span>
    <div style="font-size:1rem;color:#475569;line-height:1.65;width:100%;">
        Sistem informasi geografis berbasis web untuk analisis kesesuaian lahan
        komoditas pertanian di <strong style="color:#16a34a;">Distrik Agats</strong>,
        Kabupaten Asmat, Provinsi Papua Selatan. Data diproses menggunakan
        <strong style="color:#2563eb;">Google Earth Engine</strong> dengan citra
        Sentinel-2 tahun 2025.
    </div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# METODOLOGI — 4 kartu
# ══════════════════════════════════════════════════════════════════════════════
 
st.markdown("""
<div style="font-size:1rem;font-weight:700;text-transform:uppercase;
            letter-spacing:1.2px;color:#1a2332;margin-bottom:8px;">
    Alur Metodologi
</div>""", unsafe_allow_html=True)
 
m1, m2, m3, m4 = st.columns(4)
 
def _method_card(col, step, title, desc, color, bg):
    with col:
        st.markdown(f"""
        <div style="background:{bg};border:1px solid {color}30;
                    border-top:3px solid {color};border-radius:10px;
                    padding:14px 14px 12px;height:100%;">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
                <span style="font-size:.7rem;font-weight:700;text-transform:uppercase;
                             letter-spacing:1px;color:{color};">LANGKAH {step}</span>
            </div>
            <div style="font-size:1rem;font-weight:700;color:#1a2332;margin-bottom:5px;">
                {title}
            </div>
            <div style="font-size:.72rem;color:#64748b;line-height:1.55;">{desc}</div>
        </div>""", unsafe_allow_html=True)
 
_method_card(m1, "1", "Pengumpulan Data",
    "Sentinel-2 2025, ERA5 Monthly Climate, SRTM DEM 90m, CHIRPS Precipitation Daily, SoilGrids Topsoil.",
    "#2563eb", "#eff6ff")
_method_card(m2, "2", "Klasifikasi Hierarki",
    "Level-1: Wilayah Terbangun, Vegetasi, Badan Air. Level-2B: kelas vegetasi detail.",
    "#16a34a", "#f0fdf4")
_method_card(m3, "3", "Analisis Kesesuaian Lahan",
    "Weighted Average & Limiting Factor berbasis FAO Land Evaluation Framework 1976.",
    "#d97706", "#fffbeb")
_method_card(m4, "4", "Visualisasi",
    "Dashboard WebGIS interaktif menampilkan statistik luas, grafik, info detail per piksel.",
    "#7c3aed", "#faf5ff")
 
st.markdown("<div style='margin-bottom:16px'></div>", unsafe_allow_html=True)

 
# ══════════════════════════════════════════════════════════════════════════════
# DATA GEE
# ══════════════════════════════════════════════════════════════════════════════
 
desaAgats = ee.FeatureCollection(ASSETS + "DesaAgats")
lc_image  = ee.Image(LC_ASSETS)

@st.cache_data(show_spinner=False)
def calc_lc_area():
    area_img = ee.Image.pixelArea().divide(10000).rename("area")
    rows = []
    for val, label in LC_PIXEL_MAP.items():
        try:
            ha = round(ee.Number(
                area_img.updateMask(lc_image.eq(val)).reduceRegion(
                    reducer=ee.Reducer.sum(), geometry=desaAgats.geometry(),
                    scale=90, maxPixels=1e13, bestEffort=True,
                ).get("area")
            ).getInfo(), 2)
        except Exception:
            ha = 0.0
        rows.append({"Kelas": label, "Area (ha)": ha})
    return pd.DataFrame(rows)
 
with st.spinner("Menghitung luas tutupan lahan…"):
    df_lc = calc_lc_area()
 
total_lc    = round(df_lc["Area (ha)"].sum(), 2)
df_lc_valid = df_lc[df_lc["Area (ha)"] > 0].copy()
df_lc_valid["Persen (%)"] = (
    (df_lc_valid["Area (ha)"] / total_lc * 100).round(2) if total_lc > 0 else 0.0
)
 
# ══════════════════════════════════════════════════════════════════════════════
# LAYOUT: 70% peta | 30% statistik
# ══════════════════════════════════════════════════════════════════════════════
 
col_map, col_stat = st.columns([7, 3], gap="small")
 
# ─────────────────────────────────────────────────────────────────────────────
# KOLOM KIRI: PETA
# ─────────────────────────────────────────────────────────────────────────────
 
with col_map:
    Map = geemap.Map(
        draw_ctrl=False, measure_ctrl=False,
        fullscreen_ctrl=True, zoom_control=True,
    )
    Map.options["doubleClickZoom"] = False

    # BASEMAP
    Map.add_basemap(DEFAULT_BASEMAP)

    # LAND COVER LAYER
    Map.addLayer(lc_image, LC_VIS, "Tutupan Lahan 2025")
    Map.add_legend(title="Tutupan Lahan (Sentinel-2 2025)", legend_dict=LC_LEGEND)
    Map.centerObject(desaAgats, 11)

    # BATAS DESA
    Map.addLayer(
        desaAgats.style(color="00e676", fillColor="00000000", width=1),
        {}, "Batas Desa",
    )
 
    st_folium(Map, height=MAP_HEIGHT, width=None)
 
# ─────────────────────────────────────────────────────────────────────────────
# KOLOM KANAN: STATISTIK
# ─────────────────────────────────────────────────────────────────────────────
 
with col_stat:
    stat_cont = st.container(height=MAP_HEIGHT)
    with stat_cont:
 
        def _sec(label):
            st.markdown(f"""
            <div style="font-size:1rem;font-weight:700;text-transform:uppercase;
                        letter-spacing:1px;color:#1a2332;margin:10px 0 6px;
                        padding-bottom:4px;border-bottom:1px solid #e2e8f0;">
                {label}
            </div>""", unsafe_allow_html=True)
 
        # ── Wilayah aktif ─────────────────────────────────────────────────
        _sec("Wilayah Aktif")
        st.markdown(f"""
        <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;
                    padding:12px 14px;margin-bottom:8px;">
            <div style="font-size:1rem;color:#64748b;margin-bottom:2px;">Wilayah</div>
            <div style="font-size:1.3rem;font-weight:700;color:#1a2332;">Distrik Agats</div>
            <div style="font-size:1rem;color:#94a3b8;margin-top:3px;">
                Total luas teranalisis
            </div>
            <div style="font-size:1.7rem;font-weight:800;color:#15803d;margin-top:1px;">
                {total_lc:,.1f} ha
            </div>
        </div>""", unsafe_allow_html=True)
 
        # ── Luas per kelas ────────────────────────────────────────────────
        _sec("Luas per Kelas Tutupan")
        for _, row in df_lc_valid.sort_values("Area (ha)", ascending=False).iterrows():
            pct   = row["Persen (%)"]
            color = LC_COLOR.get(row["Kelas"], "#888")
            bar_w = max(3, int(pct))
            # Lighten bg: use color + '18'
            st.markdown(f"""
            <div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:8px;
                        padding:8px 10px;margin-bottom:5px;">
                <div style="display:flex;align-items:center;
                            justify-content:space-between;margin-bottom:4px;">
                    <div style="display:flex;align-items:center;gap:7px;">
                        <div style="width:10px;height:10px;border-radius:2px;
                                    background:{color};flex-shrink:0;"></div>
                        <span style="font-size: 1rem;font-weight:600;
                                     color:#1a2332;">{row['Kelas']}</span>
                    </div>
                    <span style="font-size:1rem;color:#64748b;font-weight:600;">
                        {pct:.1f}%
                    </span>
                </div>
                <div style="background:#f1f5f9;border-radius:3px;height:4px;">
                    <div style="background:{color};height:4px;border-radius:3px;
                                width:{bar_w}%;"></div>
                </div>
                <div style="font-size:1rem;color:#94a3b8;margin-top:3px;text-align:right;">
                    {row['Area (ha)']:,.1f} ha
                </div>
            </div>""", unsafe_allow_html=True)
 
        # ── Pie chart ─────────────────────────────────────────────────────
        if total_lc > 0:
            _sec("Proporsi Tutupan")
            fig_pie = px.pie(
                df_lc_valid, names="Kelas", values="Area (ha)",
                color="Kelas", color_discrete_map=LC_COLOR, hole=0.4,
            )
            fig_pie.update_traces(
                textposition="inside", textinfo="percent", textfont_size=10,
            )
            fig_pie.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#475569", size=10),
                margin=dict(l=0, r=0, t=6, b=0), showlegend=False, height=230
            )
            st.plotly_chart(fig_pie, use_container_width=True,
                            config={"displayModeBar": False})
 
        # ── Tentang peta ──────────────────────────────────────────────────
        _sec("Tentang Peta Tutupan Lahan")
        st.markdown("""
        <div style="font-size:0.85rem;color:#475569;line-height:1.65;
                    background:#f8fafc;border:1px solid #e2e8f0;
                    border-radius:8px;padding:12px 13px;">
            Penjelasan kelas tutupan lahan sebagai berikut.
            <br><br>
            <strong style="color:#1a2332;">Hutan</strong> : Area vegetasi tinggi dan rapat (hutan, rawa hutan, atau mangrove).
            <br>
            <strong style="color:#1a2332;">Vegetasi Tergenang</strong> : Vegetasi yang bercampur dengan genangan air.
            <br>
            <strong style="color:#1a2332;">Tanaman</strong> : Area budidaya tanaman pertanian dan lahan tanam yang dikelola manusia.
            <br>
            <strong style="color:#1a2332;">Lahan Terbuka</strong> : Area tanah atau batuan terbuka dengan sedikit atau tanpa vegetasi.
            <br>
            <strong style="color:#1a2332;">Padang Rumput</strong> : Area terbuka yang didominasi rumput atau semak rendah.
            <br>
            <strong style="color:#1a2332;">Wilayah Terbangun</strong> : Area permukiman dan infrastruktur buatan manusia.
            <br>
            <strong style="color:#1a2332;">Badan Air</strong> : Area yang didominasi perairan seperti sungai dan rawa.
        </div>""", unsafe_allow_html=True)
 
        # ── Parameter LSA ─────────────────────────────────────────────────
        _sec("Parameter Analisis LSA")
        params = [
            ("🌧️", "Curah Hujan Tahunan",  "mm/tahun"),
            ("🌡️", "Suhu Rata-rata",        "°C"),
            ("💧", "Kelembaban Relatif",    "%"),
            ("⛰️", "Elevasi",               "mdpl"),
            ("📐", "Kemiringan Lereng",     "%"),
            ("🧪", "pH Tanah",              "–"),
            ("🪨", "KTK / CEC",             "cmol/kg"),
            ("🌱", "C/N Ratio",             "–"),
            ("🏔️", "Tekstur Tanah",         "% liat/pasir/debu"),
        ]
        for icon, name, unit in params:
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:8px;padding:4px 0;
                        border-bottom:1px solid #f1f5f9;font-size:.73rem;">
                <span>{icon}</span>
                <span style="flex:1;color:#334155;">{name}</span>
                <span style="color:#94a3b8;font-size:.65rem;">{unit}</span>
            </div>""", unsafe_allow_html=True)
 
# ══════════════════════════════════════════════════════════════════════════════
# FOOTER INFO — 3 kartu
# ══════════════════════════════════════════════════════════════════════════════
 
st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
 
fi1, fi2, fi3 = st.columns(3)
 
def _info_card(col, icon, title, lines, color, bg, border):
    with col:
        items = "".join(f"""
        <div style="display:flex;gap:7px;padding:3px 0;font-size:.72rem;">
            <span style="color:{color};flex-shrink:0;margin-top:1px;">▸</span>
            <span style="color:#475569;">{l}</span>
        </div>""" for l in lines)
        st.markdown(f"""
        <div style="background:{bg};border:1px solid {border};
                    border-radius:10px;padding:14px 15px;height:100%;">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:9px;">
                <span style="font-size:1.2rem;">{icon}</span>
                <span style="font-size:.78rem;font-weight:700;color:#1a2332;">{title}</span>
            </div>
            {items}
        </div>""", unsafe_allow_html=True)
 
_info_card(fi1, "🛰️", "Sumber Data", [
    "Sentinel-2 MSI L2A (2025)",
    "ERA5 Monthly Climate (2025)",
    "SRTM DEM 90m",
    "SoilGrids v2 Topsoil",
    "DesaAgats FeatureCollection",
], "#2563eb", "#eff6ff", "#bfdbfe")
 
_info_card(fi2, "⚙️", "Metode Analisis", [
    "Klasifikasi Hierarki Bertingkat",
    "Random Forest Classifier",
    "FAO Land Evaluation Framework 1976",
    "Weighted Average (WA)",
    "Limiting Factor (LF)",
], "#16a34a", "#f0fdf4", "#bbf7d0")
 
_info_card(fi3, "📐", "Spesifikasi Teknis", [
    "Resolusi spasial: 90 m",
    "Proyeksi: WGS84 (EPSG:4326)",
    "Scale reduksi: 90 m/piksel",
    "Luas: ee.Image.pixelArea()",
    "Reduce: ee.Reducer.sum()",
], "#d97706", "#fffbeb", "#fde68a")