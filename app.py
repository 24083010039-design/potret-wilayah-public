
import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Potret Wilayah",
    page_icon=":material/analytics:",
    layout="wide",
    initial_sidebar_state="auto"
)

D = json.loads(
    (Path(__file__).parent / "data.json")
    .read_text(encoding="utf-8")
)

P = D["province"]
REG = pd.DataFrame(D["regions"])
KPI = pd.DataFrame(D["comparisons"])
CAT = pd.DataFrame(D["catalog"])

NAVY = "#142B43"
TEAL = "#117C83"
BLUE = "#9CB9CD"

st.markdown("""
<style>
.stApp {
    background: #f5f7fa;
}
[data-testid="stSidebar"] {
    background: #142b43;
}
[data-testid="stSidebarNav"] a {
    color: #e5edf5 !important;
    border-radius: 7px;
}
[data-testid="stSidebarNav"] a[aria-current="page"] {
    background: #117c83 !important;
    color: white !important;
}
[data-testid="stSidebar"] p {
    color: #e5edf5;
}
[data-testid="stMetric"] {
    background: white;
    border: 1px solid #dce5ec;
    border-radius: 12px;
    padding: 17px;
}
.block-container {
    padding-top: 2.6rem;
    max-width: 1500px;
}
.hero {
    background: #142b43;
    color: white;
    border-radius: 15px;
    padding: 25px;
    margin-bottom: 24px;
}
.hero h1 {
    color: white;
    font-size: clamp(24px,3.4vw,36px);
    margin: 5px 0;
}
.hero p {
    color: #dce7f0;
    line-height: 1.6;
    margin-bottom: 0;
}
.eyebrow {
    color: #83d3d1;
    font-size: 12px;
    font-weight: bold;
    letter-spacing: 1.4px;
}
</style>
""", unsafe_allow_html=True)

def hero(title, text):
    st.markdown(
        f"""<div class="hero">
        <div class="eyebrow">
        POTRET WILAYAH | RESEARCH PUBLIC VIEW
        </div>
        <h1>{title}</h1><p>{text}</p>
        </div>""",
        unsafe_allow_html=True
    )

def chart(fig, height=430):
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=12,r=12,t=22,b=12),
        font=dict(color=NAVY,size=13),
        paper_bgcolor="white",
        plot_bgcolor="white",
        legend_title_text=""
    )
    st.plotly_chart(
        fig, use_container_width=True,
        config={"displaylogo":False}
    )

def note():
    st.caption(
        "PODES 2025 dan status resmi 2025, "
        "berdasarkan artefak penelitian. "
        "Agregat terpilih; bukan publikasi resmi BPS."
    )

def home():
    hero(
        "Ringkasan Wilayah",
        "Profil perkotaan dan perdesaan "
        "Kepulauan Bangka Belitung."
    )

    a,b,c,d = st.columns(4)

    a.metric("Desa / kelurahan",P["total"])
    b.metric("Perkotaan",P["urban"])
    c.metric("Perdesaan",P["rural"])
    d.metric("Kabupaten / kota",len(REG))

    left,right = st.columns([1,1.6])

    with left:
        st.subheader("Komposisi provinsi")
        fig = go.Figure(go.Pie(
            labels=["Perkotaan","Perdesaan"],
            values=[P["urban"],P["rural"]],
            hole=0.65,
            marker_colors=[TEAL,BLUE],
            textinfo="percent"
        ))
        chart(fig,350)

    with right:
        st.subheader("Cakupan desa per wilayah")
        fig = px.bar(
            REG.sort_values("total"),
            x="total",y="name",
            orientation="h",
            labels={
                "total":"Jumlah desa",
                "name":"Kabupaten/kota"
            },
            text_auto=True
        )
        fig.update_traces(marker_color=TEAL)
        chart(fig,350)

    st.subheader("Temuan deskriptif")

    st.write(
        f"Sebanyak **{P['urban']/P['total']*100:.1f}%** "
        "desa/kelurahan berstatus perkotaan."
    )

    st.write(
        "Kelompok perdesaan lebih besar "
        "daripada kelompok perkotaan."
    )

    biggest = REG.loc[REG.total.idxmax()]

    st.write(
        f"Wilayah dengan cakupan desa terbanyak "
        f"adalah {biggest['name']} "
        f"({biggest['total']} desa)."
    )

    note()

