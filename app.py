# app.py — INSAMAR | Visualizador Ventas (Recauchados 2025)
# Requiere: streamlit, pandas, openpyxl, plotly
# Ejecuta: streamlit run app.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# =========================
# 0) Config
# =========================
st.set_page_config(
    page_title="INSAMAR | Ventas Recauchados 2025",
    page_icon="📊",
    layout="wide",
)

# =========================
# 1) Paleta (derivada del logo)
# =========================
COL_BG = "#000F30"        # navy profundo
COL_PANEL = "#031A46"     # panel/vidrio
COL_ACCENT = "#0D9CD8"    # cian
COL_ACCENT_2 = "#3867A6"  # azul medio
COL_TEXT = "#E3E3E8"      # gris muy claro
COL_MUTED = "#A9B3C7"     # muted
COL_GRID = "rgba(227,227,232,0.12)"

# =========================
# 2) CSS — estilo “artistico abierto”
# =========================
st.markdown(
    f"""
<style>
/* Fondo general */
.stApp {{
  background: radial-gradient(1200px 700px at 15% 10%, rgba(13,156,216,0.18), transparent 60%),
              radial-gradient(900px 600px at 80% 30%, rgba(56,103,166,0.18), transparent 55%),
              linear-gradient(180deg, {COL_BG} 0%, #00081F 100%);
  color: {COL_TEXT};
}}
html, body, [class*="css"] {{ color: {COL_TEXT}; }}
a {{ color: {COL_ACCENT}; }}

/* Sidebar look */
section[data-testid="stSidebar"] {{
  background: linear-gradient(180deg, rgba(0,15,48,0.92), rgba(0,8,31,0.92)) !important;
  border-right: 1px solid rgba(227,227,232,0.10);
}}

/* Panel “vidrio” */
.panel {{
  background: rgba(3,26,70,0.35);
  border: 1px solid rgba(227,227,232,0.14);
  border-radius: 18px;
  padding: 16px 16px 10px 16px;
  box-shadow: 0 16px 40px rgba(0,0,0,0.30);
}}

/* Header marca */
.brand {{
  display:flex; align-items:center; gap:14px;
  margin: 4px 0 10px 0;
}}
.badge {{
  width: 44px; height: 44px; border-radius: 14px;
  background: linear-gradient(135deg, rgba(13,156,216,0.95), rgba(56,103,166,0.95));
  box-shadow: 0 12px 30px rgba(0,0,0,0.35);
  position: relative;
  overflow:hidden;
}}
.badge:before {{
  content:"";
  position:absolute; inset:-40%;
  background: radial-gradient(circle at 30% 30%, rgba(255,255,255,0.55), transparent 45%);
  transform: rotate(20deg);
}}
.title {{
  font-size: 28px; font-weight: 800; letter-spacing: 0.6px;
}}
.subtitle {{
  margin-top:-6px;
  font-size: 13px; color: {COL_MUTED};
}}

/* KPIs */
.kpi-grid {{
  display:grid;
  grid-template-columns: repeat(5, minmax(160px, 1fr));
  gap: 12px;
  margin: 10px 0 8px 0;
}}
.kpi {{
  background: rgba(3,26,70,0.35);
  border: 1px solid rgba(227,227,232,0.14);
  border-radius: 16px;
  padding: 12px 12px 10px 12px;
}}
.kpi .label {{
  font-size: 12px;
  color: {COL_MUTED};
  margin-bottom: 6px;
}}
.kpi .value {{
  font-size: 22px;
  font-weight: 800;
  letter-spacing: 0.2px;
}}
.kpi .hint {{
  font-size: 11px;
  color: rgba(227,227,232,0.65);
  margin-top: 6px;
}}

/* File uploader dropzone */
div[data-testid="stFileUploaderDropzone"] {{
  background: rgba(3,26,70,0.35) !important;
  border: 1px dashed rgba(227,227,232,0.22) !important;
  border-radius: 18px !important;
}}
div[data-testid="stFileUploaderDropzone"] * {{
  color: {COL_TEXT} !important;
}}
div[data-testid="stFileUploaderDropzone"] button {{
  background: rgba(13,156,216,0.18) !important;
  color: {COL_TEXT} !important;
  border: 1px solid rgba(13,156,216,0.55) !important;
  border-radius: 14px !important;
}}

/* Botones Streamlit (incluye download) */
.stButton > button,
div[data-testid="stDownloadButton"] > button {{
  background: linear-gradient(135deg, rgba(13,156,216,0.35), rgba(56,103,166,0.35)) !important;
  color: {COL_TEXT} !important;
  border: 1px solid rgba(227,227,232,0.18) !important;
  border-radius: 14px !important;
  box-shadow: 0 10px 24px rgba(0,0,0,0.25) !important;
}}
.stButton > button:hover,
div[data-testid="stDownloadButton"] > button:hover {{
  border: 1px solid rgba(13,156,216,0.55) !important;
}}

/* ====== FIX “fondos blancos” en widgets (inputs/selects/date/multiselect/slider) ====== */
div[data-baseweb="base-input"] > div {{
  background: rgba(3,26,70,0.35) !important;
  border: 1px solid rgba(227,227,232,0.18) !important;
  border-radius: 14px !important;
}}
div[data-baseweb="base-input"] input,
div[data-baseweb="base-input"] textarea {{
  background: transparent !important;
  color: {COL_TEXT} !important;
}}
div[data-baseweb="select"] > div {{
  background: rgba(3,26,70,0.35) !important;
  border: 1px solid rgba(227,227,232,0.18) !important;
  border-radius: 14px !important;
}}
div[data-baseweb="select"] * {{
  color: {COL_TEXT} !important;
}}
/* Date picker popover */
div[data-baseweb="popover"] > div {{
  background: rgba(0,15,48,0.98) !important;
  border: 1px solid rgba(227,227,232,0.18) !important;
}}
/* Slider track */
div[data-testid="stSlider"] [data-baseweb="slider"] > div {{
  background: rgba(227,227,232,0.14) !important;
}}
/* Dataframes */
div[data-testid="stDataFrame"] {{
  background: rgba(3,26,70,0.20) !important;
  border-radius: 14px !important;
}}
</style>
    """,
    unsafe_allow_html=True,
)

