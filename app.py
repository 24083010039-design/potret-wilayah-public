from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Potret Wilayah | Public Demo",
    page_icon=":material/analytics:",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("Potret Wilayah")
st.caption("Urban-Rural Village Classification & Interactive BI")

st.warning(
    "DEMONSTRASI DATA SINTETIS. "
    "Seluruh wilayah dan angka bersifat fiktif, "
    "bukan statistik resmi BPS atau hasil penelitian."
)

html = (
    Path(__file__).resolve().parent / "index.html"
).read_text(encoding="utf-8")

components.html(html, height=1100, scrolling=True)

st.caption(
    "Prototipe akademik independen. "
    "Tidak mewakili publikasi resmi pemerintah."
)