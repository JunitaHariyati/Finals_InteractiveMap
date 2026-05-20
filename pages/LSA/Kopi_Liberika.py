from config import *
from utils.gee_cache import (get_desa_list, calculate_area_stats)
from utils.gee_info import (get_polygon_statistics)
from utils.gee_layers import (build_parameter_stack)

desaAgats = ee.FeatureCollection(ASSETS + "DesaAgats")

st.set_page_config(page_title="LSA of Coffee", layout="wide")

st.title("Analisis Kesesuaian Lahan untuk Kopi Liberika")

# Map Initialization
Map = geemap.Map(
    draw_ctrl=False, measure_ctrl=False, fullscreen_ctrl=True
)
Map.options["doubleClickZoom"] = False

# -------------------- FILTERING OPTION ---------------------
with st.container():
    st.markdown('<div class="filter-bar" style="flex-wrap:wrap;gap:16px;">', unsafe_allow_html=True)
    f1, f2, f3 = st.columns([1.4, 1.8, 1.8])
    
    # LSA METHOD
    with f1:
        method = st.radio(
        "Metode Analisis",
        ["Weighted Average", "Limiting Factor"],
        index=0,
        horizontal=True
    )
    
    # FILTERING DESA
    with f2:
        desa_list = get_desa_list()
        desa_options = ["Semua Desa"] + desa_list
        selected_desa = st.selectbox(
            "Filter Desa",options=desa_options,
            index=0
        )
    
    # FILTERING KELAS
    with f3:
        
        selected_class = st.selectbox(
            "Filter Kelas Kesesuaian Lahan",
            list(CLASS_OPTIONS.keys())
        )
        selected_value = CLASS_OPTIONS[selected_class]

    st.markdown("</div>", unsafe_allow_html=True)

# ---- Assets ---
if method == "Limiting Factor":
    asset_id = ASSETS + "LSA_liberica_coffee_LF_2025"
else:
    asset_id = ASSETS + "LSA_liberica_coffee_WA_2025"

vegetation = ee.Image(ASSETS + "classified_2025_2B_ESRI")
vegetMask = vegetation.neq(1).And(vegetation.neq(2))

# Load image
image = ee.Image(asset_id).updateMask(vegetMask)

# -------------------- FILTER CLASS ---------------------
# Filter Class Map
if selected_value == 0:
    display_image = image
    map_vis = CLASS_VIS
else:
    display_image = image.updateMask(image.eq(selected_value))

    map_vis = {
        "min": selected_value,
        "max": selected_value,
        "palette": SINGLE_CLASS_PALETTE[selected_value],
        "opacity": 0.7
    }

# -------------------- FILTER DESA ---------------------
if selected_desa == "Semua Desa":
    filtered_image = display_image
    region_geometry = desaAgats.geometry()
    map_center_object = desaAgats
    zoom_level = 11
else:
    desa_geometry = desaAgats.filter(
        ee.Filter.eq("NAMOBJ", selected_desa)
    )
    filtered_image = display_image.clip(
        desa_geometry
    )
    region_geometry = desa_geometry.geometry()
    map_center_object = desa_geometry
    zoom_level = 13

# -------------------- CALCULATE AREA ---------------------

df = calculate_area_stats(filtered_image, region_geometry)

classes = {
        1: "N",
        2: "S3",
        3: "S2",
        4: "S1"
    }

if selected_value != 0:
    selected_label = classes[selected_value]
    df = df[df["Kelas"] == selected_label]

# -------------------- MAP ONLY ---------------------

