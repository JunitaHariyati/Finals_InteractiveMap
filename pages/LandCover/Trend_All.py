from config import *
from utils.gee_cache import calc_lc_area_year
import streamlit.components.v1 as components

# ===================== INITIALIZATION =======================
YEARS = [2020, 2021, 2022, 2023, 2024, 2025]
_COLOR = LC_COLOR 
load_css()

# ===================== HEADER TITLE =======================
st.markdown("""
    <span style="font-size:3rem;font-weight:800;color:#1a2332;">Perubahan Tutupan Lahan Distrik Agats (2020-2025)</span>
""", unsafe_allow_html=True)

# ===================== LOAD IMAGE =======================
desaAgats = ee.FeatureCollection(ASSETS + "DesaAgats")

# ===================== CALCULATE TOTAL AREA IN 2020-2025 =======================
with st.spinner("Menghitung statistik..."):
    dfs = []
    for year in YEARS:
        df = calc_lc_area_year(year)
        dfs.append(df)
# COMBINE ALL YEAR
df_all = pd.concat(dfs, ignore_index=True)

# ===================== LAYOUTING =======================
# CHART | STATS

st.markdown("---")
col_left, col_right = st.columns([7, 3], gap="small")

# ===================== CHART (LEFT) =======================
with col_left:
    # TITLE
    st.subheader("Grafik Perubahan Luas Tutupan Lahan 2020-2025")

    # LINE CHART
    fig_line = px.line(
        df_all,x="Tahun",y="Area (ha)",
        color="Kelas",color_discrete_map=LC_COLOR,markers=True,
    )

    fig_line.update_traces(
        line_width=3,marker_size=8,
    )

    fig_line.update_layout(
        height=600, xaxis_title="Tahun", yaxis_title="Luas (ha)",
    )

    # ADD CHART TO PAGE
    st.plotly_chart(
        fig_line,
        use_container_width=True,
        config={"displayModeBar": False},
        key="trend_line_chart"
    )

    st.markdown("<br>", unsafe_allow_html=True)

# ===================== STATS (RIGHT) =======================
def _section_label(text: str, margin_top: str = "10px"):
    st.markdown(f"""
    <div style="font-size:1rem;font-weight:700;text-transform:uppercase;
                letter-spacing:1px;color:#1a2332;margin:{margin_top} 0 5px;
                padding-bottom:3px;border-bottom:1px solid #e2e8f0;">
        {text}
    </div>""", unsafe_allow_html=True)

with col_right:
    stat_cont = st.container(height=650)
    with stat_cont:
        # ===================== TOTAL AREA =======================
        st.markdown("### Statistik Wilayah")

        total_2025 = (
            df_all[df_all["Tahun"] == 2025]["Area (ha)"].sum()
        )

        st.metric(
            "Total Luas 2025",f"{total_2025:,.1f} ha"
        )

        pivot_df = (
            df_all.pivot(
                index="Kelas", columns="Tahun",values="Area (ha)"
            )
        )

        change_df = pivot_df[2025] - pivot_df[2020]

        # ===================== TOTAL AREA CHANGES =======================
        _section_label(f"Luas Kelas - 2020 vs 2025")

        pivot_df = (
            df_all.pivot(index="Kelas", columns="Tahun", values="Area (ha)").fillna(0)
        )

        first_year = min(YEARS)
        last_year  = max(YEARS)

        change_df = pd.DataFrame({
            "Kelas": pivot_df.index,
            "Awal": pivot_df[first_year],
            "Akhir": pivot_df[last_year],
        })

        change_df["Delta"] = change_df["Akhir"] - change_df["Awal"]

        change_df = change_df.sort_values(
            "Akhir", ascending=False
        )

        total_last = change_df["Akhir"].sum()

        html_cards = """
        <style>
            * {
                font-family: "Source Sans", sans-serif;
            }
        </style>
        """
        
        for _, row in change_df.iterrows():
            cls      = row["Kelas"]
            ha_awal  = row["Awal"]
            ha_akhir = row["Akhir"]
            delta    = row["Delta"]

            color = _COLOR.get(cls, "#888")
            arrow = "▲" if delta > 0 else "▼" if delta < 0 else "-"
            d_col = "#15803d" if delta > 0 else "#b91c1c" if delta < 0 else "#64748b"

            html_cards += f"""
            <div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:8px;
                        padding:10px 12px;margin-bottom:6px;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
                    <div style="display:flex;align-items:center;gap:8px;">
                        <div style="width:10px;height:10px;border-radius:2px;background:{color};"></div>
                        <span style="font-size:0.85rem;font-weight:600;color:#1a2332;">{cls}</span>
                    </div>
                    <span style="font-size:0.8rem;font-weight:700;color:{d_col};">
                        {arrow} {abs(delta):,.1f} ha
                    </span>
                </div>
                <div style="font-size:0.72rem;color:#64748b;display:flex;justify-content:space-between;">
                    <span>{first_year}: {ha_awal:,.1f} ha</span>
                    <span>{last_year}: {ha_akhir:,.1f} ha</span>
                </div>
            </div>
            """

        components.html(html_cards, height=len(change_df) * 65, scrolling=True)
