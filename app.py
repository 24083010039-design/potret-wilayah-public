"""Potret Wilayah: cerita data agregat untuk Kepulauan Bangka Belitung."""

import base64
import html
import json
import textwrap
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


ROOT = Path(__file__).parent
D = json.loads((ROOT / "data.json").read_text(encoding="utf-8"))
BPS_LOGO = base64.b64encode((ROOT / "bps-logo.png").read_bytes()).decode("ascii")
INDICATOR_METADATA = json.loads((ROOT / "indicator_metadata.json").read_text(encoding="utf-8"))
INDICATOR_BY_CODE = {item["code"]: item for item in INDICATOR_METADATA["indicators"]}
INDICATOR_AVAILABILITY = json.loads((ROOT / "indicator_availability.json").read_text(encoding="utf-8"))
AVAILABILITY_BY_CODE = {str(item["code"]): item for item in INDICATOR_AVAILABILITY["indicators"]}
P = D["province"]
REG = pd.DataFrame(D["regions"])
KOTA_CODES = {"1971"}
ADMIN_KOTA_COUNT = int(REG["code"].astype(str).isin(KOTA_CODES).sum())
ADMIN_KABUPATEN_COUNT = int(len(REG) - ADMIN_KOTA_COUNT)
KPI = pd.DataFrame(D["comparisons"])
COMPARISON_BY_CODE = {item["code"]: item for item in D["comparisons"]}
CAT = pd.DataFrame(D["catalog"])
APPROVED_RESULTS = json.loads((ROOT / "release_research_results.json").read_text(encoding="utf-8"))
APPROVED_CONFUSION_MATRICES = APPROVED_RESULTS["confusion_matrices"]
APPROVED_MODEL_COMPARISON = APPROVED_RESULTS["model_comparison"]
APPROVED_FEATURE_AUDIT = APPROVED_RESULTS["feature_audit"]

COLOR = {
    "blue": "#0866B1",
    "sky": "#08749C",
    "green": "#217A50",
    "green_soft": "#EAF6EF",
    "orange": "#A94D0A",
    "orange_light": "#FFF2E6",
    "blue_light": "#EAF4FB",
    "ink": "#172B4D",
    "slate": "#52677D",
    "muted": "#52677D",
    "paper": "#F2F5F9",
    "white": "#FFFFFF",
    "line": "#D9E2EA",
    "grid": "#E6ECF1",
    "negative": "#E78322",
}
URBAN = COLOR["blue"]
RURAL = COLOR["orange"]
MODEL_COLORS = {"Logistic Regression": COLOR["blue"], "Random Forest": COLOR["green"]}

SIDEBAR_ICONS = [
    ":material/dashboard:", ":material/compare_arrows:", ":material/bar_chart:", ":material/map:",
    ":material/monitoring:", ":material/insights:", ":material/menu_book:", ":material/science:",
]


FONT_B64 = base64.b64encode((ROOT / "assets" / "fonts" / "PlusJakartaSans-Variable.ttf").read_bytes()).decode("ascii")
DASHBOARD_CSS = (ROOT / "assets" / "dashboard.css").read_text(encoding="utf-8").replace("__PLUS_JAKARTA_FONT__", FONT_B64)
st.markdown(f"<style>{DASHBOARD_CSS}</style>", unsafe_allow_html=True)

RELEASE_CANDIDATE_ID = "PREMIUM_PRODUCT_FINAL_20261126_4d33b9f1"
st.markdown(f'<span id="potret-release-candidate" data-release-id="{RELEASE_CANDIDATE_ID}" style="display:none"></span>', unsafe_allow_html=True)


def idnum(value, digits=1):
    rendered = f"{float(value):,.{digits}f}"
    return rendered.replace(",", "\0").replace(".", ",").replace("\0", ".")


def pct(value, digits=1):
    return f"{idnum(value, digits)}%"


def page_head(number, chapter, title, question, deck):
    st.markdown(
        f'<div class="page-header"><div class="page-header-copy">'
        f'<div class="page-kicker">Bab {html.escape(number)} &nbsp;·&nbsp; {html.escape(chapter)}</div>'
        f'<h1>{html.escape(title)}</h1>'
        f'<div class="page-question">{html.escape(question)}</div>'
        f'<p class="page-deck">{html.escape(deck)}</p></div>'
        f'<div class="page-context">{idnum(P["total"],0)} desa/kelurahan<br>7 wilayah · 2025</div></div>'
        '<hr class="page-rule">',
        unsafe_allow_html=True,
    )


def section_heading(kicker, title, deck=""):
    deck_html = f'<p class="section-deck">{html.escape(deck)}</p>' if deck else ""
    st.markdown(
        f'<div class="section-kicker">{html.escape(kicker)}</div>'
        f'<div class="section-heading">{html.escape(title)}</div>{deck_html}',
        unsafe_allow_html=True,
    )


def chart(fig, height=420, key=None):
    fig.update_layout(
        template="plotly_white",
        height=height,
        font=dict(family='"Plus Jakarta Sans", "Segoe UI", Arial, sans-serif', size=13, color=COLOR["ink"]),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hoverlabel=dict(bgcolor=COLOR["ink"], font_color="white", font_size=13),
        uniformtext_minsize=10,
        uniformtext_mode="show",
    )
    if not fig.layout.margin.to_plotly_json():
        fig.update_layout(margin=dict(l=16, r=32, t=28, b=44))
    fig.update_xaxes(
        gridcolor=COLOR["grid"],
        zerolinecolor="#8297A8",
        automargin=True,
        tickfont=dict(size=12, color=COLOR["slate"]),
        title_font=dict(size=13, color=COLOR["slate"]),
    )
    fig.update_yaxes(
        gridcolor=COLOR["grid"],
        zerolinecolor="#8297A8",
        automargin=True,
        tickfont=dict(size=12, color=COLOR["slate"]),
        title_font=dict(size=13, color=COLOR["slate"]),
    )
    st.plotly_chart(
        fig,
        width="stretch",
        key=key,
        config={"displaylogo": False, "displayModeBar": False, "responsive": True, "scrollZoom": False},
    )


def chart_panel(fig, height=420, key=None):
    """Give a primary analytical chart a clear, responsive card surface."""
    with st.container(border=True):
        chart(fig, height, key)


def source_note(extra=""):
    text = "Sumber: PODES 2025 dan klasifikasi wilayah resmi 2025. Satuan analisis: desa/kelurahan di Kepulauan Bangka Belitung."
    if extra:
        text += " " + extra
    st.caption(text)


def semantic_table(frame, caption, min_width=760):
    """Render an accessible HTML table with a local horizontal-scroll region."""
    headings = "".join(f"<th scope=\"col\">{html.escape(str(column))}</th>" for column in frame.columns)
    body_rows = []
    for row in frame.itertuples(index=False, name=None):
        cells = []
        for value in row:
            if pd.isna(value):
                value = "—"
            elif isinstance(value, (int, float)):
                value = idnum(value, 0 if float(value).is_integer() else 3)
            cells.append(f"<td>{html.escape(str(value))}</td>")
        body_rows.append("<tr>" + "".join(cells) + "</tr>")
    markup = (
        f'<div class="table-scroll" role="region" aria-label="{html.escape(caption)}; tabel dapat digulir mendatar" tabindex="0">'
        f'<table class="pw-table" style="min-width:{int(min_width)}px"><caption>{html.escape(caption)}</caption>'
        f"<thead><tr>{headings}</tr></thead><tbody>{''.join(body_rows)}</tbody></table></div>"
    )
    st.markdown(markup, unsafe_allow_html=True)


def direction(urban, rural):
    if urban > rural:
        return "perkotaan"
    if rural > urban:
        return "perdesaan"
    return "kedua kelompok"


def footer(next_index):
    if next_index is None:
        st.markdown('<div class="next-question"><b>Pembacaan lebih lanjut:</b> apa yang dapat dan belum dapat disimpulkan dari perbandingan wilayah dan evaluasi model?</div>', unsafe_allow_html=True)
        st.markdown('<div class="page-next"></div>', unsafe_allow_html=True)
        source_note()
        return
    next_page = pages[next_index]
    questions = {
        0: "Pada karakteristik apa kelompok perkotaan dan perdesaan paling berbeda atau berdekatan?",
        1: "Bagaimana jumlah unit tersebar di antara tujuh wilayah?",
        2: "Di mana geometri memperlihatkan sebaran jumlah unit penelitian?",
        3: "Seberapa baik model mengenali pola pada data evaluasi?",
        4: "Bidang informasi mana yang paling banyak mengubah skor model?",
        5: "Apa yang diukur setiap indikator, dan bagaimana membacanya?",
        6: "Bagaimana sumber, unit, dan batas membentuk kesimpulan yang aman?",
    }
    current_index = max(0, min(6, next_index - 1))
    st.markdown(f'<div class="next-question"><b>Pertanyaan berikutnya:</b> {html.escape(questions[current_index])}</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-next"></div>', unsafe_allow_html=True)
    st.page_link(next_page, label=f"Lanjutkan cerita: {next_page.title} →")
    source_note()


def masthead():
    st.markdown(
        f'<div class="masthead"><div class="masthead-brand"><img class="masthead-mark" alt="Badan Pusat Statistik Provinsi Kepulauan Bangka Belitung" src="data:image/png;base64,{BPS_LOGO}">'
        '<div><div class="masthead-name">POTRET WILAYAH</div>'
        '<div class="masthead-meta" style="text-align:left">Kepulauan Bangka Belitung &nbsp;·&nbsp; Data 2025</div></div></div>'
        '<div class="independent-mark">Prototipe akademik independen<br>Bukan situs atau publikasi resmi BPS</div></div>',
        unsafe_allow_html=True,
    )


def kpi_card(label, value, detail, accent, tint, icon, share=None, administrative_composition=None):
    micro = ""
    if share is not None:
        micro = f'<div class="mini-progress" role="img" aria-label="Proporsi {html.escape(label)} {idnum(share)} persen"><i style="width:{share:.1f}%;background:{accent}"></i></div>'
    elif administrative_composition:
        kabupaten, kota = administrative_composition
        micro = (
            f'<div class="kpi-composition" role="img" '
            f'aria-label="Struktur administratif: {kabupaten} kabupaten dan {kota} kota">'
            f'<span><b>{kabupaten}</b> kabupaten</span><span><b>{kota}</b> kota</span></div>'
        )
    return (f'<div class="kpi-card" style="--kpi-accent:{accent};--kpi-tint:{tint}">'
        f'<div class="kpi-top"><span class="kpi-icon" aria-hidden="true">{icon}</span></div>'
        f'<div class="kpi-label">{html.escape(label)}</div><div class="kpi-value">{html.escape(value)}</div>'
        f'<div class="kpi-meta">{html.escape(detail)}</div>{micro}</div>')


def home_region_map(height=370):
    fig = build_big_map(height=height)
    chart(fig, height, key="home_coverage_map")
    st.caption("Angka menunjukkan jumlah desa/kelurahan. Warna menunjukkan cakupan, bukan kemajuan.")


