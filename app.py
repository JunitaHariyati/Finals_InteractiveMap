import ee
import streamlit as st

st.set_page_config(page_title="My Streamlit App", layout="wide")

# ===================== INITIALIZE EARTH ENGINE ACCOUNT =======================
try:
    ee.Initialize(project="ee-junitahariyati0717")
except Exception:
    ee.Authenticate()
    ee.Initialize(project="ee-junitahariyati0717")

# ===================== CSS =======================
st.markdown("""
<style>
#MainMenu, footer, header {{ visibility: hidden; }}
.stDeployButton {{ display: none; }}
[data-testid="stToolbar"] {{ display: none; }}
            
[data-testid="stSidebarNav"] {
    display: none;
}
</style>
""", unsafe_allow_html=True)

# ===================== PAGES =======================
home = st.Page("pages/Home.py", title="Home", default=True)
trend_all = st.Page("pages/LandCover/Trend_All.py", title="Perbandingan Semua Tahun")
compare_trend = st.Page("pages/LandCover/Compare.py", title="Perbandingan 2 Tahun")
avocado = st.Page("pages/LSA/Alpukat.py", title="Alpukat")
cashew = st.Page("pages/LSA/Cashew.py", title="Jambu Mete")
citrus = st.Page("pages/LSA/Citrus.py", title="Jeruk")
cocoa = st.Page("pages/LSA/Cocoa.py", title="Kakao")
coconut = st.Page("pages/LSA/Coconut.py", title="Kelapa")
durian = st.Page("pages/LSA/Durian.py", title="Durian")
coffee = st.Page("pages/LSA/Kopi_Liberika.py", title="Kopi Liberika")

# ===================== NAVIGATION BAR =======================
with st.sidebar:

    st.markdown("### Halaman Utama")
    st.page_link(home)

    st.markdown('### Analisis Tutupan Lahan')
    st.page_link(trend_all)
    st.page_link(compare_trend)

    st.markdown("### Analisis Kesesuaian Lahan")
    st.page_link(coconut)
    st.page_link(coffee)
    st.page_link(durian)
    st.page_link(cocoa)
    st.page_link(cashew)
    st.page_link(citrus)
    st.page_link(avocado)
    
# ===================== ROUTER =======================
pg = st.navigation([home, trend_all, compare_trend, coconut, coffee, durian, cocoa, cashew, citrus, avocado])

pg.run()