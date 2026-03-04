import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from io import BytesIO

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard PAUD – Tangerang Selatan",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* ══════════════════════════════════════════════════════════════════
       CSS VARIABLES — Light Mode (default)
    ══════════════════════════════════════════════════════════════════ */
    :root {
        --bg-main:        linear-gradient(135deg, #f0f4ff 0%, #faf5ff 100%);
        --bg-sidebar:     rgba(255, 255, 255, 0.97);
        --bg-card:        #ffffff;
        --bg-table-even:  #f9fafb;
        --bg-table-hover: #eef2ff;
        --bg-input:       #ffffff;

        --text-primary:   #1f2937;
        --text-heading:   #111827;
        --text-muted:     #6b7280;
        --text-label:     #374151;

        --border:         #e5e7eb;
        --accent:         #4f46e5;
        --accent-light:   #818cf8;
        --shadow-card:    0 2px 14px rgba(79,70,229,.12);
        --shadow-table:   0 1px 8px rgba(0,0,0,.07);
    }

    /* ══════════════════════════════════════════════════════════════════
       CSS VARIABLES — Dark Mode
    ══════════════════════════════════════════════════════════════════ */
    @media (prefers-color-scheme: dark) {
        :root {
            --bg-main:        linear-gradient(135deg, #0f1117 0%, #1a1b2e 100%);
            --bg-sidebar:     rgba(22, 23, 36, 0.98);
            --bg-card:        #1e2030;
            --bg-table-even:  #1a1c2e;
            --bg-table-hover: #2d2f4d;
            --bg-input:       #1e2030;

            --text-primary:   #e5e7eb;
            --text-heading:   #f9fafb;
            --text-muted:     #9ca3af;
            --text-label:     #d1d5db;

            --border:         #374151;
            --accent:         #818cf8;
            --accent-light:   #4f46e5;
            --shadow-card:    0 2px 14px rgba(0,0,0,.4);
            --shadow-table:   0 1px 8px rgba(0,0,0,.3);
        }
    }

    /* ══════════════════════════════════════════════════════════════════
       BASE — Apply variables to Streamlit elements
    ══════════════════════════════════════════════════════════════════ */
    [data-testid="stAppViewContainer"] { background: var(--bg-main) !important; }
    [data-testid="stSidebar"]          { background: var(--bg-sidebar) !important; }
    [data-testid="stHeader"]           { background: transparent !important; }

    /* Text */
    html, body, [class*="css"], p, span, div, label { color: var(--text-primary) !important; }
    h1, h2, h3, h4, h5 { color: var(--text-heading) !important; }
    .stMarkdown p, .stMarkdown li { color: var(--text-primary) !important; }
    small, caption, .stCaption { color: var(--text-muted) !important; }
    a { color: var(--accent) !important; }

    /* Inputs */
    input, select, textarea {
        background: var(--bg-input) !important;
        color: var(--text-primary) !important;
        border-color: var(--border) !important;
        min-height: 42px;
        font-size: 1rem !important;
    }

    /* ── Metric cards ─────────────────────────────────────────────── */
    .metric-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 1rem 1.2rem;
        box-shadow: var(--shadow-card);
        text-align: center;
        margin-bottom: 0.5rem;
        transition: transform .15s ease, box-shadow .15s ease;
    }
    .metric-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-card); }
    .metric-card h2 { font-size: 2rem; font-weight: 700; color: var(--accent) !important; margin: 0; }
    .metric-card p  { color: var(--text-muted) !important; margin: 0; font-size: .78rem;
                      letter-spacing: .06em; text-transform: uppercase; }

    /* ── Section titles ───────────────────────────────────────────── */
    .section-title { font-size: 1.05rem; font-weight: 600;
                     color: var(--text-heading) !important; margin-bottom: .4rem; }

    /* ── Table ────────────────────────────────────────────────────── */
    .table-wrapper {
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        border-radius: 10px;
        box-shadow: var(--shadow-table);
        border: 1px solid var(--border);
    }
    table  { width: 100%; border-collapse: collapse; font-size: 0.8rem;
             min-width: 700px; white-space: nowrap; }
    th     { background: var(--accent) !important; color: #fff !important;
             padding: 9px 12px; text-align: left; position: sticky; top: 0; }
    td     { padding: 6px 12px; border-bottom: 1px solid var(--border);
             color: var(--text-primary) !important;
             background: var(--bg-card); }
    tr:nth-child(even) td { background: var(--bg-table-even) !important; }
    tr:hover td            { background: var(--bg-table-hover) !important; }

    /* ── Sidebar ──────────────────────────────────────────────────── */
    [data-testid="stSidebar"] label { color: var(--text-label) !important; font-weight: 500; }
    [data-testid="stSidebar"] small,
    [data-testid="stSidebar"] .stCaption p { color: var(--text-muted) !important; }
    [data-testid="stSidebarContent"] { padding-top: 1rem; }

    /* ── Buttons ──────────────────────────────────────────────────── */
    .stDownloadButton button, .stButton button {
        background: var(--accent) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: opacity .15s;
    }
    .stDownloadButton button:hover, .stButton button:hover { opacity: .85; }

    /* ══════════════════════════════════════════════════════════════════
       RESPONSIVE — Tablet ≤ 1024px
    ══════════════════════════════════════════════════════════════════ */
    @media (max-width: 1024px) {
        .metric-card h2 { font-size: 1.75rem !important; }
    }

    /* ══════════════════════════════════════════════════════════════════
       RESPONSIVE — Mobile ≤ 768px
    ══════════════════════════════════════════════════════════════════ */
    @media (max-width: 768px) {
        [data-testid="stAppViewBlockContainer"] { padding: 0.5rem 0.75rem !important; }

        .metric-card { padding: 0.75rem 0.8rem; }
        .metric-card h2 { font-size: 1.5rem !important; }
        .metric-card p  { font-size: 0.7rem !important; }

        [data-testid="stPlotlyChart"] { max-height: 260px; overflow: hidden; }

        table { font-size: 0.74rem; }
        th, td { padding: 5px 8px; }

        .section-title { font-size: 0.92rem; }
        h1 { font-size: 1.35rem !important; }
        h2 { font-size: 1.05rem !important; }
        h3 { font-size: 0.98rem !important; }

        [data-testid="column"] { min-width: 100% !important; }
    }

    /* ══════════════════════════════════════════════════════════════════
       RESPONSIVE — Small phones ≤ 480px
    ══════════════════════════════════════════════════════════════════ */
    @media (max-width: 480px) {
        .metric-card h2 { font-size: 1.2rem !important; }
        .metric-card p  { font-size: 0.65rem !important; }
        h1 { font-size: 1.15rem !important; }
    }