def home():
    rural_share = P["rural"] / P["total"] * 100
    urban_share = P["urban"] / P["total"] * 100
    icons = [
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="4" y="3.5" width="16" height="17" rx="3"/><path d="M8 8h8M8 12h8M8 16h4"/></svg>',
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 20V9l5 3V6l6 4V4h5v16H4Z"/></svg>',
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 20h18M5 20V9l4 3V7l5 4V4l5 3v13"/></svg>',
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 19h16M6 16V9m4 7V5m4 11v-5m4 5V7"/></svg>',
    ]
    st.markdown(
        f'<div class="home-title-row"><div class="home-title-copy"><div class="page-kicker">DASHBOARD RINGKASAN · BANGKA BELITUNG</div>'
        f'<h1 class="home-headline">{pct(rural_share)} desa/kelurahan dalam cakupan berstatus perdesaan.</h1>'
        '<div class="home-deck">Telusuri komposisi 393 desa/kelurahan, perbedaan karakteristik, sebaran wilayah, dan pembacaan model.</div></div>'
        '<div class="home-title-side"><b>Snapshot 2025</b><br>Agregat wilayah · tujuh kabupaten/kota<br>Status perkotaan/perdesaan resmi</div></div>',
        unsafe_allow_html=True)
    st.caption("Sumber cakupan: PODES 2025 dan kode wilayah pada master BPS; status perkotaan/perdesaan mengikuti klasifikasi resmi 2025.")
    with st.container(key="home_kpis"):
        cards = st.columns(4,gap="small")
        items = [
            ("Desa/kelurahan",idnum(P["total"],0),"Dalam cakupan penelitian",COLOR["blue"],COLOR["blue_light"],icons[0],None,None),
            ("Perkotaan",idnum(P["urban"],0),f"{pct(urban_share)} dari semua unit",COLOR["sky"],COLOR["blue_light"],icons[1],urban_share,None),
            ("Perdesaan",idnum(P["rural"],0),f"{pct(rural_share)} dari semua unit",COLOR["orange"],COLOR["orange_light"],icons[2],rural_share,None),
            ("Kabupaten/kota",idnum(len(REG),0),"Wilayah administratif dalam cakupan",COLOR["green"],COLOR["green_soft"],icons[3],None,(ADMIN_KABUPATEN_COUNT,ADMIN_KOTA_COUNT)),
        ]
        for col,item in zip(cards,items):
            with col:
                st.markdown(kpi_card(*item[:6],share=item[6],administrative_composition=item[7]),unsafe_allow_html=True)

    st.markdown('<div class="dashboard-section-label">POTRET PERTAMA · KOMPOSISI & SEBARAN</div>',unsafe_allow_html=True)
    geo, story = st.columns([1.28,.92],gap="medium")
    with geo:
        with st.container(border=True):
            st.markdown('<div class="panel-title">Di mana 393 desa/kelurahan berada?</div><div class="panel-subtitle">Batas kabupaten/kota BIG · angka adalah jumlah desa/kelurahan dalam penelitian</div>',unsafe_allow_html=True)
            home_region_map(370)
            st.page_link(pages[3],label="Buka peta interaktif →",width="stretch")
    with story:
        with st.container(border=True):
            st.markdown('<div class="panel-title">Komposisi status dan temuan utama</div><div class="panel-subtitle">Status resmi 2025 pada desa/kelurahan dalam cakupan</div>',unsafe_allow_html=True)
            fig=go.Figure()
            fig.add_trace(go.Bar(name="Perkotaan",y=["Dari seluruh cakupan"],x=[P["urban"]],orientation="h",marker_color=URBAN,
                text=[f'Perkotaan · {idnum(P["urban"],0)} ({pct(urban_share)})'],textposition="inside",insidetextanchor="middle",
                hovertemplate="Perkotaan: %{x} desa/kelurahan · %{text}<extra></extra>"))
            fig.add_trace(go.Bar(name="Perdesaan",y=["Dari seluruh cakupan"],x=[P["rural"]],orientation="h",marker_color=RURAL,
                text=[f'Perdesaan · {idnum(P["rural"],0)} ({pct(rural_share)})'],textposition="inside",insidetextanchor="middle",
                hovertemplate="Perdesaan: %{x} desa/kelurahan · %{text}<extra></extra>"))
            fig.update_layout(barmode="stack",height=120,showlegend=False,margin=dict(l=4,r=4,t=8,b=24),bargap=.5)
            fig.update_xaxes(range=[0,P["total"]],tickvals=[0,100,200,300,P["total"]],title="Jumlah desa/kelurahan",showgrid=True)
            fig.update_yaxes(showticklabels=False,showgrid=False,zeroline=False)
            chart(fig,120,key="home_status_composition")
            st.caption("61,6% berstatus perdesaan dan 38,4% perkotaan. Persentase menghitung desa/kelurahan, bukan penduduk.")
            top=KPI.iloc[KPI.gap.abs().argmax()]
            near=KPI.iloc[KPI.gap.abs().argmin()]
            pharmacy=KPI.loc[KPI.code=="H03"].iloc[0]
            st.markdown(
                f'<div class="story-stat"><span class="story-number">{idnum(abs(top.gap))}</span><span class="story-unit">poin persentase</span></div>'
                f'<div class="finding-title">Selisih terbesar: {html.escape(str(top["name"]).lower())}</div>'
                f'<div class="finding-copy">{pct(top.rural)} desa/kelurahan perdesaan dan {pct(top.urban)} perkotaan memiliki ciri ini · selisih {idnum(abs(top.gap))} poin persentase.</div>'
                f'<div class="finding-row"><div class="finding-value">{idnum(abs(pharmacy.gap))}</div><div><div class="finding-title">Apotek · selisih terbesar berikutnya</div><div class="finding-copy">{pct(pharmacy.urban)} perkotaan · {pct(pharmacy.rural)} perdesaan</div></div></div>'
                f'<div class="finding-row"><div class="finding-value">{idnum(abs(near.gap))}</div><div><div class="finding-title">Angkutan trayek tetap · nilai paling dekat</div><div class="finding-copy">{pct(near.urban)} perkotaan · {pct(near.rural)} perdesaan · selisih {idnum(abs(near.gap))} poin persentase</div></div></div>'
                '<div class="analysis-note">Ini perbandingan deskriptif pada 12 indikator terpilih. Selisih tidak menunjukkan sebab, kesejahteraan, atau kondisi tiap penduduk.</div>',
                unsafe_allow_html=True)
            st.page_link(pages[1],label="Bandingkan 12 indikator →",width="stretch")

    st.markdown('<div class="dashboard-section-label">INDIKATOR & MODEL</div>',unsafe_allow_html=True)
    indicator,ranks,model=st.columns([1.4,1,1],gap="small")
    with indicator:
        with st.container(border=True):
            st.markdown('<div class="panel-title">Empat jarak indikator terbesar</div><div class="panel-subtitle">Persentase desa/kelurahan per kelompok</div>',unsafe_allow_html=True)
            frame=KPI.assign(abs_gap=KPI.gap.abs()).nlargest(4,"abs_gap").sort_values("abs_gap")
            fig=go.Figure()
            fig.add_trace(go.Bar(name="Perkotaan",y=frame.name,x=frame.urban,orientation="h",marker_color=URBAN,text=[pct(v) for v in frame.urban],textposition="outside",cliponaxis=False,hovertemplate="%{y}<br>Perkotaan %{text}<extra></extra>"))
            fig.add_trace(go.Bar(name="Perdesaan",y=frame.name,x=frame.rural,orientation="h",marker_color=RURAL,text=[pct(v) for v in frame.rural],textposition="outside",cliponaxis=False,hovertemplate="%{y}<br>Perdesaan %{text}<extra></extra>"))
            fig.update_layout(
                barmode="group",height=300,margin=dict(l=8,r=52,t=38,b=18),
                legend=dict(orientation="h",x=0,xanchor="left",y=1.02,yanchor="bottom",font=dict(size=11)),
                bargap=.35,
            )
            fig.update_xaxes(range=[0,112],title=None,ticksuffix="%",dtick=25)
            fig.update_yaxes(title=None,showgrid=False,tickfont=dict(size=11))
            chart(fig,300,key="home_top_indicator_gaps")
            st.page_link(pages[1],label="Telusuri seluruh indikator →",width="stretch")
    with ranks:
        with st.container(border=True):
            st.markdown('<div class="panel-title">Sebaran unit penelitian</div><div class="panel-subtitle">Jumlah menurut kabupaten/kota</div>',unsafe_allow_html=True)
            frame=REG.sort_values("total",ascending=True)
            fig=go.Figure(go.Bar(x=frame.total,y=frame.name,orientation="h",marker_color=COLOR["blue"],
                text=[idnum(v,0) for v in frame.total],textposition="outside",cliponaxis=False,hovertemplate="%{y}<br>%{x} unit<extra></extra>"))
            fig.update_layout(height=280,showlegend=False,margin=dict(l=2,r=28,t=4,b=12),bargap=.34)
            fig.update_xaxes(range=[0,98],showticklabels=False,showgrid=False,zeroline=False)
            fig.update_yaxes(title=None,showgrid=False,tickfont=dict(size=11))
            chart(fig,280,key="home_region_ranking")
            st.page_link(pages[2],label="Analisis antarwilayah →",width="stretch")
    with model:
        with st.container(border=True):
            models=pd.DataFrame(D["models"])
            lr=models.loc[models.model=="Logistic Regression"].iloc[0]
            rf=models.loc[models.model=="Random Forest"].iloc[0]
            st.markdown('<div class="panel-title">Sekilas evaluasi model</div><div class="panel-subtitle">Metrik dari data evaluasi penelitian</div>',unsafe_allow_html=True)
            st.markdown(
                f'<div class="model-metric"><div><span>Accuracy · Logistic Regression</span><b>{pct(float(lr["Accuracy"])*100)}</b></div><i style="width:{float(lr["Accuracy"])*100:.1f}%;background:{COLOR["blue"]}"></i></div>'
                f'<div class="model-metric"><div><span>Accuracy · Random Forest</span><b>{pct(float(rf["Accuracy"])*100)}</b></div><i style="width:{float(rf["Accuracy"])*100:.1f}%;background:{COLOR["green"]}"></i></div>'
                f'<div class="model-metric"><div><span>ROC-AUC · Logistic Regression</span><b>{idnum(float(lr["ROC-AUC"]),3)}</b></div></div>'
                f'<div class="model-metric"><div><span>ROC-AUC · Random Forest</span><b>{idnum(float(rf["ROC-AUC"]),3)}</b></div></div>'
                '<div class="analysis-note">Skor tidak membuktikan pemenang statistik atau jaminan generalisasi.</div>',unsafe_allow_html=True)
            st.page_link(pages[4],label="Baca metrik dan batas model →",width="stretch")

    st.markdown('<div class="dashboard-footnote"><b>Cara membaca:</b> status perkotaan/perdesaan adalah klasifikasi wilayah; jumlah bukan ukuran penduduk, kesejahteraan, atau kemajuan. Geometri peta mengacu pada BIG dan disederhanakan untuk visualisasi.</div>',unsafe_allow_html=True)
    footer(1)