def contrast():
    hero(
        "Perkotaan vs Perdesaan",
        "Perbandingan indikator terpilih "
        "dengan denominator yang jelas."
    )

    domain = st.selectbox(
        "Domain",
        ["Semua"]+sorted(KPI.domain.unique()),
        key="contrast_domain"
    )

    frame = KPI if domain=="Semua" else KPI[
        KPI.domain==domain
    ]

    long = frame.melt(
        id_vars=["name"],
        value_vars=["urban","rural"],
        var_name="Kelompok",
        value_name="Persentase"
    )

    long["Kelompok"] = long.Kelompok.map({
        "urban":"Perkotaan",
        "rural":"Perdesaan"
    })

    fig = px.bar(
        long,
        x="Persentase",
        y="name",
        color="Kelompok",
        barmode="group",
        orientation="h",
        color_discrete_sequence=[TEAL,BLUE],
        labels={"name":"Indikator"}
    )

    fig.update_xaxes(range=[0,100])

    chart(fig,max(330,95*len(frame)))

    st.subheader("Selisih persentase")

    st.dataframe(
        frame[["name","urban","rural","gap"]]
        .rename(columns={
            "name":"Indikator",
            "urban":"Perkotaan (%)",
            "rural":"Perdesaan (%)",
            "gap":"Selisih (poin persentase)"
        }),
        hide_index=True,
        use_container_width=True
    )

    st.caption(
        "Denominator: 151 desa perkotaan dan "
        "242 desa perdesaan. Selisih dihitung "
        "sebelum pembulatan."
    )

    note()

def regional():
    hero(
        "Analisis Antarwilayah",
        "Eksplorasi cakupan wilayah penelitian "
        "tanpa publikasi sel kelompok kecil."
    )

    selected = st.multiselect(
        "Kabupaten/kota",
        REG.name.tolist(),
        default=REG.name.tolist(),
        key="regional_filter"
    )

    f = REG[REG.name.isin(selected)]

    a,b = st.columns(2)
    a.metric("Wilayah terpilih",len(f))
    b.metric("Total desa",int(f.total.sum()))

    if f.empty:
        st.info("Pilih minimal satu wilayah.")
        return

    fig = px.bar(
        f.sort_values("total",ascending=False),
        x="name",y="total",text_auto=True,
        labels={
            "name":"Kabupaten/kota",
            "total":"Jumlah desa"
        }
    )

    fig.update_traces(marker_color=TEAL)

    chart(fig)

    st.dataframe(
        f[["name","total"]].rename(columns={
            "name":"Kabupaten/kota",
            "total":"Jumlah desa"
        }),
        hide_index=True,
        use_container_width=True
    )

    note()

def spatial():
    hero(
        "Peta Spasial",
        "Batas administrasi kabupaten/kota "
        "dan cakupan desa penelitian."
    )

    features = D["geo"]["features"]

    if not features:
        st.warning(
            "Aset batas wilayah belum tersedia "
            "pada paket publik ini."
        )
        return

    selected = st.selectbox(
        "Sorot wilayah",
        ["Semua"]+REG.name.tolist(),
        key="map_region"
    )

    lookup = {
        r["code"]:r for r in D["regions"]
    }

    fig = go.Figure()

    for feature in features:
        info = lookup[feature["properties"]["code"]]
        geom = feature["geometry"]

        polygons = (
            [geom["coordinates"]]
            if geom["type"]=="Polygon"
            else geom["coordinates"]
        )

        active = (
            selected=="Semua"
            or selected==info["name"]
        )

        color = TEAL if active else "#b9cbd9"

        x,y = [],[]

        for polygon in polygons:
            for ring in polygon:
                x.extend(pt[0] for pt in ring)
                y.extend(pt[1] for pt in ring)
                x.append(None)
                y.append(None)

        fig.add_trace(go.Scattergl(
            x=x,y=y,mode="lines",
            line=dict(color=color,width=1.8),
            name=info["name"],
            text=[
                f"{info['name']}: "
                f"{info['total']} desa"
            ]*len(x),
            hoverinfo="text",
            showlegend=True
        ))

    fig.update_yaxes(
        scaleanchor="x",
        scaleratio=1,
        visible=False
    )

    fig.update_xaxes(visible=False)

    chart(fig,570)

    if selected!="Semua":
        n = int(
            REG.loc[
                REG.name==selected,"total"
            ].iloc[0]
        )
        st.metric(selected,n)

    st.caption(
        "Sumber batas wilayah: BIG, RBI 1:50.000, "
        "Administrasi Kabupaten/Kota, referensi 2023. "
        "Geometri disederhanakan untuk visualisasi. "
        "Tanpa basemap daring; bukan peta legal."
    )

