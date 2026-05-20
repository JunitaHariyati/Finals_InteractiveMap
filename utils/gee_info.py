from config import ee, st, ASSETS
from utils.gee_layers import build_parameter_stack

@st.cache_data(show_spinner=False)
def get_polygon_statistics(desa_name):
    parameter_stack = build_parameter_stack
    desaAgats = ee.FeatureCollection(ASSETS + "DesaAgats")

    desa_geometry = desaAgats.filter(
        ee.Filter.eq("NAMOBJ", desa_name)
    ).geometry()

    stats = parameter_stack.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=desa_geometry,
        scale=90,
        maxPixels=1e13
    ).getInfo()

    return stats