def contrast():
    page_head("2", "Memahami karakteristik", "Perkotaan dan perdesaan", "Pada indikator apa kedua kelompok paling berbeda—dan paling mirip?", "Dua belas indikator dengan nilai pembanding menunjukkan perbedaan pada beberapa bidang dan kedekatan pada bidang lain. Angka adalah persentase desa/kelurahan dalam tiap kelompok.")
    domains = ["Semua bidang"] + sorted(KPI.domain.unique().tolist())
    domain = st.selectbox("Pilih bidang untuk menelusuri indikator", domains, key="contrast_domain")
    frame = KPI.copy() if domain == "Semua bidang" else KPI[KPI.domain == domain].copy()
    frame = frame.assign(abs_gap=frame.gap.abs()).sort_values("abs_gap", ascending=False)
    if frame.empty:
        st.info("Belum ada indikator untuk bidang ini.")
        footer(2)
        return

    top = frame.iloc[0]
    near = frame.iloc[-1]
    direction_text = f"Nilai lebih tinggi tercatat pada kelompok {direction(top.urban, top.rural)}."
    if abs(top.gap) >= 40:
        lead_line = "Jarak besar pada indikator terpilih"
    elif abs(top.gap) <= 10:
        lead_line = "Nilai dua kelompok relatif berdekatan"
    else:
        lead_line = "Perbedaan paling lebar pada pilihan ini"
    feature = KPI.loc[KPI.code == "C07"].iloc[0]
    if domain == "Semua bidang":
        headline = f"Penghasilan utama pertanian lebih dominan pada kelompok perdesaan."
        body = f"Nilainya {pct(feature.rural)} pada perdesaan dan {pct(feature.urban)} pada perkotaan. Jaraknya {idnum(abs(feature.gap))} poin persentase."
    else:
        headline = str(top["name"])
        body = f"{pct(top.urban)} pada perkotaan dan {pct(top.rural)} pada perdesaan; selisihnya {idnum(abs(top.gap))} poin persentase."
    st.markdown(
        f'<div class="section-kicker">{html.escape(lead_line)} &nbsp;·&nbsp; {html.escape(domain)}</div>'
        f'<div class="section-heading">{html.escape(headline)}</div>'
        f'<p class="section-deck">{html.escape(body)} {html.escape(direction_text)}</p>',
        unsafe_allow_html=True,
    )
    metric_left, metric_right = st.columns([1, 1], gap="large")
    with metric_left:
        st.markdown(
            f'<div class="number-callout"><div class="value">{idnum(abs(top.gap))}</div>'
            f'<div class="label">poin persentase · jarak terbesar dalam pilihan</div></div>',
            unsafe_allow_html=True,
        )
    with metric_right:
        st.markdown(
            f'<div class="number-callout" style="border-color:{COLOR["green"]}"><div class="value" style="color:{COLOR["green"]}">{idnum(abs(near.gap))}</div>'
            f'<div class="label">poin persentase · jarak terkecil: {html.escape(str(near["name"]))}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="chart-title">Bandingkan persentase pada skala yang sama</div><div class="chart-deck">Dua batang per indikator menunjukkan bagian desa/kelurahan dalam masing-masing kelompok. Urutan mengikuti selisih terbesar.</div>', unsafe_allow_html=True)
    display = frame.copy()
    display["label"] = display["name"].map(lambda s: textwrap.fill(s, width=30, break_long_words=False))
    labels = display.label.tolist()
    fig = go.Figure()
    for column, name, color in [("urban", "Perkotaan", URBAN), ("rural", "Perdesaan", RURAL)]:
        fig.add_trace(go.Bar(
            x=display[column], y=labels, orientation="h", name=name,
            marker=dict(color=color, line=dict(color="white", width=.6)),
            text=[pct(value) for value in display[column]], textposition="outside",
            textfont=dict(size=12, color=COLOR["ink"]), cliponaxis=False,
            customdata=display["name"],
            hovertemplate="%{customdata}<br>" + name + ": %{text}<extra></extra>",
        ))
    chart_height = max(500, 34 * len(display) + 110)
    fig.update_layout(
        barmode="group", bargap=.34, bargroupgap=.08,
        height=chart_height, margin=dict(l=12, r=52, t=34, b=54),
        legend=dict(orientation="h", y=1.12, x=0, font=dict(size=12)),
    )
    fig.update_xaxes(range=[0, 112], tickvals=[0,20,40,60,80,100], ticktext=["0%","20%","40%","60%","80%","100%"], title="Persentase desa/kelurahan dalam kelompok")
    fig.update_yaxes(title=None, autorange="reversed", showgrid=False, tickfont=dict(size=12))
    chart_panel(fig, chart_height, key="comparison_grouped_bars")
    st.markdown('<div class="analysis-note"><b>Poin persentase</b> adalah jarak antara dua persentase—misalnya 40% dikurangi 30% sama dengan 10 poin persentase. Angka tidak menunjukkan persentase penduduk. Perbedaan bersifat deskriptif dan tidak menjelaskan sebab-akibat.</div>', unsafe_allow_html=True)

    st.markdown('<div class="chart-title">Ringkasan per indikator</div>', unsafe_allow_html=True)
    table = frame[["name", "domain", "urban", "rural", "gap"]].copy()
    table["Arah nilai lebih tinggi"] = [direction(row.urban, row.rural) for row in table.itertuples()]
    table["Jarak"] = table.gap.abs().map(lambda value: f"{idnum(value)} poin persentase")
    table = table.rename(columns={"name": "Indikator", "domain": "Bidang", "urban": "Perkotaan (%)", "rural": "Perdesaan (%)"})
    table["Perkotaan (%)"] = table["Perkotaan (%)"].map(pct)
    table["Perdesaan (%)"] = table["Perdesaan (%)"].map(pct)
    semantic_table(table[["Bidang", "Indikator", "Perkotaan (%)", "Perdesaan (%)", "Jarak", "Arah nilai lebih tinggi"]], "Perbandingan dua belas indikator perkotaan dan perdesaan", min_width=980)
    footer(2)


def regional():
    page_head("3", "Melihat persebaran", "Cakupan antarwilayah", "Bagaimana 393 desa dan kelurahan terbagi di tujuh kabupaten/kota?", "Peringkat berikut menunjukkan banyaknya unit penelitian yang masuk dalam setiap wilayah administratif. Pilih subset untuk melihat bagaimana bagian cakupannya berubah.")
    selected = st.multiselect("Wilayah dalam perbandingan", REG.name.tolist(), default=REG.name.tolist(), key="regional_filter", placeholder="Pilih kabupaten/kota")
    frame = REG[REG.name.isin(selected)].copy()
    if frame.empty:
        st.info("Pilih setidaknya satu kabupaten/kota untuk melihat sebaran cakupan.")
        footer(3)
        return
    total = int(frame.total.sum())
    share = total / P["total"] * 100
    ranked_selected = frame.sort_values("total", ascending=False)
    biggest = ranked_selected.iloc[0]
    smallest = ranked_selected.iloc[-1]
    profile_options = frame.sort_values("total", ascending=False).name.tolist()
    profile_name = st.selectbox("Profil wilayah", profile_options, key="regional_profile")
    profile = frame.loc[frame.name == profile_name].iloc[0]

    left, right = st.columns([1.75, 1], gap="large")
    with left:
        section_heading("Peringkat jumlah unit", f"Cakupan terbanyak pada pilihan: {biggest['name']}.", f"Wilayah ini mencakup {idnum(biggest['total'],0)} desa/kelurahan ({pct(biggest['total']/P['total']*100)} dari seluruh cakupan). {smallest['name']} mencakup {idnum(smallest['total'],0)}; selisih jumlahnya {idnum(biggest['total']-smallest['total'],0)} unit.")
        order = frame.sort_values("total", ascending=True).copy()
        fig = go.Figure(go.Bar(
            x=order.total,
            y=order.name,
            orientation="h",
            marker_color=COLOR["blue"],
            text=[f"{idnum(v,0)}  ·  {pct(v/P['total']*100)}" for v in order.total],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{y}<br>%{x} desa/kelurahan<extra></extra>",
        ))
        fig.update_layout(showlegend=False, margin=dict(l=6, r=68, t=12, b=30), bargap=.42)
        fig.update_xaxes(title="Jumlah desa/kelurahan", range=[0, float(order.total.max()) * 1.5], tickformat="d")
        fig.update_yaxes(title=None, showgrid=False)
        chart_panel(fig, max(350, 48 * len(order) + 80), key="regional_rank")
    with right:
        st.markdown(f'<div class="map-profile"><div class="section-kicker">Profil pilihan</div><div class="map-profile-name">{html.escape(profile_name)}</div><div class="map-profile-value">{idnum(profile.total,0)}</div><div class="metric-ruler">desa/kelurahan &nbsp;·&nbsp; {pct(profile.total/P["total"]*100)} dari seluruh unit penelitian</div></div>', unsafe_allow_html=True)
        st.markdown('<hr class="editorial-rule">', unsafe_allow_html=True)
        section_heading("Cakupan wilayah terpilih", f"{idnum(total,0)} unit · {pct(share)}", "Bagian dari keseluruhan desa dan kelurahan dalam penelitian.")
        st.markdown('<div class="analysis-note">Bagian cakupan mengukur porsi desa/kelurahan penelitian. Angka ini bukan jumlah penduduk, luas, atau tingkat pembangunan kabupaten/kota.</div>', unsafe_allow_html=True)

    table = frame.copy()
    table["Bagian dari seluruh cakupan"] = table.total.map(lambda value: pct(value / P["total"] * 100))
    table = table.sort_values("total", ascending=False).rename(columns={"name": "Kabupaten/kota", "total": "Jumlah desa/kelurahan"})
    st.markdown('<div class="chart-title">Angka menurut pilihan wilayah</div>', unsafe_allow_html=True)
    semantic_table(table[["Kabupaten/kota", "Jumlah desa/kelurahan", "Bagian dari seluruh cakupan"]], "Jumlah desa dan kelurahan menurut kabupaten/kota", min_width=680)
    footer(3)


def _ring_area(ring):
    return sum(p1[0] * p2[1] - p2[0] * p1[1] for p1, p2 in zip(ring, ring[1:])) / 2


def _ring_centroid(ring):
    cross_sum = 0.0
    x_sum = 0.0
    y_sum = 0.0
    for p1, p2 in zip(ring, ring[1:]):
        cross = p1[0] * p2[1] - p2[0] * p1[1]
        cross_sum += cross
        x_sum += (p1[0] + p2[0]) * cross
        y_sum += (p1[1] + p2[1]) * cross
    if abs(cross_sum) < 1e-14:
        return (sum(p[0] for p in ring[:-1]) / max(1, len(ring) - 1), sum(p[1] for p in ring[:-1]) / max(1, len(ring) - 1))
    return x_sum / (3 * cross_sum), y_sum / (3 * cross_sum)


def _inside_ring(point, ring):
    x, y = point
    inside = False
    for (x1, y1), (x2, y2) in zip(ring, ring[1:]):
        if (y1 > y) != (y2 > y):
            crossing_x = (x2 - x1) * (y - y1) / (y2 - y1) + x1
            if x < crossing_x:
                inside = not inside
    return inside


def representative_point(feature):
    geometry = feature["geometry"]
    polygons = geometry["coordinates"] if geometry["type"] == "MultiPolygon" else [geometry["coordinates"]]
    outer = max((polygon[0] for polygon in polygons), key=lambda ring: abs(_ring_area(ring)))
    center = _ring_centroid(outer)
    if _inside_ring(center, outer):
        return center
    lat_values = [point[1] for point in outer]
    min_lat, max_lat = min(lat_values), max(lat_values)
    for frac in (.5, .4, .6, .3, .7):
        y = min_lat + frac * (max_lat - min_lat)
        xs = []
        for p1, p2 in zip(outer, outer[1:]):
            if (p1[1] > y) != (p2[1] > y):
                xs.append((p2[0] - p1[0]) * (y - p1[1]) / (p2[1] - p1[1]) + p1[0])
        xs.sort()
        if len(xs) >= 2:
            left, right = max(zip(xs[::2], xs[1::2]), key=lambda segment: segment[1] - segment[0])
            point = ((left + right) / 2, y)
            if _inside_ring(point, outer):
                return point
    return center



def map_fill(value, low, high):
    stops = ["#EAF4FB", "#B7D8ED", "#58A4D4", COLOR["blue"]]
    fraction = 0 if high == low else max(0,min(1,(float(value)-low)/(high-low)))
    scaled = fraction * (len(stops)-1)
    index = min(len(stops)-2,int(scaled))
    mix = scaled-index
    first = [int(stops[index][i:i+2],16) for i in (1,3,5)]
    second = [int(stops[index+1][i:i+2],16) for i in (1,3,5)]
    channels = [round(x+(y-x)*mix) for x,y in zip(first,second)]
    return "#" + "".join(f"{channel:02X}" for channel in channels)


