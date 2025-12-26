# app.py — INSAMAR | Visualizador Ventas (Recauchados 2025)
# Requiere: streamlit, pandas, openpyxl, plotly
# Ejecuta: streamlit run app.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import date

# =========================
# 0) Config
# =========================
st.set_page_config(
    page_title="INSAMAR | Ventas Recauchados 2025",
    page_icon="📊",
    layout="wide",
)

# =========================
# 1) Paleta (derivada del logo que compartiste)
# =========================
COL_BG = "#000F30"       # navy profundo
COL_PANEL = "#031A46"    # panel/vidrio
COL_ACCENT = "#0D9CD8"   # cian
COL_ACCENT_2 = "#3867A6" # azul medio
COL_TEXT = "#E3E3E8"     # gris muy claro
COL_MUTED = "#A9B3C7"    # muted
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

/* Tipografía y links */
html, body, [class*="css"] {{
  color: {COL_TEXT};
}}
a {{ color: {COL_ACCENT}; }}

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

/* Cards KPIs */
.kpi-grid {{
  display:grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 10px;
}}
.kpi {{
  background: rgba(3,26,70,0.62);
  border: 1px solid rgba(227,227,232,0.12);
  border-radius: 18px;
  padding: 14px 14px 12px 14px;
  box-shadow: 0 16px 36px rgba(0,0,0,0.25);
  backdrop-filter: blur(10px);
}}
.kpi .label {{
  font-size: 12px;
  color: {COL_MUTED};
}}
.kpi .value {{
  font-size: 22px;
  font-weight: 800;
  margin-top: 6px;
}}
.kpi .hint {{
  margin-top: 6px;
  font-size: 11px;
  color: rgba(227,227,232,0.70);
}}

/* Paneles */
.panel {{
  background: rgba(3,26,70,0.50);
  border: 1px solid rgba(227,227,232,0.12);
  border-radius: 18px;
  padding: 14px;
  box-shadow: 0 14px 34px rgba(0,0,0,0.22);
  backdrop-filter: blur(10px);
}}

/* Dataframe */
[data-testid="stDataFrame"] {{
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid rgba(227,227,232,0.12);
}}