def performance():
    hero(
        "Kinerja Model",
        "Evaluasi kandidat Logistic Regression "
        "dan Random Forest."
    )

    m = pd.DataFrame(D["models"])

    metric = st.selectbox(
        "Metrik evaluasi",
        [
            "MCC","Balanced accuracy",
            "Accuracy","ROC-AUC","PR-AUC"
        ],
        key="model_metric"
    )

    fig = px.bar(
        m,x="model",y=metric,
        color="model",
        color_discrete_sequence=[TEAL,BLUE],
        text_auto=".3f",
        labels={"model":"Model"},
        error_y="MCC_SD" if metric=="MCC" else None
    )

    fig.update_layout(showlegend=False)
    fig.update_yaxes(range=[0,1])

    chart(fig,390)

    st.dataframe(
        m,hide_index=True,
        use_container_width=True
    )

    st.caption(
        "Set A, 51 fitur, nested stratified CV, "
        "25 fold. Tanpa balancing. "
        "SD menggambarkan variasi antar-fold."
    )

    st.subheader("Validasi lintas kabupaten")

    if D["cross"]:
        cross = pd.DataFrame(D["cross"])

        st.dataframe(
            cross,hide_index=True,
            use_container_width=True
        )

        st.caption(
            "Leave-one-kabupaten-out. Metrik MCC "
            "dirata-ratakan hanya dari fold valid. "
            "Tidak ada prediksi desa yang dirilis."
        )
    else:
        st.info(
            "Ringkasan numerik cross-kabupaten "
            "belum dimasukkan ke paket publik."
        )

    st.warning(
        "Perbedaan performa tidak otomatis "
        "menetapkan model pemenang."
    )

def factors():
    hero(
        "Faktor Pembeda",
        "Kontribusi domain fitur terhadap "
        "performa model kandidat."
    )

    model = st.selectbox(
        "Model",
        list(D["importance"]),
        key="importance_model"
    )

    f = pd.DataFrame([
        {"Domain":k,"Importance":v}
        for k,v in D["importance"][model].items()
    ]).sort_values("Importance")

    f["Arah"] = f.Importance.map(
        lambda v:"Positif" if v>=0 else "Negatif"
    )

    fig = px.bar(
        f,x="Importance",y="Domain",
        color="Arah",
        orientation="h",
        color_discrete_map={
            "Positif":TEAL,
            "Negatif":"#d49b60"
        },
        text_auto=".3f",
        labels={
            "Importance":"Rata-rata penurunan MCC"
        }
    )

    chart(fig,430)

    st.info(
        "Permutation importance mengukur "
        "kontribusi prediktif, bukan hubungan kausal."
    )

    st.caption(
        "Sumber: T8b importance domain, "
        "Set A, lima fold. Audit overlap "
        "dan leakage semantik masih terbuka."
    )

