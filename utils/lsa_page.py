from config import *
from utils.gee_cache import (get_desa_list, calculate_area_stats)
from utils.gee_layers import (build_parameter_stack)

# FUNCTION TO BUILD LSA PAGE
# PARAMETERS:
#   commodity_id: Commodity Name Identifier
#   title       : Page Title
#   asset_id    : GEE Assets ID for Suitability Image
#   vegetation_asset: GEE Assets ID for Vegetation Mask
#   desa_fc_asset : GEE Assets ID for Geometry (ROI)
#   extra_methods : additional method for liberica coffee analysis

def render_lsa_page(
    commodity_id: str,
    title: str,
    asset_id: str,
    vegetation_asset: str,
    desa_fc_asset: str,
    extra_methods: list = [],
    lf_asset_id : str = None
):
    # ===================== INITIALIZATION =======================
    # LOAD ASSETS
    desaAgats  = ee.FeatureCollection(desa_fc_asset)
    vegetation = vegetation_asset

    # SESSION STATE KEY PREFIX
    _p = commodity_id + "_"

    # SESSION STATE DEFAULT
    _defaults = {
        _p + "method":        "Weighted Average",
        _p + "desa":          "Semua Desa",
        _p + "clicked_point": None,
        _p + "click_stats":   None,
    }
    # SET SESSION STATE
    for _k, _v in _defaults.items():
        if _k not in st.session_state:
            st.session_state[_k] = _v
    load_css()

    # CONFIG
    methods = ["Weighted Average"] + extra_methods

    # ===================== MAIN PAGE =======================
    # HEADER
    st.title(title)

    # ===================== FILTER BAR =======================
    with st.container():
        if commodity_id != "liberica_coffee":
            fc1, fc2, fc3, fc4 = st.columns([1.8, 2, 2, 4], gap="medium")
        else:
            fc1, fc2, fc3, fc4 = st.columns([3, 2, 2, 2], gap="medium")
        # FILTER METHOD
        with fc1:
            method = st.radio(
                "METODE ANALISIS",
                methods,
                index=0,
                horizontal=True,
                key="w_" + commodity_id + "_method",
            )
            if method != st.session_state[_p + "method"]:
                st.session_state[_p + "method"]        = method
                st.session_state[_p + "clicked_point"] = None
                st.session_state[_p + "click_stats"]   = None
 
        # FILTER DESA
        with fc2:
            desa_list    = get_desa_list()
            desa_options = ["Semua Desa"] + desa_list
            sel_desa = st.selectbox(
                "WILAYAH DESA",
                desa_options,
                index=desa_options.index(st.session_state[_p + "desa"])
                      if st.session_state[_p + "desa"] in desa_options else 0,
                key="w_" + commodity_id + "_desa",
            )
            if sel_desa != st.session_state[_p + "desa"]:
                st.session_state[_p + "desa"]          = sel_desa
                st.session_state[_p + "clicked_point"] = None
                st.session_state[_p + "click_stats"]   = None
 
    st.markdown("<div style='margin-bottom:10px'></div>", unsafe_allow_html=True)
 
    # CHECK IF METHOD LIMITING FACTOR
    if method == "Limiting Factor" and lf_asset_id is not None:
        asset_id = lf_asset_id   # CHANGE ASSET_ID
    else:
        asset_id = asset_id

    # MASK VEGETATION EXCEPT SELECTED CLASSES
    veget_mask = ee.Image(vegetation).neq(1).And(ee.Image(vegetation).neq(2))
    image_raw  = ee.Image(asset_id).updateMask(veget_mask)
 
    # ===================== FILTER DESA =======================
 
    # IF NOT SELECTED
    if st.session_state[_p + "desa"] == "Semua Desa":
        # DISPLAY ALL DESA
        filtered_image  = image_raw
        region_geometry = desaAgats.geometry()
        map_center_obj  = desaAgats
        zoom_level      = 11
        desa_fc         = None
    else:
        # UPDATE IMAGE BY SELECTED DESA
        desa_fc        = desaAgats.filter(ee.Filter.eq("NAMOBJ", st.session_state[_p + "desa"]))
        filtered_image = image_raw.clip(desa_fc).updateMask(
            ee.Image.constant(1).clip(desa_fc)
        )
        region_geometry = desa_fc.geometry()
        map_center_obj  = desa_fc
        zoom_level      = 15
 
    # ===================== CALCULATE TOTAL AREA =======================
    with st.spinner("Menghitung statistik luas…"):
        # CALL FUNCTION
        df_area = calculate_area_stats(
            asset_key=asset_id,
            _image=filtered_image,
            _region_geometry=region_geometry,
            region_key=st.session_state[_p + "desa"],
            method_key=st.session_state[_p + "method"],
        )
 
    # TOTAL AREA BY SUITABILITY CLASS
    total_area = round(df_area["Area (ha)"].sum(), 2)
    s1_area    = round(df_area[df_area["Kelas"] == "S1"]["Area (ha)"].sum(), 2)
    s2_area    = round(df_area[df_area["Kelas"] == "S2"]["Area (ha)"].sum(), 2)
    s3_area    = round(df_area[df_area["Kelas"] == "S3"]["Area (ha)"].sum(), 2)
    n_area     = round(df_area[df_area["Kelas"] == "N"]["Area (ha)"].sum(), 2)
 
    # PERCENTAGE TOTAL AREA BY SUITABILITY CLASS
    pct_s1 = (s1_area / total_area * 100) if total_area > 0 else 0
    pct_s2 = (s2_area / total_area * 100) if total_area > 0 else 0
    pct_s3 = (s3_area / total_area * 100) if total_area > 0 else 0
    pct_n  = (n_area  / total_area * 100) if total_area > 0 else 0
 
    # ===================== LAYOUTING =======================
    # MAP | STATS
    col_map, col_stat = st.columns([7, 3], gap="small")
 
    # ===================== MAP (LEFT) =======================
    with col_map:
        Map = geemap.Map(
            draw_ctrl=False,
            measure_ctrl=False,
            fullscreen_ctrl=True,
            zoom_control=True,
        )
        Map.options["doubleClickZoom"] = False

        # LSA LAYER
        for value, (name, color) in LSA_LAYERS.items():

            layer = filtered_image.updateMask(filtered_image.eq(value))

            Map.addLayer(
                layer,
                {
                    "min": value,
                    "max": value,
                    "palette": [color],
                },
                name,
            )

        # BATAS DESA
        if st.session_state[_p + "desa"] == "Semua Desa":
            Map.addLayer(
                desaAgats.style(color="ffffff", fillColor="00000000", width=1),
                {}, "Batas Desa",
            )
        else:
            Map.addLayer(
                desaAgats.style(color="ffffff40", fillColor="00000000", width=0.5),
                {}, "Semua Desa",
            )
            Map.addLayer(
                desa_fc.style(color="ffeb3b", fillColor="ffeb3b1a", width=2.5),
                {}, f"Desa: {st.session_state[_p + 'desa']}",
            )
        
        Map.centerObject(map_center_obj, zoom_level)
 
        # LEGEND
        Map.add_legend(title="Kelas Kesesuaian Lahan", legend_dict=LEGEND_DICT)
 
        # ===================== SET CIRCLE MARKER ON MAP =======================
        _cp = st.session_state.get(_p + "clicked_point")
        # IF CLICKED, MAKE CIRCLE MARKER
        if isinstance(_cp, dict) and "lat" in _cp and "lon" in _cp:
            folium.CircleMarker(
                location=[_cp["lat"], _cp["lon"]], radius=7, color="#ffffff",
                weight=2, fill=True, fill_color="#2563eb", fill_opacity=0.85,
                tooltip=f"📍 {_cp['lat']:.4f}, {_cp['lon']:.4f}",
            ).add_to(Map)
 
        # ===================== RENDER MAP =======================
        map_key = (
            f"{commodity_id}_"
            f"{st.session_state[_p + 'method']}_"
            f"{st.session_state[_p + 'desa']}"
        )

        # ADD LAYER CONTROL
        folium.LayerControl(collapsed=False, position="topright").add_to(Map)
 
        map_data = st_folium(
            Map, height=MAP_HEIGHT, width=None, returned_objects=["last_clicked"], key=map_key,
        )
 
        # ===================== CLICK EVENT =======================
        clicked = map_data.get("last_clicked")
        if clicked:
            # COLLECT LATITUDE AND LONGITUDE
            new_pt = {"lat": clicked["lat"], "lon": clicked["lng"]}
 
            # IF NEW POINT != LAST CLICKED POINT
            if new_pt != st.session_state[_p + "clicked_point"]:
                # SET STATE TO LATEST CLICKED POINT
                st.session_state[_p + "clicked_point"] = new_pt
                with st.spinner("Mengambil data parameter lokasi…"):
                    try:
                        # CALL FUNCTION TO GET POINT'S STATS
                        point = ee.Geometry.Point([new_pt["lon"], new_pt["lat"]])
                        stats = build_parameter_stack().reduceRegion(
                            reducer=ee.Reducer.first(),
                            geometry=point,
                            scale=90,
                            maxPixels=1e13,
                        ).getInfo()
                        st.session_state[_p + "click_stats"] = stats
                    except Exception as err:
                        st.session_state[_p + "click_stats"] = None
                        st.warning(f"Gagal mengambil data GEE: {err}")
 
                st.rerun()
 
    # ===================== STATS (RIGHT) =======================
    with col_stat:
        stat_container = st.container(height=700)
 
        def _section(label):
            st.markdown(f"""
            <div style="font-size:1.3rem;font-weight:600;text-transform:uppercase;
                        letter-spacing:1px;color:#484f58;margin:10px 0 5px">
                {label}
            </div>""", unsafe_allow_html=True)
 
        # ===================== TOTAL AREA =======================
        with stat_container:
            if st.session_state[_p + "desa"] == "Semua Desa":
                _section("Statistik Semua Desa")
            else:
                _section(f"Statistik Luas Desa {st.session_state[_p + 'desa']}")
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
 
            # ===================== PIE CHART =======================
            if total_area > 0:
                _section("Proporsi Kelas")
 
                pie_df  = df_area[df_area["Area (ha)"] > 0].copy()
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
                    font=dict(color="#7d8590", size=15, family="Segoe UI"),
                    margin=dict(l=0, r=0, t=10, b=0),
                    showlegend=True,
                    height=300,
                    legend=dict(
                        orientation="h", yanchor="bottom", y=-0.28,
                        xanchor="center", x=0.5,
                        font=dict(size=15), bgcolor="rgba(0,0,0,0)",
                    ),
                )
                st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})
 
            # ===================== BAR CHART =======================
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
                    font=dict(color="#7d8590", size=15, family="Segoe UI"),
                    margin=dict(l=0, r=0, t=10, b=0),
                    showlegend=False,
                    height=250,
                    yaxis=dict(showgrid=True, gridcolor="#21262d", title="Luas (ha)"),
                    xaxis=dict(title=""),
                )
                st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})
 
            st.divider()
 
            # ===================== CLASS DESCRIPTION =======================
            _section("Deskripsi Kelas")

            for cls_key, info in CLASS_DESC.items():
                color = CLASS_COLOR[cls_key]
                st.markdown(f"""
                <div style="border-left:3px solid {color};padding:7px 10px;margin-bottom:7px;
                            background:rgba(255,255,255,.02);border-radius:0 6px 6px 0">
                    <div style="font-weight:600;font-size:1.1rem;margin-bottom:2px">
                        {info['title']}
                    </div>
                    <div style="font-size:1rem;color:#7d8590;line-height:1.5">
                        {info['desc']}
                    </div>
                </div>""", unsafe_allow_html=True)
 
            # ===================== PIXEL POINT INFO STATS =======================
            cp = st.session_state[_p + "clicked_point"]
            cs = st.session_state[_p + "click_stats"]
 
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
                        disp = f"{float(val):.2f}" if val is not None else "-"
                        param_rows.append({"Parameter": label, "Nilai": disp})
 
                    st.dataframe(
                        pd.DataFrame(param_rows).set_index("Parameter"),
                        use_container_width=True,
                    )
                else:
                    st.info("Data parameter tidak tersedia untuk lokasi ini.")