/* Sidebar */
section[data-testid="stSidebar"] {{
  background: linear-gradient(180deg, rgba(3,26,70,0.85), rgba(0,8,31,0.95));
  border-right: 1px solid rgba(227,227,232,0.10);
}}
section[data-testid="stSidebar"] * {{
  color: {COL_TEXT};
}}
</style>
    """,
    unsafe_allow_html=True,
)

# =========================
# 3) Helpers
# =========================
def _fmt_clp(x: float) -> str:
    if pd.isna(x): return "—"
    return f"${x:,.0f}".replace(",", ".")

def _fmt_usd(x: float) -> str:
    if pd.isna(x): return "—"
    return f"US$ {x:,.0f}"

def _safe_col(df: pd.DataFrame, candidates: list[str]) -> str | None:
    cols = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in cols:
            return cols[cand.lower()]
    # fuzzy contains
    for cand in candidates:
        for c in df.columns:
            if cand.lower() in c.lower():
                return c
    return None

@st.cache_data(show_spinner=False)
def load_data_from_excel(file) -> pd.DataFrame:
    df = pd.read_excel(file, sheet_name="Data venta")
    # Normaliza nombres esperados
    col_date = _safe_col(df, ["Fecha de contabilización", "Fecha"])
    if col_date:
        df[col_date] = pd.to_datetime(df[col_date], errors="coerce")
        df = df[df[col_date].notna()].copy()
        df.rename(columns={col_date: "Fecha"}, inplace=True)
    else:
        # fallback: buscar primera col datetime-like
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

    # columnas mínimas
    required = ["Fecha", "Documento", "Cliente", "Vendedor", "Producto", "Cantidad", "PrecioUnit", "VentaCLP"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas esperadas: {missing}. Revisa la hoja 'Data venta'.")

    # tipos
    df["Cantidad"] = pd.to_numeric(df["Cantidad"], errors="coerce").fillna(0)
    df["PrecioUnit"] = pd.to_numeric(df["PrecioUnit"], errors="coerce").fillna(0)
    df["VentaCLP"] = pd.to_numeric(df["VentaCLP"], errors="coerce").fillna(0)

    # Derivadas útiles
    df["Año"] = df["Fecha"].dt.year
    df["Mes"] = df["Fecha"].dt.to_period("M").astype(str)
    df["Trimestre"] = df["Fecha"].dt.to_period("Q").astype(str)
    df["TicketPromCLP"] = np.where(df["Cantidad"] > 0, df["VentaCLP"] / df["Cantidad"], np.nan)

    return df

def kpi_cards(kpis: list[tuple[str, str, str]]):
    # kpis: [(label, value, hint), ...]
    html = '<div class="kpi-grid">'
    for label, value, hint in kpis:
        html += f"""
        <div class="kpi">
          <div class="label">{label}</div>
          <div class="value">{value}</div>
          <div class="hint">{hint}</div>
        </div>
        """
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

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

# Fallback local (tu archivo en el entorno)
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
    d1, d2 = st.date_input("Rango de fechas", value=(min_d, max_d), min_value=min_d, max_value=max_d)

    clientes = sorted(df["Cliente"].dropna().unique().tolist())
    vendedores = sorted(df["Vendedor"].dropna().unique().tolist())

    sel_clientes = st.multiselect("Cliente(s)", options=clientes, default=[])
    sel_vendedores = st.multiselect("Vendedor(es)", options=vendedores, default=[])

    txt_producto = st.text_input("Buscar producto (contiene)", value="", help="Ej: 11R22.5, 295/80R22.5, PBA60, etc.")

    st.markdown("---")
    st.markdown("### 🧭 Agrupación")
    group_main = st.selectbox(
        "Agrupar análisis por",
        options=["Mes", "Trimestre", "Cliente", "Vendedor", "Producto"],
        index=0
    )
    top_n = st.slider("Top N (clientes/productos)", 5, 30, 12)

# Aplica filtros
mask = (df["Fecha"].dt.date >= d1) & (df["Fecha"].dt.date <= d2)
if sel_clientes:
    mask &= df["Cliente"].isin(sel_clientes)
if sel_vendedores:
    mask &= df["Vendedor"].isin(sel_vendedores)
if txt_producto.strip():
    mask &= df["Producto"].str.contains(txt_producto.strip(), case=False, na=False)

dff = df[mask].copy()

# =========================
# 7) KPIs principales
# =========================
total_clp = float(dff["VentaCLP"].sum())
total_qty = float(dff["Cantidad"].sum())
avg_ticket = float(dff["VentaCLP"].sum() / max(dff["Cantidad"].sum(), 1))
docs = int(dff["Documento"].nunique())
custs = int(dff["Cliente"].nunique())

kpis = [
    ("Venta total (CLP)", _fmt_clp(total_clp), "Suma de “Venta” en el rango filtrado"),
    ("Unidades", f"{total_qty:,.0f}".replace(",", "."), "Suma de “Quantity”"),
    ("Precio prom. por unidad", _fmt_clp(avg_ticket), "Venta / Unidades (promedio ponderado)"),
    ("Documentos", f"{docs:,}".replace(",", "."), "N° interno único"),
    ("Clientes únicos", f"{custs:,}".replace(",", "."), "Clientes distintos en el período"),
]
kpi_cards(kpis)

if show_usd:
    st.caption(f"Conversión informativa: 1 USD = {usd_rate:,.0f} CLP".replace(",", "."))
    kpis_usd = [
        ("Venta total (USD)", _fmt_usd(total_clp / usd_rate), "CLP → USD (tipo cambio indicado)"),
        ("Precio prom. (USD/ud)", _fmt_usd(avg_ticket / usd_rate), "Promedio ponderado (CLP → USD)"),
    ]
    kpi_cards(kpis_usd)

st.markdown("---")

# =========================
# 8) Visualizaciones (autoexplicativas)
# =========================
colA, colB = st.columns([1.15, 0.85], gap="large")

with colA:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("#### 📈 Evolución de ventas (tendencia)")
    st.caption("Muestra el comportamiento temporal. Útil para detectar estacionalidad, quiebres o picos de demanda.")

    ts = (dff.groupby("Mes", as_index=False)
          .agg(VentaCLP=("VentaCLP", "sum"), Unidades=("Cantidad", "sum"), Docs=("Documento", "nunique")))
    ts = ts.sort_values("Mes")

    fig_ts = px.line(
        ts, x="Mes", y="VentaCLP",
        markers=True,
        title=None,
        hover_data={"Unidades": True, "Docs": True, "VentaCLP": ":,.0f"},
    )
    fig_ts.update_layout(
        height=380,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=COL_TEXT),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor=COL_GRID),
    )
    st.plotly_chart(fig_ts, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with colB:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("#### 🧩 Distribución de precio unitario")
    st.caption("Sirve para ver dispersión de precios y outliers (posibles errores o casos especiales).")

    fig_hist = px.histogram(
        dff,
        x="PrecioUnit",
        nbins=40,
        title=None,
        hover_data=["Producto", "Cliente", "Vendedor"]
    )
    fig_hist.update_layout(
        height=380,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=COL_TEXT),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor=COL_GRID),
    )
    st.plotly_chart(fig_hist, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("")

colC, colD = st.columns([1, 1], gap="large")

with colC:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("#### 🥇 Top productos por venta")
    st.caption("Ranking para focalizar gestión comercial, abastecimiento y mix de productos.")

    top_prod = (dff.groupby("Producto", as_index=False)
                .agg(VentaCLP=("VentaCLP", "sum"), Unidades=("Cantidad", "sum")))
    top_prod = top_prod.sort_values("VentaCLP", ascending=False).head(top_n)

    fig_prod = px.bar(
        top_prod.sort_values("VentaCLP"),
        x="VentaCLP", y="Producto",
        orientation="h",
        title=None,
        hover_data={"Unidades": True, "VentaCLP": ":,.0f"}
    )
    fig_prod.update_layout(
        height=520,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=COL_TEXT),
        xaxis=dict(showgrid=True, gridcolor=COL_GRID),
        yaxis=dict(showgrid=False),
    )
    st.plotly_chart(fig_prod, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with colD:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("#### 🧑‍💼 Top clientes por venta")
    st.caption("Identifica concentración de ingresos y cartera crítica. Útil para priorizar retención y acuerdos.")

    top_cli = (dff.groupby("Cliente", as_index=False)
               .agg(VentaCLP=("VentaCLP", "sum"), Unidades=("Cantidad", "sum"), Docs=("Documento", "nunique")))
    top_cli = top_cli.sort_values("VentaCLP", ascending=False).head(top_n)

    fig_cli = px.bar(
        top_cli.sort_values("VentaCLP"),
        x="VentaCLP", y="Cliente",
        orientation="h",
        title=None,
        hover_data={"Unidades": True, "Docs": True, "VentaCLP": ":,.0f"}
    )
    fig_cli.update_layout(
        height=520,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=COL_TEXT),
        xaxis=dict(showgrid=True, gridcolor=COL_GRID),
        yaxis=dict(showgrid=False),
    )
    st.plotly_chart(fig_cli, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# =========================
# 9) Vista “Director”: tabla resumen + detalle
# =========================
st.markdown("### 🧾 Vista Director (resumen + detalle)")
st.caption("Un bloque para decidir: resumen por dimensión elegida + tabla de detalle filtrada (exportable).")

agg_map = {
    "Mes": ["Mes"],
    "Trimestre": ["Trimestre"],
    "Cliente": ["Cliente"],
    "Vendedor": ["Vendedor"],
    "Producto": ["Producto"],
}
gcols = agg_map[group_main]

summary = (dff.groupby(gcols, as_index=False)
           .agg(
                VentaCLP=("VentaCLP", "sum"),
                Unidades=("Cantidad", "sum"),
                Docs=("Documento", "nunique"),
                Clientes=("Cliente", "nunique"),
                PrecioPromCLP=("TicketPromCLP", "mean"),
            ))
summary["PrecioPromCLP"] = np.where(summary["Unidades"] > 0, summary["VentaCLP"] / summary["Unidades"], np.nan)
summary = summary.sort_values("VentaCLP", ascending=False)

c1, c2 = st.columns([1, 1], gap="large")

with c1:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("#### Resumen agregado")
    st.dataframe(
        summary.head(40),
        use_container_width=True,
        hide_index=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("#### Detalle (filtrado)")
    st.dataframe(
        dff.sort_values("Fecha", ascending=False).head(2000),
        use_container_width=True,
        hide_index=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

# Export
st.markdown("")

export_cols = ["Fecha","Documento","CodCliente","Cliente","Vendedor","ItemCode","Producto","Cantidad","PrecioUnit","VentaCLP","Mes","Trimestre"]
export_cols = [c for c in export_cols if c in dff.columns]
csv_bytes = dff[export_cols].to_csv(index=False).encode("utf-8")

st.download_button(
    "⬇️ Descargar datos filtrados (CSV)",
    data=csv_bytes,
    file_name="INSAMAR_ventas_filtradas.csv",
    mime="text/csv",
)

with st.expander("🧠 Cómo leer este dashboard (2 minutos)"):
    st.markdown(
        """
**Qué hace esto**
- Permite **filtrar** ventas por fecha, cliente, vendedor y texto en producto.
- Entrega **KPIs operativos** (venta, unidades, precio promedio ponderado, documentos, clientes).
- Muestra **tendencia mensual**, distribución de precios, y rankings por producto/cliente.
- Incluye vista “director” con **resumen agregable** + **detalle exportable**.

**Definiciones**
- **Venta total**: suma de la columna “Venta”.
- **Unidades**: suma de “Quantity”.
- **Precio prom. por unidad**: Venta / Unidades (ponderado).
- **Documento**: “Número interno” único.

**Usos típicos**
- Detectar meses pico/bajo, clientes concentrados, productos dominantes, outliers de precio.
        """
    )

