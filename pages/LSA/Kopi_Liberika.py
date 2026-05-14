from config import ee, st, geemap, pd

st.set_page_config(page_title="LSA of Coffee", layout="wide")

st.title("Analisis Kesesuaian Lahan untuk Kopi Liberika")

# --- Projects Assets ID ---
assets = "projects/tugasakhir-473409/assets/"

# --- Radio Button ---
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

# --- Class Option ---
class_options = {
    "Semua Kelas": 0,
    "S1 - Sangat Sesuai": 4,
    "S2 - Cukup Sesuai": 3,
    "S3 - Sesuai Marginal": 2,
    "N - Tidak sesuai": 1
}

selected_class = st.selectbox(
    "Lihat Detail Kelas",
    list(class_options.keys())
)

selected_value = class_options[selected_class]

# --- Visualize ---
class_vis = {
    'min': 1,
    'max': 4,
    'palette': [
        '#E24B4A',  # N
        '#EF9F27',  # S3
        '#97C459',  # S2
        '#1D9E75']  # S1
    }

single_class_palette = {
    1: ["#E24B4A"],
    2: ["#EF9F27"],
    3: ["#97C459"],
    4: ["#1D9E75"]
}

# Filter Image
if selected_value == 0:
    display_image = image
    map_vis = class_vis
else:
    display_image = image.updateMask(image.eq(selected_value))

    map_vis = {
        "min": selected_value,
        "max": selected_value,
        "palette": single_class_palette[selected_value]
    }

# Legend
legend_dict = {
    "S1 - Sangat Sesuai": "#1D9E75",
    "S2 - Cukup Sesuai": "#97C459",
    "S3 - Sesuai Marginal": "#EF9F27",
    "N - Tidak Sesuai": "#E24B4A"
}

# --- CALCULATE AREA ---

# Pixel area in hectares
area_image = ee.Image.pixelArea().divide(10000).rename("area")

# Calculate area for each class
classes = {
    1: "N - Tidak Sesuai",
    2: "S3 - Sesuai Marginal",
    3: "S2 - Cukup Sesuai",
    4: "S1 - Sangat Sesuai"
}

area_data = []

for class_value, class_name in classes.items():

    class_mask = image.eq(class_value)

    area = (
        area_image
        .updateMask(class_mask)
        .reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=image.geometry(),
            scale=30,
            maxPixels=1e13
        )
        .get("area")
    )

    try:
        area_ha = round(ee.Number(area).getInfo(), 2)
    except:
        area_ha = 0

    area_data.append({
        "Class": class_name,
        "Area (ha)": area_ha
    })

df = pd.DataFrame(area_data)

if selected_value != 0:
    selected_label = classes[selected_value]
    df = df[df["Class"] == selected_label]

# --- LAYOUTING ---

col1, col2 = st.columns([1, 1])

# Left Column

with col1:

    Map = geemap.Map(draw_ctrl=True)


    # Load asset
    composite_id = assets + 'compositeFull_2025'
    composite = ee.Image(composite_id)

    # Visualization
    viz_params = {
        'bands': ['B4', 'B3', 'B2'],
        'min': 0,
        'max': 0.3
    }

    Map.addLayer(composite, viz_params, 'Agats Composite')
    Map.addLayer(display_image, map_vis, selected_class)
    Map.centerObject(display_image, 11)

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