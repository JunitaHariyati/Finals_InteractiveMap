# Library
from config import *
from utils.gee_cache import (get_desa_list, calculate_area_stats)
from utils.gee_info import (get_polygon_statistics)
from utils.gee_layers import (build_parameter_stack)

# -------------------- INITIALIZATION ---------------------
# LOCAL CONSTANT
ASSET_WA   = ASSETS + "LSA_durian_WA_2025"
ASSET_LF   = ASSETS + "LSA_durian_LF_2025"
VEGETATION = ASSETS + "classified_2025_2B_ESRI"

_defaults = {
    "durian_method":        "Weighted Average",
    "durian_desa":          "Semua Desa",
    "durian_class":         "Semua Kelas",
    "durian_clicked_point": None,
    "durian_click_stats":   None,
}
for _k, _v in _defaults.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# -------------------- CSS ---------------------

st.markdown("""
    <style>
    #MainMenu, footer, header {{ visibility: hidden; }}
    .stDeployButton {{ display: none; }}
    [data-testid="stToolbar"] {{ display: none; }}
            
    [data-testid="stMetricValue"] {
        font-size: 30px;
    }
            
    [data-testid="block-container"]
    [data-testid="stHorizontalBlock"]
    > [data-testid="stColumn"]:first-of-type {{
        position: sticky;
        top: 0;
        align-self: flex-start;
        z-index: 1;
    }}
    
    [data-testid="block-container"]
    [data-testid="stHorizontalBlock"]
    > [data-testid="stColumn"]:last-of-type {{
        height: 700px;
        max-height: 700px;
        overflow-y: auto;
        overflow-x: hidden;
        padding-right: 4px;
    }}
    
    [data-testid="block-container"]
    [data-testid="stHorizontalBlock"]
    > [data-testid="stColumn"]:last-of-type::-webkit-scrollbar {{ width: 4px; }}
    [data-testid="block-container"]
    [data-testid="stHorizontalBlock"]
    > [data-testid="stColumn"]:last-of-type::-webkit-scrollbar-track {{ background: transparent; }}
    [data-testid="block-container"]
    [data-testid="stHorizontalBlock"]
    > [data-testid="stColumn"]:last-of-type::-webkit-scrollbar-thumb {{
        background: #000000; border-radius: 2px;
    }}
    </style>
    """,unsafe_allow_html=True)


# -------------------- MAIN PAGE ---------------------

# HEADER
st.title("Analisis Kesesuaian Lahan - Durian")

# -------------------- FILTERING OPTION ---------------------
with st.container():
    st.markdown("""
    <div style="font-size:.65rem;font-weight:600;text-transform:uppercase;
                letter-spacing:1px;color:#484f58;margin-bottom:6px">
        ⚙ Filter &amp; Kontrol
    </div>
    """, unsafe_allow_html=True)
 
    fc1, fc2, fc3 = st.columns([1.8, 2.4, 2.4])
 
    with fc1:
        method = st.radio(
            "Metode LSA",
            ["Weighted Average"],
            index=0,
            horizontal=True,
            key="w_method",
        )
        if method != st.session_state.durian_method:
            st.session_state.durian_method        = method
            st.session_state.durian_clicked_point = None
            st.session_state.durian_click_stats   = None
 
    with fc2:
        desa_list    = get_desa_list()
        desa_options = ["Semua Desa"] + desa_list
        sel_desa = st.selectbox(
            "Wilayah Desa",
            desa_options,
            index=desa_options.index(st.session_state.durian_desa)
                  if st.session_state.durian_desa in desa_options else 0,
            key="w_desa",
        )
        if sel_desa != st.session_state.durian_desa:
            st.session_state.durian_desa          = sel_desa
            st.session_state.durian_clicked_point = None
            st.session_state.durian_click_stats   = None
 
    with fc3:
        class_options = list(CLASS_OPTIONS.keys())
        sel_class = st.selectbox(
            "Kelas Kesesuaian",
            class_options,
            index=class_options.index(st.session_state.durian_class)
                  if st.session_state.durian_class in class_options else 0,
            key="w_class",
        )
        if sel_class != st.session_state.durian_class:
            st.session_state.durian_class = sel_class

st.markdown("<div style='margin-bottom:10px'></div>", unsafe_allow_html=True)

# ---- Assets ---
desaAgats = ee.FeatureCollection(ASSETS + "DesaAgats")

asset_id = ASSETS + "LSA_durian_WA_2025"

veget_mask = ee.Image(VEGETATION).neq(1).And(ee.Image(VEGETATION).neq(2))
image_raw  = ee.Image(asset_id).updateMask(veget_mask)

# -------------------- FILTER CLASS ---------------------
sel_class_val = CLASS_OPTIONS[st.session_state.durian_class]

# Filter Class Map
if sel_class_val == 0:
    display_image = image_raw
    map_vis = CLASS_VIS
else:
    display_image = image_raw.updateMask(image_raw.eq(sel_class_val))
    map_vis = {
        "min":     sel_class_val,
        "max":     sel_class_val,
        "palette": SINGLE_CLASS_PALETTE[sel_class_val],
        "opacity": 0.75,
    }