def build_big_map(selected="Semua", height=440):
    features = {feature["properties"]["code"]: feature for feature in D["geo"]["features"]}
    centers = {code: representative_point(feature) for code,feature in features.items()}
    rows = {row.code: row for row in REG.itertuples()}
    totals = [int(row.total) for row in REG.itertuples()]
    low, high = min(totals), max(totals)
    fig = go.Figure()
    for row in REG.itertuples():
        feature = features.get(row.code)
        if feature is None:
            continue
        geometry = feature["geometry"]
        polygons = geometry["coordinates"] if geometry["type"] == "MultiPolygon" else [geometry["coordinates"]]
        lon, lat = [], []
        for polygon in polygons:
            outer = polygon[0]
            lon.extend(point[0] for point in outer)
            lat.extend(point[1] for point in outer)
            lon.append(outer[0][0]); lat.append(outer[0][1])
            lon.append(None); lat.append(None)
        highlight = selected == row.name
        fig.add_trace(go.Scatter(
            x=lon,y=lat,mode="lines",fill="toself",fillcolor=map_fill(row.total,low,high),
            line=dict(color=COLOR["ink"] if highlight else "#FFFFFF",width=2.8 if highlight else 1.05),
            hoveron="fills",name=row.name,showlegend=False,
            customdata=[[row.name,int(row.total),pct(row.total/P["total"]*100)]]*len(lon),
            hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]} desa/kelurahan · %{customdata[2]} dari cakupan<extra></extra>",
            connectgaps=False,
        ))
    codes = [code for code in REG.code if code in centers]
    x_values = [centers[code][0] for code in codes]
    y_values = [centers[code][1] for code in codes]
    positions = ["top center","middle left","bottom left","middle right","middle right","top right","bottom right"]
    counts = [int(rows[code].total) for code in codes]
    names = [str(rows[code].name) for code in codes]
    labels = [str(count) for count in counts]
    fig.add_trace(go.Scatter(
        x=x_values,y=y_values,text=labels,textposition=positions[:len(codes)],
        mode="markers+text",marker=dict(size=8,color="#FFFFFF",line=dict(color=COLOR["ink"],width=1.2)),
        textfont=dict(family='"Plus Jakarta Sans",Arial,sans-serif',size=12,color=COLOR["ink"]),
        customdata=[[name,idnum(count,0)] for name,count in zip(names,counts)],
        hovertemplate="%{customdata[0]}<br>%{customdata[1]} desa/kelurahan<extra></extra>",
        showlegend=False,cliponaxis=False,
    ))
    all_lon=[point[0] for feature in features.values() for polygon in (feature["geometry"]["coordinates"] if feature["geometry"]["type"]=="MultiPolygon" else [feature["geometry"]["coordinates"]]) for point in polygon[0]]
    all_lat=[point[1] for feature in features.values() for polygon in (feature["geometry"]["coordinates"] if feature["geometry"]["type"]=="MultiPolygon" else [feature["geometry"]["coordinates"]]) for point in polygon[0]]
    x_pad=max((max(all_lon)-min(all_lon))*.055,.08)
    y_pad=max((max(all_lat)-min(all_lat))*.06,.06)
    fig.update_layout(
        height=height,margin=dict(l=12,r=14,t=8,b=8),showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False,range=[min(all_lon)-x_pad,max(all_lon)+x_pad],constrain="domain"),
        yaxis=dict(visible=False,range=[min(all_lat)-y_pad,max(all_lat)+y_pad],scaleanchor="x",scaleratio=1,constrain="domain"),
    )
    return fig