</style>
""", unsafe_allow_html=True)


# ─── Load Data ──────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    data_path = Path(__file__).parent / "data.json"
    with open(data_path, encoding="utf-8") as f:
        raw = json.load(f)

    rows = []
    for item in raw:
        det = item.get("details") or {}
        api = det.get("profil_api") or {}
        rows.append({
            "NPSN":               item.get("npsn", ""),
            "Nama Sekolah":       item.get("nama_sekolah", ""),
            "Kecamatan":          item.get("kecamatan", ""),
            "Kelurahan":          item.get("kelurahan", ""),
            "Alamat":             item.get("jalan") or det.get("Alamat", ""),
            "Status":             item.get("status", ""),
            "Akreditasi":         det.get("Akreditasi", "-"),
            "Bentuk Pendidikan":  det.get("Bentuk Pendidikan", "-"),
            "Luas Tanah":         det.get("Luas Tanah", "-"),
            "Telepon":            det.get("Telepon") or api.get("Telepon API") or "-",
            "Email":              det.get("Email") or api.get("Email API") or "-",
            "Website":            det.get("Website", "-"),
            "Kepala Sekolah":     api.get("Kepala Sekolah", "-"),
            "Guru L":             api.get("Guru Laki-laki", 0),
            "Guru P":             api.get("Guru Perempuan", 0),
            "Profil URL":         det.get("Profil Sekolah URL", ""),
        })
    return pd.DataFrame(rows)


@st.cache_data
def load_excel_data():
    """Build a comprehensive DataFrame with ALL fields including profil_api details."""
    data_path = Path(__file__).parent / "data.json"
    with open(data_path, encoding="utf-8") as f:
        raw = json.load(f)

    rows = []
    for item in raw:
        det = item.get("details") or {}
        api = det.get("profil_api") or {}
        rows.append({
            "NPSN":                  item.get("npsn", ""),
            "Nama Sekolah":          item.get("nama_sekolah", ""),
            "Kecamatan":             item.get("kecamatan", ""),
            "Kelurahan":             item.get("kelurahan", ""),
            "Alamat":                item.get("jalan") or det.get("Alamat", ""),
            "Status":                item.get("status", ""),
            "Bentuk Pendidikan":     det.get("Bentuk Pendidikan", "-"),
            "Akreditasi":            det.get("Akreditasi", "-"),
            "Luas Tanah":            det.get("Luas Tanah", "-"),
            "Naungan":               det.get("Naungan", "-"),
            "No SK Pendirian":       det.get("No. SK. Pendirian", "-"),
            "Tanggal SK Pendirian":  det.get("Tanggal SK. Pendirian", "-"),
            "Kementerian Pembina":   det.get("Kementerian Pembina", "-"),
            "Telepon":               det.get("Telepon") or api.get("Telepon API") or "-",
            "Email":                 det.get("Email") or api.get("Email API") or "-",
            "Website":               det.get("Website", "-"),
            "Profil URL":            det.get("Profil Sekolah URL", ""),
            "Kepala Sekolah":        api.get("Kepala Sekolah", "-"),
            "Operator Satuan":       api.get("Operator", "-"),
            "Guru Laki-laki":        api.get("Guru Laki-laki", 0),
            "Guru Perempuan":        api.get("Guru Perempuan", 0),
            "Total Guru":            (api.get("Guru Laki-laki") or 0) + (api.get("Guru Perempuan") or 0),
            "Siswa Laki-laki":       api.get("Siswa Laki-laki", "-"),
            "Siswa Perempuan":       api.get("Siswa Perempuan", "-"),
            "Ruang Kelas":           api.get("Ruang Kelas", 0),
            "Ruang Perpustakaan":    api.get("Ruang Perpustakaan", 0),
            "Lintang":               det.get("Lintang", ""),
            "Bujur":                 det.get("Bujur", ""),
        })
    return pd.DataFrame(rows)


def to_excel_bytes(df: pd.DataFrame) -> bytes:
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Data PAUD")
        ws = writer.sheets["Data PAUD"]
        # Auto-size columns
        for col in ws.columns:
            max_len = max((len(str(cell.value or "")) for cell in col), default=10)
            ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 60)
    return buf.getvalue()


df_all = load_data()

# ─── Sidebar Filters ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("# 🏫")
    st.markdown("## Filter Data PAUD")
    st.divider()

    kec_opts = ["Semua"] + sorted(df_all["Kecamatan"].unique().tolist())
    sel_kec = st.selectbox("Kecamatan", kec_opts)

    df_kel = df_all if sel_kec == "Semua" else df_all[df_all["Kecamatan"] == sel_kec]
    kel_opts = ["Semua"] + sorted(df_kel["Kelurahan"].unique().tolist())
    sel_kel = st.selectbox("Kelurahan", kel_opts)

    status_opts = ["Semua"] + sorted(df_all["Status"].dropna().unique().tolist())
    sel_status = st.selectbox("Status", status_opts)

    akr_opts = ["Semua"] + sorted(df_all["Akreditasi"].unique().tolist())
    sel_akr = st.selectbox("Akreditasi", akr_opts)

    bentuk_opts = ["Semua"] + sorted(df_all["Bentuk Pendidikan"].unique().tolist())
    sel_bentuk = st.selectbox("Bentuk Pendidikan", bentuk_opts)

    search = st.text_input("🔍 Cari nama / NPSN")
    st.divider()

    # ── Export Section ──────────────────────────────────────────────────────────
    st.markdown("### 📥 Export Data")
    export_scope = st.radio("Ekspor:", ["Data yang difilter", "Semua data (917 sekolah)"], horizontal=True)

    # Pre-generate Excel (cached as long as filter hasn't changed)
    if export_scope == "Semua data (917 sekolah)":
        df_export = load_excel_data()
        fname = "PAUD_TangerangSelatan_Lengkap.xlsx"
    else:
        df_export = load_excel_data()
        if sel_kec    != "Semua": df_export = df_export[df_export["Kecamatan"]        == sel_kec]
        if sel_kel    != "Semua": df_export = df_export[df_export["Kelurahan"]         == sel_kel]
        if sel_status != "Semua": df_export = df_export[df_export["Status"]            == sel_status]
        if sel_akr    != "Semua": df_export = df_export[df_export["Akreditasi"]        == sel_akr]
        if sel_bentuk != "Semua": df_export = df_export[df_export["Bentuk Pendidikan"] == sel_bentuk]
        if search:
            q2 = search.lower()
            df_export = df_export[
                df_export["Nama Sekolah"].str.lower().str.contains(q2) |
                df_export["NPSN"].str.lower().str.contains(q2)
            ]
        fname = "PAUD_TangerangSelatan_Filter.xlsx"

    excel_bytes = to_excel_bytes(df_export)
    st.download_button(
        label=f"⬇️ Download Excel ({len(df_export)} baris)",
        data=excel_bytes,
        file_name=fname,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
    st.divider()
    st.caption("Data: Kemendikdasmen · Tangerang Selatan")


# ─── Apply Filters ──────────────────────────────────────────────────────────────
df = df_all.copy()
if sel_kec != "Semua":
    df = df[df["Kecamatan"] == sel_kec]
if sel_kel != "Semua":
    df = df[df["Kelurahan"] == sel_kel]
if sel_status != "Semua":
    df = df[df["Status"] == sel_status]
if sel_akr != "Semua":
    df = df[df["Akreditasi"] == sel_akr]
if sel_bentuk != "Semua":
    df = df[df["Bentuk Pendidikan"] == sel_bentuk]
if search:
    q = search.lower()
    df = df[df["Nama Sekolah"].str.lower().str.contains(q) |
            df["NPSN"].str.lower().str.contains(q) |
            df["Alamat"].str.lower().str.contains(q)]


# ─── Header Metrics ─────────────────────────────────────────────────────────────
st.markdown("# 🏫 Dashboard PAUD · Kota Tangerang Selatan")
st.caption("Sumber data: referensi.data.kemendikdasmen.go.id & sekolah.data.kemendikdasmen.go.id")
st.divider()

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="metric-card"><h2>{len(df)}</h2><p>Total PAUD (filter)</p></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-card"><h2>{df["Kecamatan"].nunique()}</h2><p>Kecamatan</p></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-card"><h2>{df["Kelurahan"].nunique()}</h2><p>Kelurahan</p></div>', unsafe_allow_html=True)
with c4:
    pct_akr = round(100 * len(df[df["Akreditasi"].isin(["A","B","C"])]) / max(len(df), 1))
    st.markdown(f'<div class="metric-card"><h2>{pct_akr}%</h2><p>Sudah Akreditasi</p></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Charts Row 1 ───────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-title">📊 Berdasarkan Kecamatan</div>', unsafe_allow_html=True)
    kec_count = df.groupby("Kecamatan").size().reset_index(name="Jumlah").sort_values("Jumlah", ascending=False)
    fig_kec = px.bar(kec_count, x="Kecamatan", y="Jumlah", color="Jumlah",
                     color_continuous_scale=["#818cf8", "#4f46e5"],
                     text="Jumlah", template="plotly_white")
    fig_kec.update_layout(showlegend=False, coloraxis_showscale=False, height=320,
                          margin=dict(t=10, b=10))
    fig_kec.update_traces(textposition="outside")
    st.plotly_chart(fig_kec, use_container_width=True)

with col2:
    st.markdown('<div class="section-title">🍩 Berdasarkan Status</div>', unsafe_allow_html=True)
    stat_count = df.groupby("Status").size().reset_index(name="Jumlah")
    fig_stat = px.pie(stat_count, names="Status", values="Jumlah",
                      color_discrete_sequence=["#10b981", "#4f46e5", "#ec4899"],
                      hole=0.5, template="plotly_white")
    fig_stat.update_layout(height=320, margin=dict(t=10, b=10))
    st.plotly_chart(fig_stat, use_container_width=True)

# ─── Charts Row 2 ───────────────────────────────────────────────────────────────
col3, col4 = st.columns(2)

with col3:
    st.markdown('<div class="section-title">🎖️ Berdasarkan Akreditasi</div>', unsafe_allow_html=True)
    akr_count = df.groupby("Akreditasi").size().reset_index(name="Jumlah")
    akr_color = {"A": "#10b981", "B": "#3b82f6", "C": "#f59e0b",
                 "-": "#9ca3af", "Belum Ada": "#9ca3af"}
    fig_akr = px.pie(akr_count, names="Akreditasi", values="Jumlah",
                     color="Akreditasi",
                     color_discrete_map=akr_color,
                     hole=0.5, template="plotly_white")
    fig_akr.update_layout(height=320, margin=dict(t=10, b=10))
    st.plotly_chart(fig_akr, use_container_width=True)

with col4:
    st.markdown('<div class="section-title">🏫 Berdasarkan Bentuk Pendidikan</div>', unsafe_allow_html=True)
    bentuk_count = df.groupby("Bentuk Pendidikan").size().reset_index(name="Jumlah").sort_values("Jumlah", ascending=False)
    palette = ["#4f46e5", "#10b981", "#f59e0b", "#ec4899", "#3b82f6", "#ea580c"]
    fig_bentuk = px.bar(bentuk_count, x="Bentuk Pendidikan", y="Jumlah",
                        color="Bentuk Pendidikan",
                        color_discrete_sequence=palette,
                        text="Jumlah", template="plotly_white")
    fig_bentuk.update_layout(showlegend=False, height=320, margin=dict(t=10, b=10))
    fig_bentuk.update_traces(textposition="outside")
    st.plotly_chart(fig_bentuk, use_container_width=True)

st.divider()

# ─── Directory Table ─────────────────────────────────────────────────────────────
st.markdown(f'<div class="section-title">📋 Direktori PAUD ({len(df)} sekolah)</div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Make Nama Sekolah a clickable link using HTML
def make_link(row):
    if row["Profil URL"]:
        return f'<a href="{row["Profil URL"]}" target="_blank">{row["Nama Sekolah"]}</a>'
    return row["Nama Sekolah"]

def make_website(url):
    if url and url not in ["-", "http://", ""]:
        if not url.startswith("http"):
            url = "http://" + url
        return f'<a href="{url}" target="_blank">Link</a>'
    return "-"

df_display = df[[
    "NPSN", "Nama Sekolah", "Kecamatan", "Kelurahan",
    "Status", "Akreditasi", "Bentuk Pendidikan",
    "Luas Tanah", "Alamat", "Website", "Profil URL"
]].copy()

df_display["Nama Sekolah"] = df_display.apply(make_link, axis=1)
df_display["Website"] = df_display["Website"].apply(make_website)
df_display = df_display.drop(columns=["Profil URL"])
df_display.index = range(1, len(df_display) + 1)

st.write(
    '<div class="table-wrapper">' + df_display.to_html(escape=False, index=True) + '</div>',
    unsafe_allow_html=True
)

st.divider()

# ─── Detail Section ─────────────────────────────────────────────────────────────
st.markdown("### 🔍 Detail Sekolah")
st.caption("Cari menggunakan NPSN (angka) atau sebagian nama sekolah.")

detail_query = st.text_input("Masukkan NPSN atau nama sekolah:", placeholder="cth: 69818802  atau  TK HARAPAN")

def show_detail_card(r):
    profil_url = r["Profil URL"]
    col_a, col_b = st.columns(2)
    with col_a:
        name_md = f"[{r['Nama Sekolah']}]({profil_url})" if profil_url else r['Nama Sekolah']
        st.markdown(f"**Nama Sekolah**: {name_md}")
        st.markdown(f"**NPSN**: {r['NPSN']}")
        st.markdown(f"**Status**: {r['Status']}")
        st.markdown(f"**Akreditasi**: {r['Akreditasi']}")
        st.markdown(f"**Bentuk Pendidikan**: {r['Bentuk Pendidikan']}")
        st.markdown(f"**Kepala Sekolah**: {r['Kepala Sekolah']}")
        st.markdown(f"**Guru (L/P)**: {r['Guru L']} / {r['Guru P']}")
    with col_b:
        st.markdown(f"**Kecamatan**: {r['Kecamatan']}")
        st.markdown(f"**Kelurahan**: {r['Kelurahan']}")
        st.markdown(f"**Alamat**: {r['Alamat']}")
        st.markdown(f"**Luas Tanah**: {r['Luas Tanah']}")
        st.markdown(f"**Telepon**: {r['Telepon']}")
        st.markdown(f"**Email**: {r['Email']}")
        if profil_url:
            st.markdown(f"**Profil Sekolah**: [{profil_url}]({profil_url})")
        if r["Website"] not in ["-", "http://", ""]:
            st.markdown(f"**Website**: [{r['Website']}]({r['Website']})")

if detail_query:
    q = detail_query.strip()

    # --- 1. Try exact NPSN match first ---
    by_npsn = df_all[df_all["NPSN"] == q]
    if not by_npsn.empty:
        st.success(f"Ditemukan via NPSN: **{by_npsn.iloc[0]['Nama Sekolah']}**")
        show_detail_card(by_npsn.iloc[0])

    else:
        # --- 2. Fuzzy name search ---
        matches = df_all[df_all["Nama Sekolah"].str.upper().str.contains(q.upper(), na=False)]

        if matches.empty:
            st.warning(f"Tidak ditemukan hasil untuk `{q}`. Coba kata kunci lain atau NPSN yang benar.")
        elif len(matches) == 1:
            st.success(f"Ditemukan 1 sekolah: **{matches.iloc[0]['Nama Sekolah']}**")
            show_detail_card(matches.iloc[0])
        else:
            st.info(f"Ditemukan **{len(matches)}** sekolah. Pilih salah satu:")
            options = matches["Nama Sekolah"] + " (" + matches["NPSN"] + ")"
            sel = st.selectbox("Pilih sekolah:", options.tolist())
            sel_npsn = sel.split("(")[-1].rstrip(")")
            sel_row = matches[matches["NPSN"] == sel_npsn].iloc[0]
            show_detail_card(sel_row)

