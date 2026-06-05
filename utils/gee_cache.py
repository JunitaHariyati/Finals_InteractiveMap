from config import ee, st, pd, ASSETS, LC_PIXEL_MAP, LC_ASSET_BY_YEAR

# LOAD ROI
desaAgats = ee.FeatureCollection(ASSETS + "DesaAgats")

# FUNCTION TO COLLECT DESA LIST
@st.cache_data
def get_desa_list():
    desa_list = desaAgats.aggregate_array("NAMOBJ").getInfo()
    desa_list.sort()
    return desa_list

# FUNCTION TO CALCULATE TOTAL AREA FOR LSA
@st.cache_data(show_spinner=False)
def calculate_area_stats(asset_key, _image, _region_geometry, region_key="all", method_key="WA"):
    # CALCULATE AREA IN EVERY PIXEL
    area_image = ee.Image.pixelArea().divide(10000).rename("area")
    classes = {1: "N", 2: "S3", 3: "S2", 4: "S1"}
    area_data = []

    # LOOP FOR EVERY CLASS
    for class_value, class_name in classes.items():
        class_mask = _image.eq(class_value)
        # SUM TOTAL AREA FOR EVERY PIXEL IN REGION GEOMETRY
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
        # PUT INTO LIST
        area_data.append({"Kelas": class_name, "Area (ha)": area_ha})
    # CONVERT TO DATAFRAME
    return pd.DataFrame(area_data)

# CALCULATE TOTAL AREA FOR LIBERICA COFFEE
@st.cache_data(show_spinner=False)
def calculate_area_stats_kopi(asset_key, region_key="all", method_key="WA"):
    
    # LOAD IMAGE
    VEGETATION = ASSETS + "classified_2025_2B_ESRI"
    veget_mask = ee.Image(VEGETATION).neq(1).And(ee.Image(VEGETATION).neq(2))
    image = ee.Image(asset_key).updateMask(veget_mask)

    # FILTER BY DESA
    if region_key == "Semua Desa":
        region_geometry = desaAgats.geometry()
    else:
        desa_fc = desaAgats.filter(ee.Filter.eq("NAMOBJ", region_key))
        region_geometry = desa_fc.geometry()
        image = image.clip(desa_fc).updateMask(ee.Image.constant(1).clip(desa_fc))

    # CALCULATE AREA IN EVERY PIXEL
    area_image = ee.Image.pixelArea().divide(10000).rename("area")
    classes = {1: "N", 2: "S3", 3: "S2", 4: "S1"}
    area_data = []

    # LOOP FOR EVERY CLASS
    for class_value, class_name in classes.items():
        class_mask = image.eq(class_value)
        # SUM TOTAL AREA FOR EVERY PIXEL IN REGION GEOMETRY
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

    # CONVERT TO DATAFRAME
    return pd.DataFrame(area_data)

# CALCULATE TOTAL AREA FOR LAND COVER
@st.cache_data(show_spinner=False)
def calc_lc_area_year(year: int):
    # LOAD IMAGE BY YEAR
    img = ee.Image(LC_ASSET_BY_YEAR[year])
    # CALCULATE AREA IN EVERY PIXEL
    area_img = ee.Image.pixelArea().divide(10000).rename("area")
    rows = []
    # LOOP FOR EVERY LAND COVER CLASSES
    for val, label in LC_PIXEL_MAP.items():
        try:
            ha = round(
                ee.Number(
                    # SUM TOTAL AREA FOR EVERY PIXEL IN DESA AGATS GEOMETRY
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
        # PUT INTO LIST
        rows.append({"Kelas": label, "Area (ha)": ha, "Tahun": year})
    # CONVERT TO DATAFRAME
    return pd.DataFrame(rows)