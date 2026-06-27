# Library
from config import ASSETS
from utils.lsa_page import render_lsa_page
 
# ===================== MAIN PAGE =======================
render_lsa_page(
    commodity_id     = "liberica_coffee",
    title            = "Analisis Kesesuaian Lahan - Kopi Liberika (2025)",
    asset_id         = ASSETS + "LSA_liberica_coffee_WA_2025",
    vegetation_asset = ASSETS + "LC_L2_2025",
    desa_fc_asset    = ASSETS + "DesaAgats",
    extra_methods    = ["Limiting Factor"],
    lf_asset_id      = ASSETS + "LSA_liberica_coffee_LF_2025",
)