# -------------------- FILTER DESA ---------------------
if st.session_state.durian_desa == "Semua Desa":
    filtered_image    = display_image
    region_geometry   = desaAgats.geometry()
    map_center_obj    = desaAgats
    zoom_level        = 11
    desa_fc           = None
else:
    desa_fc         = desaAgats.filter(ee.Filter.eq("NAMOBJ", st.session_state.durian_desa))
    filtered_image  = display_image.clip(desa_fc).updateMask(
        ee.Image.constant(1).clip(desa_fc)
    )
    region_geometry = desa_fc.geometry()
    map_center_obj  = desa_fc
    zoom_level      = 13

# -------------------- CALCULATE AREA ---------------------

with st.spinner("Menghitung statistik luas…"):
    df_area = calculate_area_stats(
        asset_key=asset_id,
        _image=filtered_image,
        _region_geometry=region_geometry,
        region_key=st.session_state.cocoa_desa,
        method_key=st.session_state.cocoa_method
    )

if sel_class_val != 0:
    df_area = df_area[df_area["Kelas"] == VAL_TO_LABEL[sel_class_val]]
 
total_area = round(df_area["Area (ha)"].sum(), 2)
s1_area    = round(df_area[df_area["Kelas"] == "S1"]["Area (ha)"].sum(), 2)
s2_area    = round(df_area[df_area["Kelas"] == "S2"]["Area (ha)"].sum(), 2)
s3_area    = round(df_area[df_area["Kelas"] == "S3"]["Area (ha)"].sum(), 2)
n_area     = round(df_area[df_area["Kelas"] == "N"]["Area (ha)"].sum(), 2)

pct_s1 = (s1_area / total_area * 100) if total_area > 0 else 0
pct_s2 = (s2_area / total_area * 100) if total_area > 0 else 0
pct_s3 = (s3_area / total_area * 100) if total_area > 0 else 0
pct_n  = (n_area  / total_area * 100) if total_area > 0 else 0
# -------------------- LAYOUTING ---------------------

col_map, col_stat = st.columns([7, 3], gap="small")

# -------------------- LEFT: MAP ---------------------

with col_map:
        Map = geemap.Map(
            draw_ctrl=False,
            measure_ctrl=False,
            fullscreen_ctrl=True,
            zoom_control=True,
        )
        Map.options["doubleClickZoom"] = False
        
        # BASEMAP
        try:
            Map.add_basemap(DEFAULT_BASEMAP)
        except Exception:
            Map.add_basemap("OpenStreetMap")
        
        # LSA LAYER
        Map.addLayer(filtered_image, map_vis, f"LSA - {st.session_state.durian_class}")

        # BATAS DESA
        if st.session_state.durian_desa == "Semua Desa":
            Map.addLayer(
                desaAgats.style(color="00e676", fillColor="00000000", width=1),
                {}, "Batas Desa",
            )
        else:
            Map.addLayer(
                desaAgats.style(color="ffffff40", fillColor="00000000", width=0.5),
                {}, "Semua Desa",
            )
            Map.addLayer(
                desa_fc.style(color="ffeb3b", fillColor="ffeb3b1a", width=2.5),
                {}, f"Desa: {st.session_state.durian_desa}",
            )
 
        Map.centerObject(map_center_obj, zoom_level)

        # LEGEND
        Map.add_legend(title="Kesesuaian Lahan (FAO 1976)", legend_dict=LEGEND_DICT)

        # ----------------- FLOATING STATS ON CLICK ---------------------------------
 
        _cp = st.session_state.get("durian_clicked_point")
        if isinstance(_cp, dict) and "lat" in _cp and "lon" in _cp:
            folium.CircleMarker(
                location=[_cp["lat"], _cp["lon"]],
                radius=7,
                color="#ffffff",
                weight=2,
                fill=True,
                fill_color="#2563eb",
                fill_opacity=0.85,
                tooltip=f"📍 {_cp['lat']:.4f}, {_cp['lon']:.4f}",
            ).add_to(Map)


        # ----------------- RENDER MAP -----------------------

        map_key = (
            f"durian_{st.session_state.durian_method}_"
            f"{st.session_state.durian_desa}_"
            f"{st.session_state.durian_class}"
        )

        map_data = st_folium(
            Map,
            height=MAP_HEIGHT,
            width=None,
            returned_objects=["last_clicked"],
            key=map_key,
        )

        # ------------- CLICK EVENT ---------------------

        clicked = map_data.get("last_clicked")
        if clicked:
            new_pt = {"lat": clicked["lat"], "lon": clicked["lng"]}
            if new_pt != st.session_state.durian_clicked_point:
                st.session_state.durian_clicked_point = new_pt
                with st.spinner("Mengambil data parameter lokasi…"):
                    try:
                        point  = ee.Geometry.Point([new_pt["lon"], new_pt["lat"]])
                        stats  = build_parameter_stack().reduceRegion(
                            reducer=ee.Reducer.first(),
                            geometry=point,
                            scale=90,
                            maxPixels=1e13,
                        ).getInfo()
                        st.session_state.durian_click_stats = stats
                    except Exception as err:
                        st.session_state.durian_click_stats = None
                        st.warning(f"Gagal mengambil data GEE: {err}")
                
                st.rerun()
 
 


