from config import ee, st, geemap, pd

st.set_page_config(page_title="LSA of Coffee", layout="wide")

st.title("Analisis Kesesuaian Lahan untuk Kopi Liberika")

# --- Projects Assets ID ---
assets = "projects/tugasakhir-473409/assets/"

# -------------------- FILTERING OPTION ---------------------

col1Opt, col2Opt, col3Opt = st.columns(3)

# -------------------- LSA METHOD OPTION ---------------------
with col1Opt:
    method = st.radio(
        "Pilih Metode LSA",
        ["Weighted Average", "Limiting Factor"],
        index=0,
        horizontal=True
    )

# ---- Assets ---
if method == "Limiting Factor":
    asset_id = assets + "LSA_liberica_coffee_LF_2025"
else:
    asset_id = assets + "LSA_liberica_coffee_WA_2025"

# Load image
image = ee.Image(asset_id)

# -------------------- DESA OPTION ---------------------

# Batas Desa
desaAgats = ee.FeatureCollection(assets + "DesaAgats")
desa_list = desaAgats.aggregate_array("NAMOBJ").getInfo()

desa_list.sort()

desa_options = ["Semua Desa"] + desa_list

with col2Opt:
    selected_desa = st.selectbox(
        "Pilih Desa",
        desa_options
    )

desa_geometry = desaAgats.filter(
    ee.Filter.eq("NAMOBJ", selected_desa)
)

# -------------------- LSA CLASS OPTION ---------------------
class_options = {
    "Semua Kelas": 0,
    "S1 - Sangat Sesuai": 4,
    "S2 - Cukup Sesuai": 3,
    "S3 - Sesuai Marginal": 2,
    "N - Tidak sesuai": 1
}

with col3Opt:
    selected_class = st.selectbox(
        "Pilih Kelas Keseuaian Lahan",
        list(class_options.keys())
)

selected_value = class_options[selected_class]

# -------------------- VISUALIZE ---------------------
class_vis = {
    'min': 1,
    'max': 4,
    'palette': [
        '#E24B4A',  # N
        '#EF9F27',  # S3
        '#97C459',  # S2
        '#1D9E75']  # S1
    , "opacity": 0.7
    }

single_class_palette = {
    1: ["#E24B4A"],
    2: ["#EF9F27"],
    3: ["#97C459"],
    4: ["#1D9E75"]
}

# Filter Class Map
if selected_value == 0:
    display_image = image
    map_vis = class_vis
else:
    display_image = image.updateMask(image.eq(selected_value))

    map_vis = {
        "min": selected_value,
        "max": selected_value,
        "palette": single_class_palette[selected_value],
        "opacity": 0.7
    }

# Filter Desa Map
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

# Legend
legend_dict = {
    "S1 - Sangat Sesuai": "#1D9E75",
    "S2 - Cukup Sesuai": "#97C459",
    "S3 - Sesuai Marginal": "#EF9F27",
    "N - Tidak Sesuai": "#E24B4A"
}

# -------------------- CALCULATE AREA ---------------------

# Pixel area in hectares
area_image = ee.Image.pixelArea().divide(10000).rename("area")

# Calculate area for each class
classes = {
    1: "N",
    2: "S3",
    3: "S2",
    4: "S1"
}

area_data = []

for class_value, class_name in classes.items():

    class_mask = image.eq(class_value)

    area = (
        area_image.updateMask(class_mask)
        .reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=region_geometry,
            scale=30,
            maxPixels=1e13
        ).get("area")
    )

    try:
        area_ha = round(ee.Number(area).getInfo(), 2)
    except:
        area_ha = 0

    area_data.append({
        "Kelas": class_name,
        "Area (ha)": area_ha
    })

df = pd.DataFrame(area_data)

if selected_value != 0:
    selected_label = classes[selected_value]
    df = df[df["Kelas"] == selected_label]

# -------------------- LAYOUTING CONTENT ---------------------

col1, col2 = st.columns([7, 3])

# Left Column

with col1:

    Map = geemap.Map(draw_ctrl=True)

    # Base Map
    Map.add_basemap("SATELLITE")

    # LSA Layer
    Map.addLayer(filtered_image, map_vis, selected_class)

    # Map by Desa
    if selected_desa == "Semua Desa":

        Map.addLayer(
            desaAgats.style(
                color="black",fillColor="00000000",width=1
            ),{},"Batas Desa"
        )

    else:

        Map.addLayer(
            desa_geometry.style(
                color="red",fillColor="00000000",width=3
            ),{},"Desa Terpilih"
        )

    Map.centerObject(map_center_object, zoom_level)

    Map.add_legend(
        title="Kelas Kesesuian (FAO 1976)",
        legend_dict=legend_dict
    )

    Map.to_streamlit(height=600)

# Right Column

with col2:

    st.subheader("Luas Area Kesesuaian")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    total_area = df["Area (ha)"].sum()

    st.metric(
        label="Total Luas (ha)",
        value=f"{total_area:,.2f}"
    )

    descriptions = {
        "S1": "Lahan sangat sesuai dengan faktor pembatas minimal.",
        "S2": "Lahan cukup sesuai dengan beberapa faktor pembatas yang masih dapat dikelola.",
        "S3": "Lahan sesuai marginal dengan faktor pembatas yang cukup signifikan.",
        "N": "Lahan tidak sesuai untuk budidaya kopi."
    }

    if selected_value != 0:
        st.subheader("Detail Kelas")
        st.info(descriptions[classes[selected_value]])