def spatial():
    page_head("4","Membaca pola geografis","Peta cakupan penelitian","Di mana unit penelitian terkonsentrasi?","Geometri BIG menunjukkan jumlah desa/kelurahan dalam cakupan, bukan kemajuan wilayah.")
    if not D["geo"].get("features"):
        st.warning("Geometri wilayah tidak tersedia pada tampilan ini.")
        footer(4)
        return
    if "map_region" not in st.session_state:
        st.session_state.map_region="Semua"
    def reset_map():
        st.session_state.map_region="Semua"
    control,reset=st.columns([3,1])
    with control:
        selected=st.selectbox("Sorot kabupaten/kota",["Semua"]+REG.name.tolist(),key="map_region")
    with reset:
        st.markdown("<div style='height:1.65rem'></div>",unsafe_allow_html=True)
        st.button("Reset sorotan",key="map_reset",on_click=reset_map,help="Kembalikan tampilan ke seluruh wilayah")
    subset=REG if selected=="Semua" else REG[REG.name==selected]
    total=int(subset.total.sum())
    share=total/P["total"]*100
    with st.container(key="spatial_layout"):
        map_col,profile_col=st.columns([2.05,1],gap="small")
        with map_col:
            st.markdown('<div class="chart-title">Jumlah desa/kelurahan menurut batas wilayah</div><div class="chart-deck">Warna pekat berarti jumlah unit lebih banyak. Arahkan kursor atau sentuh wilayah untuk detail.</div>',unsafe_allow_html=True)
            fig=build_big_map(selected=selected,height=470)
            chart_panel(fig,470,key="spatial_map")
            values=sorted(REG.total.astype(int).tolist())
            points=sorted(set([values[0],values[len(values)//3],values[(2*len(values))//3],values[-1]]))
            st.markdown('<div class="map-legend-title">Jumlah desa/kelurahan</div><div class="map-ramp" aria-label="Skala berurutan jumlah unit, dari lebih sedikit ke lebih banyak"></div>'
                f'<div class="map-ramp-values"><span>{idnum(points[0],0)}</span><span>{idnum(points[1],0)}</span><span>{idnum(points[2],0)}</span><span>{idnum(points[3],0)}</span></div>'
                '<div class="map-key">Terang = jumlah lebih sedikit &nbsp;·&nbsp; Pekat = jumlah lebih banyak</div>',unsafe_allow_html=True)
            st.caption("Label angka pada peta adalah jumlah unit. Hover atau sentuh wilayah untuk nama lengkap; tabel di bawah memuat seluruh kabupaten/kota.")
        with profile_col:
            name=selected if selected!="Semua" else "Seluruh provinsi"
            st.markdown(f'<div class="map-profile"><div class="section-kicker">Profil wilayah dipilih</div><div class="map-profile-name">{html.escape(name)}</div><div class="map-profile-value">{idnum(total,0)}</div><div class="metric-ruler">desa/kelurahan &nbsp;·&nbsp; {pct(share)} dari cakupan penelitian</div></div>',unsafe_allow_html=True)
            if selected!="Semua":
                rank=int(REG.total.rank(ascending=False,method="min").loc[REG.name==selected].iloc[0])
                st.markdown(f'<p class="section-deck">Peringkat jumlah: {rank} dari {len(REG)} kabupaten/kota.</p>',unsafe_allow_html=True)
            st.markdown('<div class="analysis-note">Skala warna membandingkan jumlah desa/kelurahan. Warna tidak menyatakan kemajuan, kesejahteraan, atau status perkotaan.</div>',unsafe_allow_html=True)
            st.caption("Geometri administrasi: BIG, RBI 1:50.000, referensi 2023; disederhanakan untuk visualisasi. Bukan peta legal.")
    table=REG.copy()
    table["Bagian cakupan"]=table.total.map(lambda value:pct(value/P["total"]*100))
    table=table.sort_values("total",ascending=False).rename(columns={"name":"Kabupaten/kota","total":"Jumlah desa/kelurahan"})
    st.markdown('<div class="chart-title">Tabel alternatif untuk pembaca peta</div>',unsafe_allow_html=True)
    semantic_table(table[["Kabupaten/kota","Jumlah desa/kelurahan","Bagian cakupan"]],"Daftar wilayah dan bagian cakupan penelitian",min_width=680)
    footer(4)


METRIC_SPECS = {
    "Prediksi yang tepat": {"key":"Accuracy", "range":[0,1], "ticks":[0,.25,.5,.75,1], "meaning":"Bagian semua prediksi yang cocok dengan status sebenarnya.", "caveat":"Angka ini dapat dipengaruhi oleh banyaknya unit pada setiap kelompok; karena itu, baca bersama ukuran lain."},
    "Pengenalan dua kelompok seimbang": {"key":"Balanced accuracy", "range":[0,1], "ticks":[0,.25,.5,.75,1], "meaning":"Rata-rata kemampuan mengenali desa/kelurahan perkotaan dan perdesaan.", "caveat":"Pada dua kelompok, 0,5 menjadi patokan seimbang; nilai lebih tinggi berarti hasil lebih baik dalam evaluasi ini."},
    "Kesesuaian prediksi dengan status": {"key":"MCC", "range":[-1,1], "ticks":[-1,-.5,0,.5,1], "meaning":"Menggabungkan kecocokan antara prediksi dan status sambil memperhitungkan dua kelompok.", "caveat":"Rentangnya −1 sampai 1. Nilai ini bukan persentase prediksi benar."},
    "Pembedaan dua kelompok": {"key":"ROC-AUC", "range":[0,1], "ticks":[0,.25,.5,.75,1], "meaning":"Menilai seberapa baik skor model membedakan urutan contoh dari dua kelompok.", "caveat":"Nilai 0,5 setara patokan acak. Ukuran ini bukan persentase prediksi benar."},
    "Ketepatan dan cakupan deteksi": {"key":"PR-AUC", "range":[0,1], "ticks":[0,.25,.5,.75,1], "meaning":"Merangkum hubungan antara ketepatan prediksi kelompok sasaran dan banyaknya anggotanya yang terdeteksi.", "caveat":"Patokan dipengaruhi proporsi kelompok sasaran. Ukuran ini bukan jumlah prediksi benar."},
}


def performance():
    page_head("5", "Memahami kemampuan model", "Kinerja model", "Apa arti skor model—dan apa yang belum bisa disimpulkan darinya?", "Logistic Regression dan Random Forest diberi karakteristik agregat wilayah untuk mengenali status perkotaan/perdesaan. Skor berikut merangkum evaluasi yang tersedia, bukan jaminan untuk wilayah lain.")
    model_frame = pd.DataFrame(D["models"])
    model_rows = {row.model: row for row in model_frame.itertuples(index=False)}
    card_cols = st.columns(2, gap="medium")
    for col, model_name, accent, soft in [
        (card_cols[0], "Logistic Regression", COLOR["blue"], COLOR["blue_light"]),
        (card_cols[1], "Random Forest", COLOR["green"], COLOR["green_soft"]),
    ]:
        with col:
            row = model_rows[model_name]
            accuracy = float(getattr(row, "Accuracy"))
            st.markdown(
                f'<div class="model-hero" style="--model-accent:{accent};--model-tint:{soft}">'
                f'<div class="model-hero-top"><span class="model-hero-name">{html.escape(model_name)}</span><span class="model-hero-tag">HASIL EVALUASI</span></div>'
                f'<div class="model-hero-value">{pct(accuracy*100)}</div>'
                f'<div class="model-hero-caption">sekitar {round(accuracy*100)} prediksi tepat dari setiap 100 pada evaluasi ini</div>'
                f'<div class="model-hero-track"><i style="width:{accuracy*100:.1f}%"></i></div>'
                '</div>', unsafe_allow_html=True,
            )
    choice = st.selectbox("Pilih ukuran yang ingin dibaca", list(METRIC_SPECS), key="model_metric_simple")
    spec = METRIC_SPECS[choice]
    metric = spec["key"]
    left_value = float(model_frame.loc[model_frame.model == "Logistic Regression", metric].iloc[0])
    right_value = float(model_frame.loc[model_frame.model == "Random Forest", metric].iloc[0])
    percentage_metrics = {"Accuracy", "Balanced accuracy"}
    metric_text = lambda value: pct(float(value) * 100, 1) if metric in percentage_metrics else idnum(value, 3)
    lead = f"{choice}: {metric_text(left_value)} untuk Logistic Regression dan {metric_text(right_value)} untuk Random Forest."
    context = f"{spec['meaning']} {spec['caveat']}"
    st.markdown(f'<div class="section-kicker">Perbandingan model · ukuran yang dipilih: {html.escape(choice)}</div><div class="section-heading">{html.escape(lead)}</div><p class="section-deck">{html.escape(context)}</p>', unsafe_allow_html=True)
    fig = go.Figure()
    low, high = spec["range"]
    mcc_sd = [
        float(model_frame.loc[model_frame.model == "Logistic Regression", "MCC_SD"].iloc[0]),
        float(model_frame.loc[model_frame.model == "Random Forest", "MCC_SD"].iloc[0]),
    ] if metric == "MCC" and "MCC_SD" in model_frame else None
    fig.add_trace(go.Bar(
        x=[left_value, right_value], y=["Logistic Regression", "Random Forest"], orientation="h",
        marker=dict(color=[MODEL_COLORS["Logistic Regression"], MODEL_COLORS["Random Forest"]], line=dict(color="white", width=1)),
        text=[metric_text(left_value), metric_text(right_value)], textposition="outside", cliponaxis=False,
        error_x=dict(type="data", array=mcc_sd, visible=True, thickness=1.5, width=4) if mcc_sd else None,
        customdata=["Logistic Regression", "Random Forest"],
        hovertemplate="%{customdata}<br>" + metric + ": %{text}<extra></extra>",
    ))
    fig.update_layout(showlegend=False, margin=dict(l=16,r=48,t=12,b=48), height=210, bargap=.5)
    axis_pad = 0 if metric == "MCC" else (high-low)*.08
    axis_ticks = [pct(value * 100, 0) for value in spec["ticks"]] if metric in percentage_metrics else [idnum(value,0 if float(value).is_integer() else 2) for value in spec["ticks"]]
    axis_title = "Persentase (%)" if metric in percentage_metrics else ("Rentang −1 hingga 1" if metric == "MCC" else "Skor · rentang 0 hingga 1")
    fig.update_xaxes(range=[low-axis_pad, high+axis_pad], tickvals=spec["ticks"], ticktext=axis_ticks, title=axis_title)
    fig.update_yaxes(title=None, showgrid=False, autorange="reversed")
    if metric == "MCC":
        fig.add_vline(x=0, line_width=1.5, line_dash="dot", line_color=COLOR["slate"])
    chart_panel(fig, 210, key="model_metric_comparison")
    st.markdown(f'<div class="metric-definition"><b>{html.escape(choice)} ({html.escape(metric)}):</b> {html.escape(spec["meaning"])} {html.escape(spec["caveat"])}</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">Seluruh ukuran yang tersedia</div>', unsafe_allow_html=True)
    all_table = pd.DataFrame({
        "Model": model_frame["model"],
        "Accuracy (%)": model_frame["Accuracy"].map(lambda value: pct(value * 100, 1)),
        "Balanced accuracy (%)": model_frame["Balanced accuracy"].map(lambda value: pct(value * 100, 1)),
        "MCC mean": model_frame["MCC"].map(lambda value: idnum(value, 3)),
        "MCC SD · fold": model_frame["MCC_SD"].map(lambda value: idnum(value, 3)),
        "ROC-AUC · skor": model_frame["ROC-AUC"].map(lambda value: idnum(value, 3)),
        "PR-AUC · skor": model_frame["PR-AUC"].map(lambda value: idnum(value, 3)),
    })
    semantic_table(all_table, "Perbandingan ukuran evaluasi · rerata fold dan simpangan baku MCC", min_width=1120)
    if APPROVED_MODEL_COMPARISON:
        p_value = float(APPROVED_MODEL_COMPARISON["p_corrected"])
        lr_mcc = model_frame.loc[model_frame.model == "Logistic Regression"].iloc[0]
        rf_mcc = model_frame.loc[model_frame.model == "Random Forest"].iloc[0]
        interpretation = "Random Forest memiliki rerata MCC teramati lebih tinggi, tetapi uji berpasangan terkoreksi tidak menunjukkan keunggulan statistik pada taraf 5%. Tidak ada model final yang dipilih."
        method_note = f"Nested stratified 5×5: MCC Logistic Regression {idnum(lr_mcc['MCC'],3)} ± {idnum(lr_mcc['MCC_SD'],3)} dan Random Forest {idnum(rf_mcc['MCC'],3)} ± {idnum(rf_mcc['MCC_SD'],3)} (rerata ± SD dari {APPROVED_MODEL_COMPARISON['n_folds']} outer fold). Uji Nadeau–Bengio corrected resampled t dua sisi pada fold berpasangan memberi p = {idnum(p_value, 3)}. SD adalah variasi antar-fold, bukan interval kepercayaan."
    else:
        interpretation = "Nilai menunjukkan perbedaan rerata teramati; tidak ada klaim model unggul secara statistik atau model final terpilih."
        method_note = "Rincian uji berpasangan tidak dimuat dalam paket ini. MCC SD adalah simpangan baku fold, bukan interval kepercayaan."
    st.markdown(f'<div class="analysis-note"><b>Ketidakpastian dan pemilihan model.</b> {html.escape(interpretation)} {html.escape(method_note)}</div>', unsafe_allow_html=True)

    st.markdown('<hr class="editorial-rule">', unsafe_allow_html=True)
    section_heading("Kesalahan klasifikasi", "Matriks kebingungan · konfigurasi A", "Baris menunjukkan status aktual; kolom menunjukkan prediksi. Perdesaan adalah kelas 0 dan perkotaan kelas positif 1.")
    if APPROVED_CONFUSION_MATRICES:
        matrix_columns = st.columns(2, gap="medium")
        matrix_rows = []
        class_rows = []
        for column, model_name in zip(matrix_columns, ["Logistic Regression", "Random Forest"]):
            matrix = APPROVED_CONFUSION_MATRICES.get(model_name)
            if matrix is None:
                continue
            tn, fp = matrix[0]
            fn, tp = matrix[1]
            with column:
                st.markdown(f'<div class="chart-title">{html.escape(model_name)}</div>', unsafe_allow_html=True)
                matrix_figure = go.Figure(go.Heatmap(
                    z=matrix,
                    x=["Prediksi: perdesaan", "Prediksi: perkotaan"],
                    y=["Aktual: perdesaan", "Aktual: perkotaan"],
                    text=[[f"TN · {idnum(tn,0)}", f"FP · {idnum(fp,0)}"], [f"FN · {idnum(fn,0)}", f"TP · {idnum(tp,0)}"]],
                    texttemplate="%{text}",
                    textfont=dict(color=COLOR["ink"], size=14),
                    colorscale=[[0, "#F7FAFC"], [1, "#AED0E2"]],
                    showscale=False,
                    hovertemplate="%{y}<br>%{x}<br>Prediksi berulang: %{z}<extra></extra>",
                ))
                matrix_figure.update_layout(height=290, margin=dict(l=14,r=12,t=58,b=58), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                matrix_figure.update_xaxes(side="top", title=None, tickfont=dict(size=11))
                matrix_figure.update_yaxes(title=None, autorange="reversed", tickfont=dict(size=11))
                chart_panel(matrix_figure, 290, key=f"confusion_matrix_{model_name.lower().replace(' ', '_')}")
            rural_precision = tn / (tn + fn) if tn + fn else float("nan")
            rural_recall = tn / (tn + fp) if tn + fp else float("nan")
            urban_precision = tp / (tp + fp) if tp + fp else float("nan")
            urban_recall = tp / (tp + fn) if tp + fn else float("nan")
            for class_name, precision, recall in [
                ("Perdesaan", rural_precision, rural_recall),
                ("Perkotaan", urban_precision, urban_recall),
            ]:
                class_rows.append({
                    "Model": model_name,
                    "Kelas": class_name,
                    "Presisi · pooled": pct(precision * 100, 1),
                    "Recall · pooled": pct(recall * 100, 1),
                })
            matrix_rows.extend([
                {"Model": model_name, "Status aktual": "Perdesaan", "Prediksi perdesaan": idnum(tn,0), "Prediksi perkotaan": idnum(fp,0)},
                {"Model": model_name, "Status aktual": "Perkotaan", "Prediksi perdesaan": idnum(fn,0), "Prediksi perkotaan": idnum(tp,0)},
            ])
        if class_rows:
            semantic_table(pd.DataFrame(class_rows), "Presisi dan recall per kelas dari hitungan gabungan fold", min_width=760)
            semantic_table(pd.DataFrame(matrix_rows), "Data matriks kebingungan agregat per model", min_width=760)
        st.markdown('<div class="analysis-note"><b>Cara membaca:</b> FN adalah desa perkotaan yang keliru dikenali sebagai perdesaan; FP adalah desa perdesaan yang keliru dikenali sebagai perkotaan. Matriks berisi 1.965 prediksi fold per model dari 25 outer fold; setiap satu dari 393 desa/kelurahan muncul lima kali. Presisi dan recall di atas dihitung dari hitungan gabungan (pooled), bukan rerata metrik per fold.</div>', unsafe_allow_html=True)
    else:
        st.info("Matriks klasifikasi tidak dimuat dalam rilis ini; tidak ada nilai yang direkonstruksi dari angka ringkasan.")

    st.markdown('<hr class="editorial-rule">', unsafe_allow_html=True)
    section_heading("Uji lintas kabupaten/kota", "Skor konfigurasi berbeda di antara tiga pilihan fitur.", "Enam ringkasan model memakai skema leave-one-kabupaten-out. Tiap putaran menyisihkan satu kabupaten/kota; skor ini tidak membuktikan keunggulan statistik atau menjamin generalisasi.")
    cross_metric = st.selectbox("Pilih ukuran untuk membandingkan konfigurasi", ["MCC", "Accuracy", "ROC-AUC", "PR-AUC"], key="cross_model_metric")
    cross_axis = [-1, 1] if cross_metric == "MCC" else [0, 1]
    cross_rows = []
    for item in D["cross"]:
        parts = item["run"].split("_")
        model_name = "Random Forest" if parts[-1] == "forest" else "Logistic Regression"
        cross_rows.append({"Model": model_name, "Konfigurasi": parts[1] if len(parts)>1 else "—", **item})
    cross_frame = pd.DataFrame(cross_rows)
    cross_fig = go.Figure()
    for model_name in ["Logistic Regression", "Random Forest"]:
        subset = cross_frame[cross_frame.Model == model_name].set_index("Konfigurasi").reindex(["A", "C", "D"])
        raw = [None if pd.isna(value) else float(value) for value in subset[cross_metric].tolist()]
        label_values = ["—" if value is None else (pct(value * 100, 1) if cross_metric == "Accuracy" else idnum(value,3)) for value in raw]
        cross_fig.add_trace(go.Bar(
            x=raw, y=["A", "C", "D"], orientation="h", name=model_name,
            marker=dict(color=MODEL_COLORS[model_name]), text=label_values, textposition="outside", cliponaxis=False,
            customdata=[model_name]*3,
            hovertemplate="Konfigurasi %{y} · %{customdata}<br>" + cross_metric + ": %{text}<extra></extra>",
        ))
    cross_fig.update_layout(barmode="group", bargap=.32, bargroupgap=.1, height=310, margin=dict(l=18,r=48,t=30,b=48), legend=dict(orientation="h",y=1.14,x=0,font=dict(size=12)))
    cross_ticks = METRIC_SPECS["Kesesuaian prediksi dengan status"]["ticks"] if cross_metric=="MCC" else [0,.25,.5,.75,1]
    cross_ticktext = [pct(value * 100, 0) for value in cross_ticks] if cross_metric == "Accuracy" else [idnum(value,0 if float(value).is_integer() else 2) for value in cross_ticks]
    cross_axis_title = "Accuracy (%)" if cross_metric == "Accuracy" else ("MCC · rentang −1 hingga 1" if cross_metric=="MCC" else cross_metric + " · skor 0 hingga 1")
    cross_fig.update_xaxes(range=cross_axis, title=cross_axis_title, tickvals=cross_ticks, ticktext=cross_ticktext)
    cross_fig.update_yaxes(title="Konfigurasi fitur", showgrid=False, autorange="reversed")
    if cross_metric == "MCC":
        cross_fig.add_vline(x=0, line_width=1.2, line_dash="dot", line_color=COLOR["slate"])
    chart_panel(cross_fig, 310, key="cross_region_grouped_bars")
    cross_rows = []
    for item in D["cross"]:
        parts = item["run"].split("_")
        model_name = "Random Forest" if parts[-1] == "forest" else "Logistic Regression"
        metric_value = lambda key: "—" if item.get(key) is None or pd.isna(item.get(key)) else (pct(float(item[key]) * 100, 1) if key == "Accuracy" else idnum(item[key],3))
        cross_rows.append({
            "Model": model_name,
            "Konfigurasi": parts[1] if len(parts)>1 else "—",
            "Informasi masukan": idnum(item["features"],0),
            "Fold MCC tersedia": f"{idnum(item['valid_mcc_folds'],0)} dari {idnum(item['folds'],0)}",
            "MCC": metric_value("MCC"),
            "Accuracy (%)": metric_value("Accuracy"),
            "ROC-AUC": metric_value("ROC-AUC"),
            "PR-AUC": metric_value("PR-AUC"),
        })
    semantic_table(pd.DataFrame(cross_rows), "Evaluasi model lintas kabupaten/kota", min_width=1000)
    folds = int(D["cross"][0]["folds"]) if D["cross"] else 0
    valid_mcc = int(D["cross"][0]["valid_mcc_folds"]) if D["cross"] else 0
    st.markdown(f'<div class="analysis-note">Setiap model diringkas dari {folds} kabupaten/kota; MCC tersedia pada {valid_mcc} fold. Satu fold tanpa MCC tidak dihitung sebagai nol. Selisih skor belum membuktikan model pemenang secara statistik atau memastikan generalisasi ke provinsi/periode lain.</div>', unsafe_allow_html=True)
    with st.expander("Apa arti konfigurasi A, C, dan D?"):
        st.markdown("- **A · 51 variabel**: paket utama penelitian.\n- **C · 37 variabel**: paket sementara tanpa fasilitas kriteria resmi dan proksinya.\n- **D · 36 variabel**: paket eksploratif, yaitu C tanpa variabel R906A.\n\nRincian jumlah dan label set ini tercatat dalam laporan evaluasi model penelitian. Perbandingan konfigurasi tetap bersifat eksploratif.")
    with st.expander("Istilah teknis"):
        st.markdown("- **Logistic Regression** memperkirakan peluang status dari bobot karakteristik masukan.\n- **Random Forest** menggabungkan keluaran dari sejumlah pohon keputusan.\n- **Fold** adalah satu putaran bagian data yang digunakan untuk evaluasi.\n- **Accuracy** adalah satu-satunya ukuran pada ringkasan ini yang dibaca sebagai bagian prediksi tepat. MCC, ROC-AUC, dan PR-AUC bukan jumlah prediksi benar.")
    footer(5)


def factors():
    page_head("6", "Membaca informasi model", "Informasi yang membantu model", "Apa yang terjadi ketika informasi suatu bidang diacak?", "Bayangkan kartu dari satu bidang dikocok; lalu amati perubahan skor model pada data uji. Ukuran ini menunjukkan kegunaan prediktif, bukan sebab-akibat.")
    importance = D["importance"]
    values = []
    for model in ["Logistic Regression", "Random Forest"]:
        for domain, value in importance[model].items():
            values.append({"Model":model, "Bidang":domain, "Nilai":float(value)})
    frame = pd.DataFrame(values)
    best_rf = frame[(frame.Model == "Random Forest")].sort_values("Nilai", ascending=False).iloc[0]
    lr_econ = float(importance["Logistic Regression"].get("Ekonomi", 0))
    rf_econ = float(importance["Random Forest"].get("Ekonomi", 0))
    st.markdown(
        f'<div class="section-kicker">Temuan teratas pada kedua ringkasan</div>'
        f'<div class="section-heading">Informasi ekonomi paling banyak mengubah skor saat diacak.</div>'
        f'<p class="section-deck">Pada Ekonomi, perubahan MCC adalah {idnum(lr_econ,4)} untuk Logistic Regression dan {idnum(rf_econ,4)} untuk Random Forest.</p>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="chart-title">Perubahan MCC setelah satu bidang diacak</div><div class="chart-deck">Batang ke kanan menunjukkan skor turun setelah pengacakan; batang ke kiri menunjukkan skor naik. Warna selalu menandai model yang sama.</div>', unsafe_allow_html=True)
    domain_order = ["Ekonomi", "Infrastruktur", "Pendidikan", "Transportasi", "Digital", "Kesehatan", "Geografi"]
    fig = go.Figure()
    fig.add_vline(x=0, line_width=1.8, line_color=COLOR["ink"])
    for model in ["Logistic Regression", "Random Forest"]:
        subset = frame[frame.Model == model].set_index("Bidang")
        values_for_model = [float(subset.loc[domain, "Nilai"]) for domain in domain_order]
        fig.add_trace(go.Bar(
            x=values_for_model, y=domain_order, orientation="h", name=model,
            marker=dict(color=MODEL_COLORS[model], line=dict(color="white", width=.8)),
            text=[idnum(value,4) for value in values_for_model], textposition="outside", cliponaxis=False,
            customdata=[model]*len(domain_order),
            hovertemplate="%{y} · %{customdata}<br>Perubahan MCC: %{text}<extra></extra>",
        ))
    fig.update_layout(barmode="group", bargap=.28, bargroupgap=.08, height=500, margin=dict(l=18,r=66,t=28,b=58), legend=dict(orientation="h",y=1.16,x=0,font=dict(size=12)))
    tickvals = [-.05, 0, .05, .10, .15, .20]
    fig.update_xaxes(title="Perubahan MCC setelah informasi diacak", range=[-.065,.245], tickvals=tickvals, ticktext=[idnum(value,2) for value in tickvals])
    fig.update_yaxes(title=None, categoryorder="array", categoryarray=list(reversed(domain_order)), showgrid=False, tickfont=dict(size=13))
    chart_panel(fig,500,key="importance_diverging_bars")
    st.markdown('<div class="analysis-note"><b>Cara membaca:</b> jika MCC turun setelah suatu bidang diacak, informasi bidang tersebut membantu prediksi pada evaluasi ini. Nilai negatif berarti MCC naik pada pengacakan ini; hal itu tidak membuktikan bidang tersebut merugikan atau tidak berguna. Tumpang tindih informasi dan kemungkinan kebocoran masih menjadi batas penelitian. Ukuran ini menunjukkan kegunaan prediktif, bukan sebab-akibat.</div>', unsafe_allow_html=True)
    with st.expander("Istilah akademik"):
        st.write("Permutation importance mengacak informasi pada satu bidang lalu menghitung perubahan Matthews correlation coefficient (MCC). Angka yang disajikan merupakan ringkasan evaluasi penelitian.")
    footer(6)


def indicator_status(code):
    state = AVAILABILITY_BY_CODE.get(str(code), {}).get("state", "availability_unverified")
    labels = {
        "included_in_candidate": ("Nilai ditampilkan", "available"),
        "internal_aggregate_verified": ("Agregat terverifikasi secara internal", "internal"),
        "constant_uninformative": ("Indikator konstan", "constant"),
        "availability_unverified": ("Menunggu verifikasi", "unknown"),
    }
    return state, labels.get(state, ("Menunggu verifikasi", "unknown"))


def render_indicator_card(row):
    code = str(row["code"])
    item = INDICATOR_BY_CODE.get(code, {})
    availability = AVAILABILITY_BY_CODE.get(code, {})
    state, (status_label, status_class) = indicator_status(code)
    name = str(item.get("formal_name") or row["name"])
    domain = str(row["domain"])
    unit = str(item.get("measurement_unit") or row["unit"])
    summary = str(item.get("plain_language") or "Penjelasan ringkas belum tersedia pada kamus yang digunakan.")
    comparison = COMPARISON_BY_CODE.get(code)
    source_details = item.get("source_variable_details", [])
    inclusion_note = '<div class="dictionary-inclusion-note">Tidak termasuk dalam paket tampilan</div>' if state == "internal_aggregate_verified" else ""

    with st.container(border=True):
        st.markdown(
            f'<div class="indicator-card-meta"><span class="indicator-code">{html.escape(code)}</span>'
            f'<span class="indicator-status {status_class}">{html.escape(status_label)}</span></div>'
            f'{inclusion_note}'
            f'<div class="indicator-card-domain">{html.escape(domain)} <span>·</span> {html.escape(unit)}</div>'
            f'<div class="indicator-card-name">{html.escape(name)}</div>'
            f'<p class="indicator-card-summary">{html.escape(summary)}</p>',
            unsafe_allow_html=True,
        )
        with st.expander("Definisi dan cara membaca"):
            st.markdown("**Definisi operasional**")
            st.write(item.get("operational_definition") or "Definisi operasional belum tersedia pada kamus penelitian.")
            st.markdown("**Rumus yang mudah dibaca**")
            readable_formula = item.get("formula_readable") or "Rumus tidak tersedia pada metadata yang dapat digunakan."
            st.markdown(f'<div class="dictionary-formula">{html.escape(str(readable_formula))}</div>', unsafe_allow_html=True)
            numerator_col, denominator_col = st.columns(2, gap="small")
            with numerator_col:
                st.markdown("**Pembilang / ukuran**")
                st.write(item.get("numerator") or "Tidak ditentukan untuk ukuran ini.")
            with denominator_col:
                st.markdown("**Penyebut**")
                st.write(item.get("denominator") or "Tidak ditentukan untuk ukuran ini.")

            st.markdown("**Variabel sumber**")
            if source_details:
                source_html = "".join(
                    '<li><code>' + html.escape(str(source.get("code", ""))) + '</code> · '
                    + html.escape(str(source.get("label") or "Label variabel tidak tersedia")) + '</li>'
                    for source in source_details
                )
                st.markdown(f'<ul class="dictionary-source-list">{source_html}</ul>', unsafe_allow_html=True)
            else:
                st.write(item.get("source_variables") or "Variabel sumber tidak dicantumkan pada kamus.")

            st.markdown("**Cara membaca**")
            guidance = item.get("interpretation_guidance") or item.get("interpretation")
            if guidance:
                if unit == "%":
                    guidance += " Nilai yang lebih tinggi berarti lebih banyak unit pada penyebut memenuhi ciri tersebut."
                elif code in {"E06", "E08"}:
                    guidance += " Nilai lebih tinggi berarti jarak rata-rata ke sekolah lebih jauh pada subkelompok yang disyaratkan."
                elif item.get("measure_type") == "mean_per_village":
                    guidance += " Rerata tidak menunjukkan sebaran atau kesamaan antar desa."
                else:
                    guidance += " Angka adalah jumlah dalam cakupan penelitian, bukan jumlah per penduduk."
                st.write(guidance)
            else:
                st.write("Panduan pembacaan khusus belum tersedia pada kamus penelitian.")

            st.markdown("**Batas interpretasi**")
            st.write(item.get("what_cannot_be_concluded") or item.get("limitation") or "Jangan menarik kesimpulan di luar definisi, penyebut, dan cakupan wilayah indikator.")

            if comparison:
                st.markdown("#### Nilai pembanding")
                st.caption("Persentase menghitung desa/kelurahan dalam tiap kelompok, bukan penduduk.")
                urban_col, rural_col, province_col = st.columns(3, gap="small")
                with urban_col:
                    st.metric("Perkotaan", pct(comparison["urban"], 1))
                with rural_col:
                    st.metric("Perdesaan", pct(comparison["rural"], 1))
                with province_col:
                    st.metric("Cakupan", pct(comparison["province"], 1))
                urban_width = min(100.0, max(0.0, float(comparison["urban"])))
                rural_width = min(100.0, max(0.0, float(comparison["rural"])))
                st.markdown(
                    f'<div class="dictionary-comparison-chart" role="img" aria-label="Perbandingan persentase desa: perkotaan {pct(comparison["urban"],1)}, perdesaan {pct(comparison["rural"],1)}; skala nol sampai seratus persen">'
                    f'<div class="dictionary-bar-row"><span>Perkotaan</span><div class="dictionary-bar-track"><i class="dictionary-bar-fill urban" style="width:{urban_width:.1f}%"></i></div><b>{pct(comparison["urban"],1)}</b></div>'
                    f'<div class="dictionary-bar-row"><span>Perdesaan</span><div class="dictionary-bar-track"><i class="dictionary-bar-fill rural" style="width:{rural_width:.1f}%"></i></div><b>{pct(comparison["rural"],1)}</b></div>'
                    '<div class="dictionary-bar-scale"><span>0%</span><span>50%</span><span>100%</span></div></div>',
                    unsafe_allow_html=True,
                )
                gap = float(comparison["gap"])
                if gap == 0:
                    gap_text = "Nilai kedua kelompok sama setelah pembulatan yang digunakan."
                else:
                    higher = "perkotaan" if gap > 0 else "perdesaan"
                    gap_text = f"Selisih {idnum(abs(gap), 1)} poin persentase; nilai lebih tinggi pada kelompok {higher}. Perbedaan tidak menunjukkan penyebab."
                st.markdown(f'<p class="dictionary-gap-note">{html.escape(gap_text)}</p>', unsafe_allow_html=True)
            elif state == "constant_uninformative":
                st.info("Variabel sumber tidak bervariasi dalam cakupan penelitian, sehingga tidak dapat membedakan kelompok.")
            elif state == "internal_aggregate_verified":
                st.info("Agregat terverifikasi secara internal, tetapi nilai numeriknya tidak disertakan dalam rilis publik. Alasan pemilihan indikator untuk paket tampilan belum terdokumentasi.")
                if code == "G03":
                    st.caption("G03 · Jumlah RT tercatat sebagai agregat internal; indikator ini tidak dimasukkan ke 12 pembanding dan nilainya tidak disertakan dalam paket publik.")
                st.caption("Nilai agregat internal tidak dimuat dalam paket publik.")
            else:
                st.info("Nilai pembanding belum dapat dipastikan. Angka tidak diganti dengan nol.")

        with st.expander("Sumber dan rincian teknis"):
            st.markdown("**Satuan**")
            st.write(item.get("measurement_unit") or item.get("unit_in_source") or unit)
            st.markdown("**Rumus teknis**")
            st.code(item.get("calculation_technical") or item.get("calculation") or "Tidak tersedia", language=None)
            st.markdown("**Catatan definisi**")
            st.write(item.get("metadata_status") or "Metadata provenance belum tercatat.")
            provenance = item.get("metadata_provenance", {})
            official_status = provenance.get("official_definition_status") or "Status verifikasi sumber resmi tidak tercatat."
            st.write(f"**Status definisi resmi:** {official_status}")
            formula_check = item.get("formula_crosschecked_with_kpi_catalog")
            formula_status = "Rumus dicocokkan dengan katalog KPI lokal." if formula_check is True else "Kecocokan rumus dengan katalog KPI lokal belum diverifikasi."
            st.write(f"**Status rumus:** {formula_status}")
            state_label = indicator_status(code)[1][0]
            st.write(f"**Ketersediaan riset:** {state_label}")
            inclusion = "Termasuk dalam paket tampilan." if availability.get("public_candidate_included") else "Tidak termasuk dalam paket tampilan."
            st.write(f"**Inklusi tampilan:** {inclusion}")
            eligibility = str(availability.get("public_release_eligibility", "NOT_ASSESSED"))
            eligibility_labels = {
                "NOT_ASSESSED": "Belum dinilai",
                "ELIGIBLE": "Layak berdasarkan pemeriksaan yang tercatat",
                "INELIGIBLE": "Tidak layak menurut keputusan yang tercatat",
            }
            st.write(f"**Kelayakan rilis publik:** {eligibility_labels.get(eligibility, eligibility)}")
            exclusion_reason = availability.get("exclusion_reason")
            if exclusion_reason:
                st.write(f"**Alasan tidak ditampilkan:** {exclusion_reason}")
            elif state == "internal_aggregate_verified":
                st.write("**Alasan tidak ditampilkan:** Alasan pemilihan indikator untuk paket tampilan belum terdokumentasi.")
            if source_details:
                st.markdown("**Kode nilai dan aturan lompatan**")
                for source in source_details:
                    st.markdown(f"- **{source.get('code', '')}** · nilai/kode: {source.get('valid_values') or 'tidak dicantumkan'} · aturan lompatan: {source.get('skip_rule') or 'tidak dicantumkan'}")


def dictionary():
    page_head(
        "7", "Memahami indikator", "Kamus indikator",
        "Apa arti kode, satuan, dan cara hitung setiap indikator?",
        "Cari indikator menurut nama, kode, atau bidang; buka definisinya untuk melihat sumber dan cara membacanya.",
    )
    state_counts = {
        "included_in_candidate": sum(item.get("state") == "included_in_candidate" for item in AVAILABILITY_BY_CODE.values()),
        "internal_aggregate_verified": sum(item.get("state") == "internal_aggregate_verified" for item in AVAILABILITY_BY_CODE.values()),
        "constant_uninformative": sum(item.get("state") == "constant_uninformative" for item in AVAILABILITY_BY_CODE.values()),
        "availability_unverified": sum(item.get("state") == "availability_unverified" for item in AVAILABILITY_BY_CODE.values()),
    }
    with st.container(key="dictionary_stats"):
        stats = st.columns(5, gap="small")
        for col, (value, eyebrow, label) in zip(stats, [
            (len(CAT), "KATALOG", "indikator"),
            (state_counts["included_in_candidate"], "TAMPILAN", "nilai pembanding di paket"),
            (state_counts["internal_aggregate_verified"], "RISET PRIVAT", "agregat internal terverifikasi"),
            (state_counts["constant_uninformative"], "KETERBATASAN", "indikator konstan"),
            (state_counts["availability_unverified"], "VERIFIKASI", "menunggu verifikasi"),
        ]):
            with col:
                with st.container(border=True):
                    st.markdown(
                        f'<div class="dictionary-stat"><span class="dictionary-stat-kicker">{eyebrow}</span>'
                        f'<strong>{idnum(value,0)}</strong><span>{html.escape(label)}</span></div>',
                        unsafe_allow_html=True,
                    )
    st.markdown(
        f'<div class="dictionary-intro"><b>Status dipisahkan.</b> {state_counts["included_in_candidate"]} indikator memiliki angka di paket tampilan; '
        f'{state_counts["internal_aggregate_verified"]} tercatat sebagai agregat terverifikasi secara internal, tetapi nilai agregatnya tidak dimuat ke paket publik; '
        f'{state_counts["constant_uninformative"]} bersumber dari indikator konstan. Kelayakan rilis publik untuk nilai tambahan belum dinilai.</div>',
        unsafe_allow_html=True,
    )

    query_col, domain_col, status_col = st.columns([1.35, .9, 1.05], gap="small")
    with query_col:
        query = st.text_input("Cari indikator", key="dictionary_search", placeholder="Nama, kode, atau variabel sumber", help="Pencarian memeriksa nama, kode, bidang, dan kode sumber.")
    with domain_col:
        domain = st.selectbox("Bidang", ["Semua bidang"] + sorted(CAT.domain.unique().tolist()), key="dictionary_domain")
    with status_col:
        status = st.selectbox(
            "Tampilan nilai",
            ["Semua indikator", "Nilai ditampilkan", "Agregat terverifikasi secara internal", "Indikator konstan", "Menunggu verifikasi"],
            key="dictionary_status",
        )

    frame = CAT.copy()
    if domain != "Semua bidang":
        frame = frame[frame.domain == domain]
    states = frame.code.astype(str).map(lambda code: AVAILABILITY_BY_CODE.get(code, {}).get("state", "availability_unverified"))
    if status == "Nilai ditampilkan":
        frame = frame[states == "included_in_candidate"]
    elif status == "Agregat terverifikasi secara internal":
        frame = frame[states == "internal_aggregate_verified"]
    elif status == "Indikator konstan":
        frame = frame[states == "constant_uninformative"]
    elif status == "Menunggu verifikasi":
        frame = frame[states == "availability_unverified"]
    if query.strip():
        term = query.strip()
        searchable = []
        for code in frame.code.astype(str):
            item = INDICATOR_BY_CODE.get(code, {})
            variable_text = " ".join(
                str(source.get("code", "")) + " " + str(source.get("label", ""))
                for source in item.get("source_variable_details", [])
            )
            searchable.append(variable_text)
        mask = (
            frame["name"].fillna("").astype(str).str.contains(term, case=False, regex=False)
            | frame["code"].fillna("").astype(str).str.contains(term, case=False, regex=False)
            | frame["domain"].fillna("").astype(str).str.contains(term, case=False, regex=False)
            | pd.Series(searchable, index=frame.index).str.contains(term, case=False, regex=False)
        )
        frame = frame[mask]

    st.markdown(
        f'<div class="search-count">{idnum(len(frame),0)} hasil <span>dari {idnum(len(CAT),0)} indikator</span></div>',
        unsafe_allow_html=True,
    )
    if frame.empty:
        st.info("Tidak ada indikator yang cocok. Coba istilah, kode, atau bidang yang lebih umum.")
        footer(7)
        return

    for category, category_frame in frame.groupby("domain", sort=True):
        st.markdown(
            f'<div class="dictionary-category"><span>{html.escape(str(category))}</span><i>{len(category_frame)} indikator</i></div>',
            unsafe_allow_html=True,
        )
        rows = list(category_frame.iterrows())
        for start in range(0, len(rows), 2):
            columns = st.columns(2, gap="small")
            for column, (_, row) in zip(columns, rows[start:start + 2]):
                with column:
                    render_indicator_card(row)

    with st.expander("Cara membaca angka dan definisi"):
        st.markdown(
            "- **Persentase desa/kelurahan** adalah proporsi unit wilayah yang memenuhi ciri, bukan proporsi penduduk.\n"
            "- **Poin persentase** adalah selisih antara dua persentase.\n"
            "- **Agregat terverifikasi secara internal** berarti angka cocok dengan rekonsiliasi riset, tetapi tidak termasuk dalam paket tampilan.\n"
            "- **Tidak termasuk dalam paket tampilan** tidak menyatakan bahwa angka nol atau bahwa ada keputusan kerahasiaan. Untuk indikator yang alasannya tidak tercatat, statusnya dinyatakan langsung.\n"
            "- **Indikator konstan** berarti sumber tidak bervariasi dalam cakupan penelitian sehingga tidak membedakan kelompok.\n"
            "- **Kelayakan rilis publik** diperiksa terpisah; status yang belum dinilai bukan persetujuan publikasi."
        )
    footer(7)


def methods():
    page_head("8", "Memahami metode dan batas", "Metode & keterbatasan", "Bagaimana informasi berubah menjadi cerita data?", "Ringkasan menjelaskan cara menggunakan temuan; rincian analitis dan batas penelitian tersedia pada tab berikutnya.")
    st.markdown('<div class="section-kicker">Dari sumber ke tampilan</div><div class="section-heading">Lima langkah penelitian</div>', unsafe_allow_html=True)
    steps = [
        ("01","Sumber","Agregat PODES 2025 dan status klasifikasi resmi 2025."),
        ("02","Integrasi","Sumber disandingkan pada unit desa/kelurahan dalam paket penelitian."),
        ("03","Analisis","Perbandingan karakteristik dan cakupan pada tujuh kabupaten/kota."),
        ("04","Evaluasi","Dua model diuji; satu kabupaten/kota disisihkan pada setiap putaran."),
        ("05","Sajian lokal","Agregat, sumber, definisi, dan batas interpretasi ditampilkan bersama."),
    ]
    flow_html = '<div class="method-flow">' + "".join(f'<section class="method-step"><div class="method-number">LANGKAH {n}</div><div class="method-title">{html.escape(title)}</div><div class="method-copy">{html.escape(copy)}</div></section>' for n,title,copy in steps) + '</div>'
    st.markdown(flow_html, unsafe_allow_html=True)
    general, research = st.tabs(["Ringkasan Umum", "Analisis Penelitian"])
    with general:
        st.markdown("### Cakupan Penelitian")
        st.write("Analisis mencakup 393 desa/kelurahan di Kepulauan Bangka Belitung: 151 berstatus perkotaan dan 242 perdesaan. Perbandingan karakteristik dan evaluasi model membantu membaca pola data; model tidak menetapkan status resmi dan tidak menggantikan klasifikasi BPS.")
        st.markdown("### Batas Interpretasi")
        st.write("Persentase pada halaman perbandingan adalah persentase desa/kelurahan. Jumlah pada peta dan grafik antarwilayah bukan jumlah penduduk, luas wilayah, maupun ukuran kesejahteraan. Perbedaan deskriptif tidak menjelaskan penyebabnya.")
        st.markdown("### Privasi dan Keamanan Data")
        st.write("Tampilan ini menggunakan ringkasan wilayah. Mikrodata PODES, identitas desa, dan prediksi per unit tidak ditampilkan. Geometri administrasi disederhanakan untuk visualisasi dan bukan peta legal.")
    with research:
        st.markdown("### Sumber, target, dan evaluasi")
        st.write("Unit analisis adalah desa/kelurahan di Kepulauan Bangka Belitung. Status klasifikasi resmi 2025 dicocokkan pada 393 dari 393 unit; target menggunakan PODES 2024, sedangkan karakteristik model berasal dari PODES 2025. Rujukan klasifikasi yang digunakan penelitian ialah Perka BPS 268/2025.")
        st.write("Logistic Regression dan Random Forest dievaluasi dengan skema berlapis dan pengelompokan kecamatan. Uji leave-one-kabupaten/kota-out mencakup tujuh wilayah; MCC tersedia pada enam fold karena Pangkalpinang hanya memiliki satu kelas pada fold uji. Nilai yang tidak terdefinisi tidak diperlakukan sebagai nol.")
        st.markdown("### Definisi dan sumber indikator")
        st.write("Kamus menyediakan nama, definisi operasional, sumber variabel, satuan, dan rumus untuk 34 indikator. Penjelasan berasal dari dokumentasi penelitian dan kamus variabel; kecocokan definisi formal belum diperiksa satu per satu terhadap kuesioner primer BPS.")
        st.markdown("### Model dan batas penggunaan")
        st.write("Tidak ada model final yang dipilih. Hasil menunjukkan pengenalan pola pada data evaluasi di satu provinsi, bukan prediksi masa depan, pengganti klasifikasi resmi, atau bukti sebab-akibat. Hubungan konsep antarfitur dan kriteria klasifikasi belum cukup untuk menyatakan seluruh fitur bebas dari kebocoran.")
        with st.expander("Audit Target dan Fitur"):
            st.markdown("**Untuk pembaca umum**")
            st.write("Label resmi dicocokkan pada seluruh 393 desa/kelurahan. Label memakai referensi PODES 2024, sedangkan masukan model berasal dari PODES 2025; hasil ini menilai kecocokan pola pada periode yang berbeda, bukan menghitung ulang aturan resmi atau meramal status masa depan.")
            st.write("Sebagian masukan berhubungan secara konsep dengan unsur yang dipakai dalam klasifikasi. Hubungan itu perlu ditelaah, tetapi belum membuktikan kebocoran langsung. Karena itu, hasil tidak menyatakan bahwa semua fitur bebas kebocoran.")
            st.markdown("**Rincian teknis untuk peneliti**")
            st.write("Skor klasifikasi resmi tidak direkonstruksi karena variabel R401a–R401d tidak didiseminasikan. Target 2025 dicocokkan langsung ke lampiran Perka BPS 268/2025 (393/393); target bersumber dari PODES 2024 dan prediktor dari PODES 2025.")
            feature_summary = APPROVED_FEATURE_AUDIT.get("summary", {})
            if feature_summary:
                feature_count = int(feature_summary.get("feature_count", 0))
                pair_count = int(feature_summary.get("pair_count", 0))
                exact_pairs = int(feature_summary.get("exact_equal_pairs", 0))
                ab_flags = int(feature_summary.get("observed_a_to_b_mappings", 0))
                ba_flags = int(feature_summary.get("observed_b_to_a_mappings", 0))
                valid_spearman = int(feature_summary.get("spearman_nonnull_pairs", 0))
                corr_threshold = 0.80
                st.write(f"Audit lineage memetakan {feature_count} calon fitur ke bagian kuesioner. Audit overlap membandingkan {pair_count} pasangan pada 393 unit: {exact_pairs} pasangan identik, {ab_flags} tanda pemetaan A→B, {ba_flags} tanda B→A, serta {valid_spearman} nilai korelasi Spearman yang terhitung. R503 konstan dan dikeluarkan dari seluruh set model.")
                strong_pairs = APPROVED_FEATURE_AUDIT.get("strong_pairs", [])
                st.write(f"Dengan ambang |Spearman ρ| ≥ {idnum(corr_threshold,2)}, terdapat {len(strong_pairs)} pasangan kuat. Korelasi tidak membuktikan hubungan semantik atau kebocoran langsung; aturan lompatan kuesioner dapat menghasilkan asosiasi tinggi.")
                if strong_pairs:
                    pair_lines = "\n".join(f"- `{pair['feature_a']}` ↔ `{pair['feature_b']}` · Spearman ρ = {idnum(pair['spearman'],3)}" for pair in strong_pairs)
                    st.markdown(pair_lines)
            else:
                st.info("Ringkasan audit fitur tidak tersedia dalam paket rilis; rincian numerik tidak direkonstruksi.")
            st.write("R906A menanyakan bidang usaha dominan. Variabel ini secara konsep berdekatan dengan komponen persentase rumah tangga pertanian dalam metode klasifikasi, tetapi mengukur hal berbeda dan berasal dari vintage yang berbeda. Audit tidak menemukan bukti kebocoran langsung dari R906A; risiko proxy konseptual tetap ada.")
            st.write("Tidak ada set fitur yang disertifikasi bebas kebocoran: audit pasangan mengukur kesamaan empiris, sedangkan pemeriksaan hubungan tiap butir dengan kriteria resmi dan aturan lompat kuesioner belum cukup untuk memberi sertifikasi.")
            st.write("Validasi leave-one-kabupaten/kota-out masih berada dalam satu provinsi; fold Pangkalpinang hanya memiliki satu kelas sehingga MCC tidak terdefinisi pada fold tersebut (6 dari 7 fold memiliki MCC). Validasi lintas provinsi tidak dilakukan, dan tidak ada model final yang dipilih.")
        with st.expander("Ketersediaan nilai dan cakupan katalog"):
            n_in_candidate = sum(item.get("state") == "included_in_candidate" for item in AVAILABILITY_BY_CODE.values())
            n_internal = sum(item.get("state") == "internal_aggregate_verified" for item in AVAILABILITY_BY_CODE.values())
            n_constant = sum(item.get("state") == "constant_uninformative" for item in AVAILABILITY_BY_CODE.values())
            st.write(f"Katalog memuat {len(CAT)} indikator. Nilai perbandingan berada dalam paket tampilan untuk {n_in_candidate} kode. Rekonsiliasi penelitian mencatat {n_internal} kode dengan agregat terverifikasi secara internal; nilai numeriknya tidak disertakan dalam paket publik. Satu indikator ({n_constant}) bersumber dari variabel konstan dan tidak membedakan kelompok.")
            st.write("G03 (R304B, Jumlah RT) memiliki agregat cakupan, perkotaan, dan perdesaan yang telah direkonsiliasi, tetapi tidak termasuk dalam 12 kode pembanding. Alasan pemilihan indikator untuk paket tampilan belum terdokumentasi. Nilai numeriknya tidak disertakan dalam paket publik.")
            st.caption("Ketersediaan pada rekonsiliasi tidak dengan sendirinya menjadi persetujuan untuk publikasi; kelayakan rilis publik untuk angka tambahan belum dinilai.")
        st.markdown("### Geometri dan cakupan wilayah")
        st.write("Peta menampilkan batas administrasi BIG, RBI skala 1:50.000, referensi 2023, yang disederhanakan untuk visualisasi. Peta bukan produk batas legal. Hasil penelitian hanya menggambarkan cakupan Bangka Belitung pada periode yang digunakan.")
    st.markdown('<div class="analysis-note"><b>Batas kesimpulan:</b> gunakan temuan sebagai ringkasan deskriptif dan evaluasi model untuk cakupan penelitian, bukan sebagai dasar klasifikasi resmi, ukuran kesejahteraan, atau gambaran kondisi setiap penduduk.</div>', unsafe_allow_html=True)
    footer(None)


pages = [
    st.Page(home, title="Ringkasan wilayah", default=True),
    st.Page(contrast, title="Perkotaan dan perdesaan", url_path="perkotaan-perdesaan"),
    st.Page(regional, title="Cakupan antarwilayah", url_path="antarwilayah"),
    st.Page(spatial, title="Peta cakupan", url_path="peta-spasial"),
    st.Page(performance, title="Kinerja model", url_path="kinerja-model"),
    st.Page(factors, title="Informasi model", url_path="faktor-pembeda"),
    st.Page(dictionary, title="Kamus indikator", url_path="kamus-indikator"),
    st.Page(methods, title="Metode dan batas", url_path="metode"),
]
nav = st.navigation(pages, position="hidden")

SIDEBAR_TITLES = [
    "Ringkasan",
    "Kota & perdesaan",
    "Cakupan wilayah",
    "Peta wilayah",
    "Kinerja model",
    "Informasi model",
    "Kamus indikator",
    "Metode & batas",
]


with st.sidebar:
    st.markdown(
        f'<header class="pw-brand"><img class="pw-brand-logo" alt="Badan Pusat Statistik Provinsi Kepulauan Bangka Belitung" src="data:image/png;base64,{BPS_LOGO}">'
        '<div class="pw-brand-title">Potret Wilayah</div>'
        '<p class="pw-brand-subtitle">Bangka Belitung · Data 2025</p></header>',
        unsafe_allow_html=True,
    )
    with st.container(key="pw_sidebar_navigation"):
        for group_title, indexes in [
            ("Jelajahi wilayah", range(0, 4)),
            ("Baca hasil model", range(4, 6)),
            ("Panduan data", range(6, 8)),
        ]:
            st.markdown(f'<h2 class="pw-nav-heading">{html.escape(group_title)}</h2>', unsafe_allow_html=True)
            for index in indexes:
                st.page_link(pages[index], label=SIDEBAR_TITLES[index], icon=SIDEBAR_ICONS[index], width="stretch")
    st.markdown('<div class="pw-sidebar-disclaimer">Prototipe akademik independen · bukan publikasi resmi BPS</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="pw-sidebar-reference"><b>Referensi data</b><br>PODES 2025 · {idnum(P["total"],0)} desa/kelurahan<br><br>Status wilayah mengikuti sumber klasifikasi resmi 2025. Geometri administrasi mengacu pada BIG.</div>',
        unsafe_allow_html=True,
    )

nav.run()