# -------------------- RIGHT: STATS ---------------------

with col_stat:
    stat_container = st.container(height=700)

    def _section(label):
        st.markdown(f"""
        <div style="font-size:1rem;font-weight:600;text-transform:uppercase;
                    letter-spacing:1px;color:#484f58;margin:10px 0 5px">
            {label}
        </div>""", unsafe_allow_html=True)
    
    # -------------------- LUAS AREA ---------------------
    with stat_container:
        _section("Statistik Luas")
        st.metric("Total Luas", f"{total_area:,.2f} ha")

        m1, m2 = st.columns(2)
        with m1:
            st.metric(
                label="S1 - Sangat Sesuai",
                value=f"{s1_area:,.2f} ha",
                delta=f"{pct_s1:.1f}%",
                delta_arrow="off"
            )
            st.metric(
                label="S3 - Sesuai Marginal",
                value=f"{s3_area:,.2f} ha",
                delta=f"{pct_s3:.1f}%",
                delta_arrow="off"
            )
        with m2:
            st.metric(
                label="S2 - Cukup Sesuai",
                value=f"{s2_area:,.2f} ha",
                delta=f"{pct_s2:.1f}%",
                delta_arrow="off"
            )

            st.metric(
                label="N - Tidak Sesuai",
                value=f"{n_area:,.2f} ha",
                delta=f"{pct_n:.1f}%",
                delta_arrow="off"
            )
            
        st.divider()
        
        # -------------------- PIE CHART ---------------------
        if total_area > 0:
            _section("Proporsi Kelas")

            pie_df = df_area[df_area["Area (ha)"] > 0].copy()
            fig_pie = px.pie(
                pie_df,
                names="Kelas",
                values="Area (ha)",
                color="Kelas",
                color_discrete_map=CLASS_COLOR,
                hole=0.42,
            )
            fig_pie.update_traces(
                textposition="inside",
                textinfo="percent+label",
                textfont_size=11,
            )
            fig_pie.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#7d8590", size=11, family="Segoe UI"),
                margin=dict(l=0, r=0, t=10, b=0),
                showlegend=True,
                height=220,
                legend=dict(
                    orientation="h", yanchor="bottom", y=-0.28,
                    xanchor="center", x=0.5,
                    font=dict(size=10), bgcolor="rgba(0,0,0,0)",
                ),
            )
            st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})
        
        # -------------------- BAR CHART ---------------------
        if total_area > 0:
            _section("Perbandingan Luas")

            fig_bar = px.bar(
                df_area[df_area["Area (ha)"] > 0],
                x="Kelas", y="Area (ha)",
                color="Kelas",
                color_discrete_map=CLASS_COLOR,
                text_auto=".0f",
            )
            fig_bar.update_traces(textposition="outside", textfont_size=10)
            fig_bar.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#7d8590", size=11, family="Segoe UI"),
                margin=dict(l=0, r=0, t=10, b=0),
                showlegend=False,
                height=190,
                yaxis=dict(showgrid=True, gridcolor="#21262d", title="Luas (ha)"),
                xaxis=dict(title=""),
            )
            st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

        st.divider()
        
        # -------------------- CLASS DESCRIPTION ---------------------
        _section("Deskripsi Kelas")

        active_label = VAL_TO_LABEL.get(sel_class_val) 
        for cls_key, info in CLASS_DESC.items():
            if active_label and cls_key != active_label:
                continue
            color = CLASS_COLOR[cls_key]
            st.markdown(f"""
            <div style="border-left:3px solid {color};padding:7px 10px;margin-bottom:7px;
                        background:rgba(255,255,255,.02);border-radius:0 6px 6px 0">
                <div style="font-weight:600;font-size:.8rem;margin-bottom:2px">
                    {info['title']}
                </div>
                <div style="font-size:1rem;color:#7d8590;line-height:1.5">
                    {info['desc']}
                </div>
            </div>""", unsafe_allow_html=True)
    
        # -------------------- PIXEL INFO ---------------------
        cp = st.session_state.durian_clicked_point
        cs = st.session_state.durian_click_stats
    
        if cp:
            _section("Parameter Titik")
    
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:8px;padding:6px 10px;
                        background:#e7e7e7;border:1px solid #ababab;border-radius:8px;
                        margin-bottom:8px">
                <span style="font-size:1rem;color:#7d8590;font-family:monospace">
                    {cp['lat']:.5f}, {cp['lon']:.5f}
                </span>
            </div>""", unsafe_allow_html=True)
    
            if cs:
                param_rows = []
                for band, label in PARAM_BAND_NAMES.items():
                    val  = cs.get(band)
                    disp = f"{float(val):.2f}" if val is not None else "–"
                    param_rows.append({"Parameter": label, "Nilai": disp})
    
                st.dataframe(
                    pd.DataFrame(param_rows).set_index("Parameter"),
                    use_container_width=True,
                )
            else:
                st.info("Data parameter tidak tersedia untuk lokasi ini.")