# =========================
# 3) Helpers
# =========================
def _fmt_clp(x: float) -> str:
    if pd.isna(x):
        return "—"
    return f"${x:,.0f}".replace(",", ".")

def _fmt_usd(x: float) -> str:
    if pd.isna(x):
        return "—"
    return f"US$ {x:,.0f}"

def _safe_col(df: pd.DataFrame, candidates: list[str]) -> str | None:
    cols = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in cols:
            return cols[cand.lower()]
    for cand in candidates:
        for c in df.columns:
            if cand.lower() in c.lower():
                return c
    return None

@st.cache_data(show_spinner=False)
def load_data_from_excel(file) -> pd.DataFrame:
    df = pd.read_excel(file, sheet_name="Data venta")

    # Fecha
    col_date = _safe_col(df, ["Fecha de contabilización", "Fecha"])
    if col_date:
        df[col_date] = pd.to_datetime(df[col_date], errors="coerce")
        df = df[df[col_date].notna()].copy()
        df.rename(columns={col_date: "Fecha"}, inplace=True)
    else:
        for c in df.columns:
            if "fecha" in c.lower():
                df[c] = pd.to_datetime(df[c], errors="coerce")
                if df[c].notna().any():
                    df.rename(columns={c: "Fecha"}, inplace=True)
                    df = df[df["Fecha"].notna()].copy()
                    break

    rename_map = {}
    rename_map[_safe_col(df, ["Número interno", "Numero interno", "DocNum", "Documento"])] = "Documento"
    rename_map[_safe_col(df, ["Código de cliente/proveedor", "Codigo de cliente", "CardCode"])] = "CodCliente"
    rename_map[_safe_col(df, ["Nombre de cliente/proveedor", "Nombre de cliente", "CardName"])] = "Cliente"
    rename_map[_safe_col(df, ["SlpName", "Vendedor", "Ejecutivo"])] = "Vendedor"
    rename_map[_safe_col(df, ["ItemCode", "Codigo item", "Item"])] = "ItemCode"
    rename_map[_safe_col(df, ["Dscription", "Descripcion", "Description"])] = "Producto"
    rename_map[_safe_col(df, ["Quantity", "Cantidad"])] = "Cantidad"
    rename_map[_safe_col(df, ["Price", "Precio"])] = "PrecioUnit"
    rename_map[_safe_col(df, ["Venta", "Total", "Monto"])] = "VentaCLP"

    rename_map = {k: v for k, v in rename_map.items() if k is not None}
    df.rename(columns=rename_map, inplace=True)

    required = ["Fecha", "Documento", "Cliente", "Vendedor", "Producto", "Cantidad", "PrecioUnit", "VentaCLP"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas esperadas: {missing}. Revisa la hoja 'Data venta'.")

    df["Cantidad"] = pd.to_numeric(df["Cantidad"], errors="coerce").fillna(0)
    df["PrecioUnit"] = pd.to_numeric(df["PrecioUnit"], errors="coerce").fillna(0)
    df["VentaCLP"] = pd.to_numeric(df["VentaCLP"], errors="coerce").fillna(0)

    df["Año"] = df["Fecha"].dt.year
    df["Mes"] = df["Fecha"].dt.to_period("M").astype(str)
    df["Trimestre"] = df["Fecha"].dt.to_period("Q").astype(str)
    df["TicketPromCLP"] = np.where(df["Cantidad"] > 0, df["VentaCLP"] / df["Cantidad"], np.nan)

    return df

def kpi_cards(kpis: list[tuple[str, str, str]]):
    # Fix: no indent HTML lines (para que Markdown no lo interprete como code block)
    parts = ['<div class="kpi-grid">']
    for label, value, hint in kpis:
        parts.append(
            f'<div class="kpi">'
            f'<div class="label">{label}</div>'
            f'<div class="value">{value}</div>'
            f'<div class="hint">{hint}</div>'
            f'</div>'
        )
    parts.append("</div>")
    st.markdown("".join(parts), unsafe_allow_html=True)

# =========================
# 4) Header
# =========================
st.markdown(
    """
<div class="brand">
  <div class="badge"></div>
  <div>
    <div class="title">INSAMAR</div>
    <div class="subtitle">Visualizador dinámico — Ventas Recauchados 2025 (auditoría-ready)</div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# =========================
# 5) Carga de datos
# =========================
with st.sidebar:
    st.markdown("### 📁 Datos")
    uploaded = st.file_uploader("Sube el Excel (o usa el archivo por defecto)", type=["xlsx", "xlsm"])

    st.markdown("---")
    st.markdown("### 💱 Conversión (opcional)")
    usd_rate = st.number_input("Tipo de cambio (CLP por 1 USD)", min_value=100, max_value=2000, value=950, step=10)
    show_usd = st.toggle("Mostrar métricas también en USD", value=True)

default_path = "Venta Recauchados 2025 (18 dic).xlsx"

try:
    data_source = uploaded if uploaded is not None else default_path
    df = load_data_from_excel(data_source)
except Exception as e:
    st.error(f"No pude cargar la hoja 'Data venta'. Detalle: {e}")
    st.stop()

# =========================
# 6) Filtros
# =========================
with st.sidebar:
    st.markdown("### 🎛️ Filtros")

    min_d = df["Fecha"].min().date()
    max_d = df["Fecha"].max().date()

    d1, d2 = st.date_input(
        "Rango de fechas",
        value=(min_d, max_d),
        min_value=min_d,
        max_value=max_d,
    )

    clientes = sorted(df["Cliente"].dropna().unique().tolist())
    vendedores = sorted(df["Vendedor"].dropna().unique().tolist())

    sel_clientes = st.multiselect("Cliente(s)", options=clientes, default=[])
    sel_vendedores = st.multiselect("Vendedor(es)", options=vendedores, default=[])

    txt_producto = st.text_input(
        "Buscar producto (contiene)",
        value="",
        help="Ej: 11R22.5, 295/80R22.5, PBA60, etc.",
    )

    st.markdown("---")
    st.markdown("### 🧭 Agrupación")
    group_main = st.selectbox(
        "Agrupar análisis por",
        options=["Mes", "Trimestre", "Cliente", "Vendedor", "Producto"],
        index=0,
    )
    top_n = st.slider("Top N (clientes/productos)", 5, 30, 12)

# === FIX CRÍTICO: la línea del mask va completa (sin paréntesis abiertos) ===
mask = (df["Fecha"].dt.date >= d1) & (df["Fecha"].dt.date <= d2)
if sel_clientes:
    mask &= df["Cliente"].isin(sel_clientes)
if sel_vendedores:
    mask &= df["Vendedor"].isin(sel_vendedores)
if txt_producto.strip():
    mask &= df["Producto"].astype(str).str.contains(txt_producto.strip(), case=False, na=False)

dff = df[mask].copy()

# =========================
# 7) KPIs principales
# =========================
total_clp = float(dff["VentaCLP"].sum())
total_qty = float(dff["Cantidad"].sum())
avg_unit = float(dff["VentaCLP"].sum() / max(dff["Cantidad"].sum(), 1))
docs = int(dff["Documento"].nunique())
custs = int(dff["Cliente"].nunique())

kpis = [
    ("Venta total (CLP)", _fmt_clp(total_clp), "Suma de “Venta” en el rango filtrado"),
    ("Unidades", f"{total_qty:,.0f}".replace(",", "."), "Suma de “Quantity”"),
    ("Precio prom. por unidad", _fmt_clp(avg_unit), "Venta / Unidades (promedio ponderado)"),
    ("Documentos", f"{docs:,}".replace(",", "."), "N° interno único"),
    ("Clientes únicos", f"{custs:,}".replace(",", "."), "Clientes distintos en el período"),
]
kpi_cards(kpis)

if show_usd:
    st.caption(f"Conversión informativa: 1 USD = {usd_rate:,.0f} CLP".replace(",", "."))
    kpis_usd = [
        ("Venta total (USD)", _fmt_usd(total_clp / usd_rate), "CLP → USD (tipo cambio indicado)"),
        ("Precio prom. (USD/ud)", _fmt_usd(avg_unit / usd_rate), "Promedio ponderado (CLP → USD)"),
    ]
    kpi_cards(kpis_usd)

st.markdown("---")

# =========================
# 8) Visualizaciones
# =========================
colA, colB = st.columns([1.15, 0.85], gap="large")

with colA:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("#### 📈 Evolución de ventas (tendencia)")
    st.caption("Comportamiento temporal. Útil para estacionalidad, quiebres o picos de demanda.")

    ts = (
        dff.groupby("Mes", as_index=False)
        .agg(VentaCLP=("VentaCLP", "sum"), Unidades=("Cantidad", "sum"), Docs=("Documento", "nunique"))
        .sort_values("Mes")
    )

    fig_ts = px.line(
        ts,
        x="Mes",
        y="VentaCLP",
        markers=True,
        hover_data={"Unidades": True, "Docs": True, "VentaCLP": ":,.0f"},
    )
    fig_ts.update_layout(
        height=380,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=COL_TEXT),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor=COL