def dictionary():
    hero(
        "Kamus Indikator",
        "Katalog 34 indikator penelitian "
        "dan status ketersediaan publik."
    )

    domain = st.selectbox(
        "Kelompok indikator",
        ["Semua"]+sorted(CAT.domain.unique()),
        key="dictionary_domain"
    )

    search = st.text_input(
        "Cari nama atau kode",
        key="dictionary_search"
    )

    f = CAT.copy()

    if domain!="Semua":
        f = f[f.domain==domain]

    if search:
        mask = (
            f.name.str.contains(
                search,case=False,regex=False
            ) |
            f.code.str.contains(
                search,case=False,regex=False
            )
        )
        f = f[mask]

    f["Status publik"] = f.published.map({
        True:"Nilai terpilih tersedia",
        False:"Nilai tidak dirilis"
    })

    st.metric("Indikator dalam filter",len(f))

    st.dataframe(
        f[[
            "code","domain","name",
            "unit","Status publik"
        ]].rename(columns={
            "code":"Kode",
            "domain":"Domain",
            "name":"Nama indikator",
            "unit":"Satuan"
        }),
        hide_index=True,
        use_container_width=True
    )

    st.caption(
        "Katalog lengkap tidak berarti seluruh "
        "34 nilai telah direkonsiliasi untuk publikasi."
    )

def methods():
    hero(
        "Metode & Keterbatasan",
        "Dokumentasi sumber, evaluasi model, "
        "privasi, dan interpretasi."
    )

    st.subheader("Sumber dan unit analisis")

    st.markdown("""
- Prediktor: PODES 2025.
- Target: status resmi perkotaan/perdesaan 2025,
  Perka BPS 268/2025.
- Unit analisis: desa/kelurahan.
- Cakupan: Kepulauan Bangka Belitung.
- Model kandidat: Logistic Regression dan Random Forest.
""")

    with st.expander("Metodologi validasi",expanded=True):
        st.write(
            "Nested stratified cross-validation "
            "digunakan pada evaluasi utama. "
            "Validasi lintas kabupaten menahan "
            "satu kelompok wilayah sebagai data uji."
        )

    with st.expander("Kebijakan privasi publik"):
        st.write(
            "Tidak ada mikrodata PODES, identitas desa, "
            "prediksi individual, atau model terlatih. "
            "Komposisi kelas hanya dirilis pada "
            "tingkat provinsi. Indikator komparatif "
            "memerlukan sedikitnya 10 observasi pada "
            "kedua kategori hasil di kedua kelompok."
        )

    with st.expander("Keterbatasan penelitian"):
        st.write(
            "Dashboard tidak mereproduksi skor "
            "klasifikasi resmi BPS. Overlap konseptual "
            "dan potensi leakage masih perlu "
            "ditafsirkan berdasarkan metadata primer. "
            "Hasil model bukan bukti kausal."
        )

    with st.expander("Status verifikasi"):
        st.write(
            "Rekonsiliasi lengkap 34 KPI, katalog "
            "insight, serta lineage semantik belum "
            "ditutup. Rilis ini adalah tampilan "
            "publik agregat terpilih."
        )

    st.caption(
        "Prototipe akademik independen. "
        "Bukan publikasi resmi pemerintah."
    )

pages = [
    st.Page(
        home,title="Ringkasan",
        icon=":material/dashboard:",
        default=True
    ),
    st.Page(
        contrast,title="Perkotaan vs Perdesaan",
        icon=":material/compare_arrows:",
        url_path="perkotaan-perdesaan"
    ),
    st.Page(
        regional,title="Antarwilayah",
        icon=":material/bar_chart:",
        url_path="antarwilayah"
    ),
    st.Page(
        spatial,title="Peta Spasial",
        icon=":material/map:",
        url_path="peta-spasial"
    ),
    st.Page(
        performance,title="Kinerja Model",
        icon=":material/monitoring:",
        url_path="kinerja-model"
    ),
    st.Page(
        factors,title="Faktor Pembeda",
        icon=":material/analytics:",
        url_path="faktor-pembeda"
    ),
    st.Page(
        dictionary,title="Kamus Indikator",
        icon=":material/menu_book:",
        url_path="kamus-indikator"
    ),
    st.Page(
        methods,title="Metode & Keterbatasan",
        icon=":material/info:",
        url_path="metode"
    )
]

with st.sidebar:
    st.markdown("### POTRET WILAYAH")
    st.caption("Bangka Belitung | PODES 2025")
    st.divider()
    st.caption("Public research view")

nav = st.navigation(pages,position="sidebar")
nav.run()

st.divider()

st.caption(
    "Potret Wilayah | Prototipe akademik | "
    "Agregat penelitian terpilih"
)
