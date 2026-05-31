from config import ee, st, pd, ASSETS

desaAgats = ee.FeatureCollection(ASSETS + "DesaAgats")

@st.cache_data
def get_desa_list():
    desa_list = desaAgats.aggregate_array("NAMOBJ").getInfo()
    desa_list.sort()
    return desa_list

@st.cache_data(show_spinner=False)
def calculate_area_stats(asset_key, image, region_geometry, region_key="all", method_key="WA"):

    area_image = ee.Image.pixelArea().divide(10000).rename("area")

    classes = {
        1: "N",
        2: "S3",
        3: "S2",
        4: "S1",
    }

    area_data = []

    for class_value, class_name in classes.items():
        class_mask = _image.eq(class_value)

        area = (
            area_image.updateMask(class_mask).reduceRegion(
                reducer=ee.Reducer.sum(),
                geometry=_region_geometry,
                scale=90,
                maxPixels=1e13,
                bestEffort=True,
            ).get("area")
        )

        try:
            area_ha = round(ee.Number(area).getInfo(), 2)
        except Exception:
            area_ha = 0.0

        area_data.append({
            "Kelas": class_name,
            "Area (ha)": area_ha,
        })

    return pd.DataFrame(area_data)

@st.cache_data(show_spinner=False)
def calculate_area_stats_kopi(asset_key, region_key="all", method_key="WA"):
    
    # Load image di DALAM fungsi berdasarkan asset_key
    VEGETATION = ASSETS + "classified_2025_2B_ESRI"
    veget_mask = ee.Image(VEGETATION).neq(1).And(ee.Image(VEGETATION).neq(2))
    image = ee.Image(asset_key).updateMask(veget_mask)

    desaAgats = ee.FeatureCollection(ASSETS + "DesaAgats")

    # Filter desa
    if region_key == "Semua Desa":
        region_geometry = desaAgats.geometry()
    else:
        desa_fc = desaAgats.filter(ee.Filter.eq("NAMOBJ", region_key))
        region_geometry = desa_fc.geometry()
        image = image.clip(desa_fc).updateMask(ee.Image.constant(1).clip(desa_fc))

    area_image = ee.Image.pixelArea().divide(10000).rename("area")
    classes = {1: "N", 2: "S3", 3: "S2", 4: "S1"}
    area_data = []

    for class_value, class_name in classes.items():
        class_mask = image.eq(class_value)
        area = (
            area_image.updateMask(class_mask).reduceRegion(
                reducer=ee.Reducer.sum(),
                geometry=region_geometry,
                scale=90,
                maxPixels=1e13,
                bestEffort=True,
            ).get("area")
        )
        try:
            area_ha = round(ee.Number(area).getInfo(), 2)
        except Exception:
            area_ha = 0.0
        area_data.append({"Kelas": class_name, "Area (ha)": area_ha})

    return pd.DataFrame(area_data)