
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

st.markdown('\n<style>\n\n:root {\n    --navy: #112b43;\n    --teal: #117c83;\n    --ink: #172f45;\n    --muted: #60778b;\n    --line: #dce5ed;\n    --surface: #ffffff;\n}\n\n.stApp {\n    background: #f1f5f9;\n}\n\n[data-testid="stHeader"] {\n    background: rgba(241,245,249,.96);\n}\n\n.block-container {\n    max-width: 1540px;\n    padding-top: 4.5rem;\n    padding-bottom: 2rem;\n}\n\n[data-testid="stSidebar"],\n[data-testid="stSidebarContent"] {\n    background: #112b43 !important;\n}\n\n[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {\n    gap: .5rem;\n}\n\n[data-testid="stSidebar"] h1,\n[data-testid="stSidebar"] h2,\n[data-testid="stSidebar"] h3,\n[data-testid="stSidebar"] p,\n[data-testid="stSidebar"] span,\n[data-testid="stSidebar"] a {\n    color: #e4edf5 !important;\n}\n\n[data-testid="stSidebar"] a {\n    border-radius: 8px;\n    padding: 8px 10px;\n    text-decoration: none;\n}\n\n[data-testid="stSidebar"] a:hover {\n    background: #24455f;\n}\n\n.st-key-current_nav {\n    background: #117c83;\n    border-radius: 8px;\n}\n\n[data-testid="stSidebar"] hr {\n    border-color: #3a5268;\n    margin: .6rem 0;\n}\n\n[data-testid="stSidebar"] [data-testid="stImage"] img {\n    background: white;\n    padding: 9px;\n    border-radius: 10px;\n    box-sizing: border-box;\n    max-width: 100%;\n    object-fit: contain;\n}\n\n.brand-name {\n    font-size: 24px;\n    font-weight: 800;\n    line-height: 1.1;\n    color: white;\n    letter-spacing: -.7px;\n    margin: 10px 0 6px;\n}\n\n.brand-sub {\n    color: #adc5d7;\n    font-size: 12px;\n    line-height: 1.5;\n}\n\n.nav-label {\n    color: #8cacc4;\n    font-size: 10px;\n    font-weight: 700;\n    letter-spacing: 1.5px;\n    margin: 8px 0 5px;\n}\n\n.hero {\n    position: relative;\n    overflow: hidden;\n    background: linear-gradient(\n        110deg,#112b43,#17445b\n    );\n    border-radius: 16px;\n    padding: 30px;\n    color: white;\n    margin-bottom: 12px;\n    border: 1px solid #294b65;\n}\n\n.hero::after {\n    content: "";\n    position: absolute;\n    width: 240px;\n    height: 240px;\n    right: -70px;\n    top: -120px;\n    border: 28px solid rgba(94,199,194,.09);\n    border-radius: 50%;\n    pointer-events: none;\n}\n\n.hero h1 {\n    color: white !important;\n    font-size: clamp(25px,3vw,40px);\n    font-weight: 780;\n    letter-spacing: -1px;\n    margin: 7px 0 10px;\n    padding: 0;\n    line-height: 1.15;\n}\n\n.hero p {\n    max-width: 850px;\n    color: #d8e6ef !important;\n    line-height: 1.7;\n    font-size: 14px;\n    margin: 0;\n}\n\n.eyebrow {\n    color: #7dd8d1;\n    font-size: 10px;\n    font-weight: 750;\n    letter-spacing: 1.8px;\n}\n\n[data-testid="stMetric"] {\n    background: #ffffff;\n    border: 1px solid #dce5ed;\n    border-top: 3px solid #117c83;\n    border-radius: 12px;\n    padding: 17px;\n    min-height: 108px;\n    box-shadow: 0 3px 12px rgba(17,43,67,.04);\n}\n\n[data-testid="stMetricLabel"] {\n    color: #60778b;\n}\n\n[data-testid="stMetricValue"] {\n    color: #112b43;\n    font-weight: 750;\n}\n\n[data-testid="stVerticalBlockBorderWrapper"] {\n    border-color: #dce5ed;\n}\n\n[data-testid="stPlotlyChart"] {\n    background: white;\n    border-radius: 12px;\n    overflow: hidden;\n    border: 1px solid #dce5ed;\n}\n\n[data-testid="stDataFrame"] {\n    border-radius: 10px;\n    overflow: hidden;\n    border: 1px solid #dce5ed;\n}\n\n[data-baseweb="select"] > div {\n    background: #ffffff;\n    border-color: #d1dce6;\n    border-radius: 8px;\n}\n\n[data-testid="stMain"] h2,\n[data-testid="stMain"] h3 {\n    color: #172f45;\n    letter-spacing: -.35px;\n}\n\n[data-testid="stCaptionContainer"] {\n    line-height: 1.6;\n}\n\n.research-note {\n    background: #e3f1ef;\n    color: #205e60;\n    padding: 15px 18px;\n    border-left: 4px solid #117c83;\n    border-radius: 7px;\n    line-height: 1.6;\n    font-size: 13px;\n}\n\n@media(max-width: 640px) {\n    .block-container {\n        padding-top: 4rem;\n        padding-left: 1rem;\n        padding-right: 1rem;\n    }\n\n    .hero {\n        padding: 20px;\n        border-radius: 12px;\n    }\n\n    .hero h1 {\n        font-size: 26px;\n    }\n\n    [data-testid="stMetric"] {\n        padding: 12px;\n        min-height: 90px;\n    }\n}\n\n</style>\n', unsafe_allow_html=True)