with st.container():
    Map.add_basemap(DEFAULT_BASEMAP)

    # LSA Layer
    Map.addLayer(filtered_image,map_vis,selected_class)

    # Batas Desa
    if selected_desa == "Semua Desa":

        Map.addLayer(
            desaAgats.style(
                color="green",fillColor="00000000",width=1,
            ),{},"Batas Desa"
        )

    else:
        Map.addLayer(
            desa_geometry.style(
                color="yellow",fillColor="00000000",width=1
            ),{},"Desa Terpilih"
        )
    Map.centerObject(map_center_object,zoom_level)

    #Legend
    Map.add_legend(
        title="Kelas Kesesuaian (FAO 1976)",
        legend_dict=LEGEND_DICT
    )

    # -------------------- STATISTIC ---------------------

    total_area = round(df["Area (ha)"].sum(), 2)

    s1_area = round(
        df[df["Kelas"] == "S1"]["Area (ha)"].sum(), 2
    )

    s2_area = round(
        df[df["Kelas"] == "S2"]["Area (ha)"].sum(), 2
    )

    s3_area = round(
        df[df["Kelas"] == "S3"]["Area (ha)"].sum(), 2
    )

    n_area = round(
        df[df["Kelas"] == "N"]["Area (ha)"].sum(), 2
    )

    class_html = f"""
    <div style="
        position: fixed;
        top: 20px;
        left: 20px;
        width: 320px;
        z-index:9999;

        background: rgba(255,255,255,0.92);
        backdrop-filter: blur(12px);

        border-radius: 18px;
        padding: 18px;

        box-shadow: 0 6px 25px rgba(0,0,0,0.25);

        font-family: Arial;
    ">

        <!-- HEADER -->

        <div style="
            display:flex;
            justify-content:space-between;
            align-items:center;
            margin-bottom:15px;
        ">

            <h3 style="
                margin:0;
                color:#1b4332;
            ">
            Statistik
            </h3>

            <button onclick="
                var x = document.getElementById('parameterContent');

                if (x.style.display === 'none') {{
                    x.style.display = 'block';
                }} else {{
                    x.style.display = 'none';
                }}
            "

            style="
                border:none;
                background:#1b4332;
                color:white;
                border-radius:8px;
                padding:6px 12px;
                cursor:pointer;
                font-size:12px;
            ">
            Toggle
            </button>

        </div>

        <!-- CONTENT -->

        <div id="parameterContent">

            <div style="
                border-left:8px solid #1D9E75;
                padding-left:10px;
                margin-bottom:10px;
            ">
                <b>S1</b><br>
                {s1_area} Ha
            </div>

            <div style="
                border-left:8px solid #97C459;
                padding-left:10px;
                margin-bottom:10px;
            ">
                <b>S2</b><br>
                {s2_area} Ha
            </div>

            <div style="
                border-left:8px solid #EF9F27;
                padding-left:10px;
                margin-bottom:10px;
            ">
                <b>S3</b><br>
                {s3_area} Ha
            </div>

            <div style="
                border-left:8px solid #E24B4A;
                padding-left:10px;
                margin-bottom:10px;
            ">
                <b>N</b><br>
                {n_area} Ha
            </div>

            <hr>

            <div style="
                background:#e8f5e9;
                border-radius:12px;
                padding:12px;
                text-align:center;
            ">
                <b>Total Luas</b><br>
                {total_area} Ha
            </div>

        </div>

    </div>
    """

    Map.get_root().html.add_child(
        folium.Element(class_html)
    )

# -------------------- CLICK EVENT ---------------------

clicked_point = None

if "clicked_point" in st.session_state:
    clicked_point = st.session_state["clicked_point"]

# -------------------- GET CLICK ---------------------

map_data = st_folium(Map,height=700,width=None,returned_objects=["last_clicked"])
clicked = map_data.get("last_clicked")

# # DEBUG CLICK
# st.write("DEBUG map_data:", map_data)
# st.write("DEBUG clicked:", clicked)

if clicked:
    st.session_state["clicked_point"] = {
        "lat": clicked["lat"],
        "lon": clicked["lng"]
    }
    clicked_point = st.session_state["clicked_point"]
    
# -------------------- EXTRACT PARAMETER VALUE ---------------------
if clicked_point:

    lat = clicked_point["lat"]
    lon = clicked_point["lon"]

    point = ee.Geometry.Point([lon, lat])
    stacked_image = build_parameter_stack()
    stats = stacked_image.reduceRegion(
        reducer=ee.Reducer.first(),
        geometry=point,
        scale=90
    ).getInfo()

    parameter_names = {
        "rainfall": "Curah Hujan",
        "temperature": "Suhu",
        "humidity": "Kelembaban",
        "elevation": "Elevasi",
        "slope_pct": "Lereng",
        "cec": "CEC",
        "cn": "C/N Ratio",
        "ph": "pH Tanah",
        "clay": "Kadar Liat",
        "sand": "Kadar Pasir",
        "silt": "Kadar Debu"
    }

    parameter_rows = ""

    for key, label in parameter_names.items():

        value = stats.get(key)

        if value is None:
            display_value = "-"
        else:
            try:
                display_value = round(float(value), 2)
            except:
                display_value = value

        parameter_rows += f"""
        <div style="
            display:flex;
            justify-content:space-between;
            padding:8px 0;
            border-bottom:1px solid #eeeeee;
        ">
            <span>{label}</span>
            <b>{display_value}</b>
        </div>
        """

    st.markdown(
        f"""
        <div style="
            position: fixed;
            bottom: 30px;
            right: 20px;
            width: 340px;
            z-index: 9999;

            background: rgba(255,255,255,0.96);
            backdrop-filter: blur(12px);

            border-radius: 18px;
            padding: 18px;

            box-shadow: 0 6px 25px rgba(0,0,0,0.25);

            font-family: Arial;

            max-height: 500px;
            overflow-y:auto;
        ">

        <h3 style="
            margin-top:0;
            color:#1b4332;
        ">
        📍 Informasi Lokasi
        </h3>

        <div style="
            background:#f5f5f5;
            padding:10px;
            border-radius:10px;
            margin-bottom:15px;
        ">

        <b>Latitude:</b> {round(lat,6)} <br>
        <b>Longitude:</b> {round(lon,6)}

        </div>

        {parameter_rows}

        </div>
        """,
        unsafe_allow_html=True
    )