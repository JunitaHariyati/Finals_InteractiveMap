# Library
from config import ASSETS
from utils.lsa_page import render_lsa_page
 
# ===================== MAIN PAGE =======================
render_lsa_page(
    commodity_id     = "durian",
    title            = "Analisis Kesesuaian Lahan - Durian (2025)",
    asset_id         = ASSETS + "LSA_durian_WA_2025",
    vegetation_asset = ASSETS + "LC_L2_2025",
    desa_fc_asset    = ASSETS + "DesaAgats",
)