def hero(title,text):

    sections = {
        "Ringkasan Wilayah":"01 / EXECUTIVE OVERVIEW",
        "Perkotaan vs Perdesaan":"02 / COMPARATIVE ANALYTICS",
        "Analisis Antarwilayah":"03 / REGIONAL INTELLIGENCE",
        "Peta Spasial":"04 / GEOSPATIAL INTELLIGENCE",
        "Kinerja Model":"05 / MACHINE LEARNING",
        "Faktor Pembeda":"06 / FEATURE INTELLIGENCE",
        "Kamus Indikator":"07 / DATA DICTIONARY",
        "Metode & Keterbatasan":"08 / RESEARCH METHODS"
    }

    label = sections.get(
        title,"POTRET WILAYAH"
    )

    st.markdown(
        f"""
        <div class="hero">
            <div class="eyebrow">{label}</div>
            <h1>{title}</h1>
            <p>{text}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

def chart(fig,height=430):

    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=20,r=24,t=35,b=28),
        font=dict(
            family="Arial, sans-serif",
            color=NAVY,
            size=12
        ),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        legend_title_text="",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            x=0
        ),
        hoverlabel=dict(
            bgcolor=NAVY,
            font_color="white",
            font_size=12
        )
    )

    if any(
        tr.type in ("bar","scatter","scattergl")
        for tr in fig.data
    ):

        fig.update_xaxes(
            gridcolor="#e7eef4",
            zerolinecolor="#cbd8e3",
            automargin=True
        )

        fig.update_yaxes(
            gridcolor="#e7eef4",
            zerolinecolor="#cbd8e3",
            automargin=True
        )

    fig.update_traces(
        selector=dict(type="bar"),
        marker_line_width=0
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displaylogo":False,
            "responsive":True,
            "toImageButtonOptions":{
                "format":"png",
                "scale":2
            }
        }
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
        "Business Intelligence untuk memahami "
        "karakteristik perkotaan dan perdesaan "
        "Kepulauan Bangka Belitung."
    )

    a,b,c,d = st.columns(4)

    a.metric(
        "Desa / kelurahan",
        P["total"]
    )

    b.metric(
        "Perkotaan",
        P["urban"]
    )

    c.metric(
        "Perdesaan",
        P["rural"]
    )

    d.metric(
        "Kabupaten / kota",
        len(REG)
    )

    left,right = st.columns([1,1.6])

    with left:
        with st.container(border=True):

            st.subheader("Komposisi wilayah")

            fig = go.Figure(go.Pie(
                labels=["Perkotaan","Perdesaan"],
                values=[P["urban"],P["rural"]],
                hole=.72,
                marker_colors=[
                    "#117c83","#9cb9cd"
                ],
                textinfo="percent",
                sort=False
            ))

            fig.add_annotation(
                text=f"<b>{P['total']}</b><br>Desa",
                x=.5,y=.5,
                showarrow=False,
                font=dict(size=22,color=NAVY)
            )

            chart(fig,350)

    with right:
        with st.container(border=True):

            st.subheader(
                "Cakupan desa per kabupaten/kota"
            )

            f = REG.sort_values("total")

            fig = px.bar(
                f,x="total",y="name",
                orientation="h",
                text_auto=True,
                labels={
                    "total":"Jumlah desa",
                    "name":""
                }
            )

            fig.update_traces(
                marker_color="#117c83",
                textposition="outside",
                cliponaxis=False
            )

            fig.update_xaxes(
                range=[0,float(f.total.max())*1.2]
            )

            chart(fig,350)

    st.subheader("Temuan utama penelitian")

    urban_share = P["urban"]/P["total"]*100

    gap = KPI.loc[
        KPI.gap.abs().idxmax()
    ]

    largest = REG.loc[
        REG.total.idxmax()
    ]

    a,b,c = st.columns(3)

    with a:
        with st.container(border=True):

            st.caption("01 / KOMPOSISI")
            st.metric(
                "Proporsi perkotaan",
                f"{urban_share:.1f}%"
            )

            st.write(
                "Kelompok perdesaan lebih besar "
                "daripada kelompok perkotaan "
                "pada cakupan penelitian ini."
            )

    with b:
        with st.container(border=True):

            st.caption("02 / CAKUPAN")
            st.metric(
                largest["name"],
                int(largest["total"])
            )

            st.write(
                "Wilayah dengan jumlah desa "
                "terbanyak dalam data penelitian."
            )

    with c:
        with st.container(border=True):

            st.caption("03 / PERBANDINGAN")
            st.metric(
                "Selisih absolut terbesar",
                f"{abs(gap['gap']):.1f} pp"
            )

            st.write(
                f"{gap['name']}, di antara "
                "12 indikator publik terpilih."
            )

    st.markdown(
        """
        <div class="research-note">
        <b>Catatan interpretasi</b><br>
        Dashboard menampilkan agregat penelitian.
        Perbedaan karakteristik wilayah merupakan
        temuan deskriptif, bukan bukti hubungan kausal.
        </div>
        """,
        unsafe_allow_html=True
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
        "Eksplorasi cakupan administrasi "
        "dan jumlah desa/kelurahan per wilayah."
    )

    a,b,c,d = st.columns(4)

    a.metric("Total desa",P["total"])
    b.metric("Kabupaten/kota",len(REG))
    c.metric("Perkotaan",P["urban"])
    d.metric("Perdesaan",P["rural"])

    features = D["geo"]["features"]

    if not features:
        st.warning("Geometri tidak tersedia.")
        return

    lookup = {
        r["code"]:r for r in D["regions"]
    }

    def points(obj):

        if (
            isinstance(obj,list)
            and len(obj)>=2
            and isinstance(obj[0],(int,float))
            and isinstance(obj[1],(int,float))
        ):
            yield obj[0],obj[1]

        elif isinstance(obj,list):

            for item in obj:
                yield from points(item)

    coords = []

    for feature in features:
        coords.extend(
            points(
                feature["geometry"]["coordinates"]
            )
        )

    min_lon = min(x for x,y in coords)
    max_lon = max(x for x,y in coords)
    min_lat = min(y for x,y in coords)
    max_lat = max(y for x,y in coords)

    center = {
        "lon":(min_lon+max_lon)/2,
        "lat":(min_lat+max_lat)/2
    }

    left,right = st.columns([2.4,1])

    with right:

        with st.container(border=True):

            st.subheader("Profil wilayah")

            selected = st.selectbox(
                "Sorot wilayah",
                ["Semua"]+REG.name.tolist(),
                key="map_region"
            )

            selected_frame = (
                REG if selected=="Semua"
                else REG[REG.name==selected]
            )

            total = int(
                selected_frame.total.sum()
            )

            share = total/P["total"]

            st.metric("Jumlah desa",total)

            st.metric(
                "Proporsi terhadap provinsi",
                f"{share*100:.1f}%"
            )

            st.progress(
                share,
                text="Cakupan desa penelitian"
            )

            st.caption(
                "Peta menggunakan jumlah "
                "desa/kelurahan, bukan proporsi "
                "perkotaan per kabupaten."
            )

        with st.container(border=True):

            st.subheader("Informasi peta")

            st.write("**Sumber geometri:** BIG")
            st.write("**Referensi batas:** 2023")
            st.write("**Data penelitian:** PODES 2025")

            st.caption(
                "Gunakan zoom, geser peta, "
                "atau arahkan pointer ke wilayah "
                "untuk melihat informasi."
            )

    with left:

        st.subheader(
            "Peta tematik Bangka Belitung"
        )

        scale = [
            [0,"#c7e7e0"],
            [.35,"#83c8bd"],
            [.65,"#318f93"],
            [1,"#12536a"]
        ]

        values = REG.total.tolist()

        fig = go.Figure(go.Choroplethmap(
            geojson=D["geo"],
            featureidkey="properties.code",
            locations=REG.code.tolist(),
            z=values,
            customdata=[
                [r["name"],
                 r["total"]/P["total"]*100]
                for r in D["regions"]
            ],
            colorscale=scale,
            zmin=min(values),
            zmax=max(values),
            marker=dict(
                opacity=.94,
                line=dict(
                    color="#ffffff",
                    width=1.4
                )
            ),
            colorbar=dict(
                title="Jumlah desa",
                orientation="h",
                x=.5,
                xanchor="center",
                y=-.10,
                len=.72,
                thickness=13
            ),
            hovertemplate=(
                "<b>%{customdata[0]}</b>"
                "<br>Jumlah desa: %{z}"
                "<br>Cakupan: "
                "%{customdata[1]:.1f}%"
                "<extra></extra>"
            )
        ))

        if selected!="Semua":

            row = REG[
                REG.name==selected
            ].iloc[0]

            fig.add_trace(
                go.Choroplethmap(
                    geojson=D["geo"],
                    featureidkey="properties.code",
                    locations=[row["code"]],
                    z=[int(row["total"])],
                    colorscale=scale,
                    zmin=min(values),
                    zmax=max(values),
                    showscale=False,
                    marker=dict(
                        opacity=1,
                        line=dict(
                            color="#112b43",
                            width=3
                        )
                    ),
                    hovertemplate=(
                        f"<b>{row['name']}</b>"
                        "<br>Jumlah desa: %{z}"
                        "<extra></extra>"
                    )
                )
            )

        fig.update_layout(
            map=dict(
                style="white-bg",
                center=center,
                zoom=5.35
            ),
            height=520,
            margin=dict(
                l=0,r=0,t=5,b=65
            ),
            paper_bgcolor="white",
            hoverlabel=dict(
                bgcolor="#112b43",
                font_color="white"
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displaylogo":False,
                "responsive":True,
                "scrollZoom":False
            }
        )

        st.caption(
            "Warna menunjukkan jumlah desa "
            "dalam cakupan penelitian."
        )

    st.subheader("Cakupan administratif")

    table = REG[["name","total"]].copy()

    table["Cakupan (%)"] = (
        table.total/P["total"]*100
    ).round(1)

    table = table.rename(columns={
        "name":"Kabupaten/kota",
        "total":"Jumlah desa"
    })

    st.dataframe(
        table,
        hide_index=True,
        use_container_width=True
    )

    st.caption(
        "Sumber batas: BIG, RBI 1:50.000, "
        "referensi 2023. Geometri disederhanakan. "
        "Bukan peta legal atau publikasi resmi BPS."
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


nav = st.navigation(
    pages,position="hidden"
)

with st.sidebar:

    logo = (
        Path(__file__).parent
        / "bps-logo.png"
    )

    if logo.is_file():
        st.image(
            str(logo),
            width=220
        )

    st.markdown(
        """
        <div class="brand-name">
            POTRET<br>WILAYAH
        </div>
        <div class="brand-sub">
            Kepulauan Bangka Belitung<br>
            Research &amp; Business Intelligence
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown(
        '<div class="nav-label">'
        'EKSPLORASI DATA'
        '</div>',
        unsafe_allow_html=True
    )

    for index,p in enumerate(pages):

        if index==4:
            st.markdown(
                '<div class="nav-label">'
                'ANALISIS PENELITIAN'
                '</div>',
                unsafe_allow_html=True
            )

        if p.url_path==nav.url_path:

            with st.container(
                key="current_nav"
            ):
                st.page_link(
                    p,
                    label=p.title,
                    icon=p.icon,
                    width="stretch"
                )

        else:

            st.page_link(
                p,
                label=p.title,
                icon=p.icon,
                width="stretch"
            )

    st.divider()

    st.caption(
        "PODES 2025 | Final Edition V2.0"
    )

    st.caption(
        "Prototipe akademik. "
        "Bukan publikasi resmi BPS."
    )

nav.run()


st.divider()

st.caption(
    "Potret Wilayah V2.0 | Prototipe akademik | "
    "Agregat penelitian terpilih"
)
