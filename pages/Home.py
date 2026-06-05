from config import *
from utils.gee_cache import calc_lc_area_year

# ===================== INITIALIZATION =======================
LC_ASSETS = ASSETS + "LC_2025" 
load_css()

# ===================== HEADER TITLE =======================
st.markdown("""
    <span style="font-size:3rem;font-weight:800;color:#1a2332;">Peta Tutupan Lahan & Kesesuaian Lahan Distrik Agats, Kabupaten Asmat, Provinsi Papua Selatan</span>
""", unsafe_allow_html=True)
 
# ===================== LOAD ASSETS =======================
desaAgats = ee.FeatureCollection(ASSETS + "DesaAgats")
lc_image  = ee.Image(LC_ASSETS)

# ===================== CALC TOTAL AREA =======================
with st.spinner("Menghitung luas tutupan lahan…"):
    df_lc = calc_lc_area_year(2025)
 
total_lc    = round(df_lc["Area (ha)"].sum(), 2)
df_lc_valid = df_lc[df_lc["Area (ha)"] > 0].copy()
df_lc_valid["Persen (%)"] = (
    (df_lc_valid["Area (ha)"] / total_lc * 100).round(2) if total_lc > 0 else 0.0
)
 
# ===================== LAYOUTING =======================
# MAP | STATS
 
col_map, col_stat = st.columns([7, 3], gap="small")
 
# ===================== MAP (LEFT) =======================
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
    
    # ADD MAP TO PAGE
    st_folium(Map, height=MAP_HEIGHT, width=None)
 
# ===================== STATS (RIGHT) =======================
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
 
        # ===================== TOTAL AREA =======================
        _sec("Statistik Wilayah")
        st.markdown(f"""
        <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;
                    padding:12px 14px;margin-bottom:8px;">
            <div style="font-size:1rem;color:#64748b;margin-bottom:2px;">Wilayah</div>
            <div style="font-size:1.3rem;font-weight:700;color:#1a2332;">Distrik Agats</div>
            <div style="font-size:1rem;color:#94a3b8;margin-top:3px;">
                Total luas (Tahun 2025)
            </div>
            <div style="font-size:1.7rem;font-weight:800;color:#15803d;margin-top:1px;">
                {total_lc:,.1f} ha
            </div>
        </div>""", unsafe_allow_html=True)
 
        # ===================== AREA LAND COVER =======================
        _sec("Luas per Kelas Tutupan")
        for _, row in df_lc_valid.sort_values("Area (ha)", ascending=False).iterrows():
            pct   = row["Persen (%)"]
            color = LC_COLOR.get(row["Kelas"], "#888")
            bar_w = max(3, int(pct))
            st.markdown(f"""
            <div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:8px;
                        padding:8px 10px;margin-bottom:5px;">
                <div style="display:flex;align-items:center;
                            justify-content:space-between;margin-bottom:4px;">
                    <div style="display:flex;align-items:center;gap:7px;">
                        <div style="width:10px;height:10px;border-radius:2px;
                                    background:{color};flex-shrink:0;"></div>
                        <span style="font-size: 1rem;font-weight:600;color:#1a2332;">{row['Kelas']}</span>
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
 
        # ===================== PIE CHART =======================
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
 
        # ===================== LAND COVER INFO =======================
        _sec("Tentang Peta Tutupan Lahan")
        st.markdown("""
        <div style="font-size:1rem;color:#475569;line-height:1.65;
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