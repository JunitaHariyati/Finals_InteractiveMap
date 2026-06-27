# Library
from config import ASSETS
from utils.lsa_page import render_lsa_page
 
# ===================== MAIN PAGE =======================
render_lsa_page(
    commodity_id     = "cocoa",
    title            = "Analisis Kesesuaian Lahan - Kakao (2025)",
    asset_id         = ASSETS + "LSA_cocoa_WA_2025",
    vegetation_asset = ASSETS + "LC_L2_2025",
    desa_fc_asset    = ASSETS + "DesaAgats",
)