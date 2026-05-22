from config import ee, st, pd, ASSETS

desaAgats = ee.FeatureCollection(ASSETS + "DesaAgats")

@st.cache_data
def get_desa_list():
    desa_list = desaAgats.aggregate_array("NAMOBJ").getInfo()
    desa_list.sort()
    return desa_list

@st.cache_data(show_spinner=False)
def calculate_area_stats(asset_key, _image, _region_geometry, region_key="all", method_key="WA"):

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