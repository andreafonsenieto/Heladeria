"""
Heladería La Dulce 🍦 — App de Ventas con Frontend Blanco Estilo Heladería
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime, timedelta
from database import init_db, insertar_venta, obtener_ventas

# ── Config ────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="🍦 Heladería La Dulce", page_icon="🍦",
                   layout="wide", initial_sidebar_state="collapsed")
init_db()

# ── Catálogo de Helados y Productos ───────────────────────────────────────────
PRODUCTOS = [
    {"nombre":"Helado Vainilla",   "emoji":"🍦","precio":8000, "desc":"Clásica crema de vainilla bourbon", "cat":"Clásicos",  "color":"#FFB703"},
    {"nombre":"Helado Chocolate",  "emoji":"🍫","precio":8000, "desc":"Puro cacao suizo semiamargo",       "cat":"Clásicos",  "color":"#8B5E3C"},
    {"nombre":"Helado Fresa",      "emoji":"🍓","precio":8000, "desc":"Fresas frescas con toque de nata",   "cat":"Clásicos",  "color":"#FF4D8D"},
    {"nombre":"Helado Mango",      "emoji":"🥭","precio":8500, "desc":"Mango biche dulce y refrescante",   "cat":"Frutales",  "color":"#FB8500"},
    {"nombre":"Helado Maracuyá",   "emoji":"🍊","precio":8500, "desc":"Fruta de la pasión tropical",       "cat":"Frutales",  "color":"#FF7B00"},
    {"nombre":"Helado Coco",       "emoji":"🥥","precio":8500, "desc":"Cremosa leche de coco caribeña",    "cat":"Frutales",  "color":"#2EC4B6"},
    {"nombre":"Sundae Brownie",    "emoji":"🍨","precio":15000,"desc":"Con brownie caliente y fudge",       "cat":"Especiales","color":"#E63946"},
    {"nombre":"Copa de Frutas",    "emoji":"🍡","precio":12000,"desc":"Helado artesanal y frutas de temporada","cat":"Especiales","color":"#FF006E"},
    {"nombre":"Malteada Clásica",  "emoji":"🥤","precio":14000,"desc":"Espesa, suave y con crema chantilly","cat":"Bebidas",   "color":"#4CC9F0"},
    {"nombre":"Malteada Oreo",     "emoji":"🍪","precio":16000,"desc":"Cargada de trocitos de galleta Oreo","cat":"Bebidas",   "color":"#4A4E69"},
    {"nombre":"Paleta de Fruta",   "emoji":"🧊","precio":5000, "desc":"Agua pura y 100% fruta natural",     "cat":"Paletas",   "color":"#06D6A0"},
    {"nombre":"Paleta de Crema",   "emoji":"🍬","precio":6000, "desc":"Rellena de dulce de leche cremoso",  "cat":"Paletas",   "color":"#FFB703"},
    {"nombre":"Cono Doble Mixto",  "emoji":"🍦","precio":10000,"desc":"Elige tus 2 sabores favoritos",      "cat":"Clásicos",  "color":"#DDA15E"},
    {"nombre":"Banana Split",      "emoji":"🍌","precio":18000,"desc":"Tres bolas, banano y cerezas",       "cat":"Especiales","color":"#E76F51"},
    {"nombre":"Waffle con Helado", "emoji":"🧇","precio":20000,"desc":"Waffle recién horneado con helado",  "cat":"Especiales","color":"#F4A261"},
]
CATEGORIAS = ["Todos","Clásicos","Frutales","Especiales","Bebidas","Paletas"]
DIAS_ES = {0:"Lunes",1:"Martes",2:"Miércoles",3:"Jueves",4:"Viernes",5:"Sábado",6:"Domingo"}

# ── Session state ─────────────────────────────────────────────────────────────
if "carrito" not in st.session_state:
    st.session_state.carrito = {}
if "pagina" not in st.session_state:
    st.session_state.pagina = "tienda"
if "cat_sel" not in st.session_state:
    st.session_state.cat_sel = "Todos"

# ── CSS GLOBAL — ESTILO HELADERÍA BLANCO Y PASTEL ─────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&family=Pacifico&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"], .stApp, .main, .block-container {
    font-family: 'Nunito', sans-serif !important;
}

/* ═══ FONDO BLANCO HELADERÍA CON TOQUES PASTEL ═══ */
.stApp {
    background: #FFFDF9 !important;
    background-image: 
        radial-gradient(#FFE4EE 1.2px, transparent 1.2px), 
        radial-gradient(#E5F4FF 1.2px, #FFFDF9 1.2px) !important;
    background-size: 40px 40px !important;
    background-position: 0 0, 20px 20px !important;
    min-height: 100vh;
}

/* ═══ CONTENEDOR 100% ANCHO DE PÁGINA (FULL WIDTH ABSOLUTO) ═══ */
.block-container, [data-testid="stMainBlockContainer"] {
    padding-top: 0rem !important;
    padding-bottom: 3.5rem !important;
    padding-left: 0rem !important;
    padding-right: 0rem !important;
    max-width: 100% !important;
    width: 100% !important;
}

/* Ocultar barra superior y decoraciones nativas de Streamlit */
header, [data-testid="stHeader"], [data-testid="stDecoration"],
[data-testid="stToolbar"], #MainMenu, footer, .stDeployButton {
    display: none !important;
    height: 0 !important;
    visibility: hidden !important;
}

[data-testid="stAppViewContainer"], [data-testid="stMain"] {
    padding-top: 0rem !important;
    margin-top: 0rem !important;
}

/* ═══ BARRA DE NAVEGACIÓN FIJA A TODO LO ANCHO DE PANTALLA (STICKY HEADER) ═══ */
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > div:has(#sticky-header-anchor) {
    position: sticky !important;
    top: 0px !important;
    left: 0px !important;
    right: 0px !important;
    z-index: 999999 !important;
    width: 100% !important;
    margin: 0 0 1.2rem 0 !important;
    background: #FFFFFF !important;
    border-bottom: 2px solid #FFD4E5 !important;
    box-shadow: 0 4px 16px rgba(255, 77, 141, 0.08) !important;
    padding: 0.5rem 3.5rem !important;
    box-sizing: border-box !important;
}

/* Evitar que elementos internos del logo hereden bordes o sombras indeseadas */
#sticky-header-anchor,
div[data-testid="stElementContainer"]:has(#sticky-header-anchor),
div[data-testid="stMarkdownContainer"]:has(#sticky-header-anchor) {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    margin: 0 !important;
}

/* Padding para el contenido inferior para alinearlo perfectamente con el header */
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > div:not(:has(#sticky-header-anchor)) {
    padding-left: 3.5rem !important;
    padding-right: 3.5rem !important;
}

div:has(#sticky-header-anchor) > div[data-testid="stVerticalBlock"] {
    gap: 0rem !important;
}

.brand-title {
    font-family: 'Pacifico', cursive !important;
    font-size: 1.65rem;
    color: #FF2E74;
    display: flex;
    align-items: center;
    gap: 0.4rem;
    margin: 0;
    line-height: 1.1;
    letter-spacing: 0.3px;
}
.brand-tagline {
    font-size: 0.76rem;
    color: #8E7A8A;
    font-weight: 700;
    margin-top: 1px;
}

/* Botones de navegación en el header */
div[data-testid="stHorizontalBlock"] .stButton > button {
    border-radius: 50px !important;
    font-weight: 800 !important;
    font-size: 0.92rem !important;
    padding: 0.45rem 1rem !important;
    height: 40px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
div[data-testid="stHorizontalBlock"] .stButton > button[kind="secondary"] {
    background: #FFFFFF !important;
    border: 2px solid #FFE0EE !important;
    color: #4A3E48 !important;
    box-shadow: 0 3px 10px rgba(0,0,0,0.02) !important;
}
div[data-testid="stHorizontalBlock"] .stButton > button[kind="secondary"]:hover {
    background: #FFF0F5 !important;
    color: #FF2E74 !important;
    border-color: #FFADC7 !important;
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(255, 77, 141, 0.16) !important;
}
div[data-testid="stHorizontalBlock"] .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #FF2E74 0%, #FF6584 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    box-shadow: 0 6px 20px rgba(255, 46, 116, 0.35) !important;
}
div[data-testid="stHorizontalBlock"] .stButton > button[kind="primary"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(255, 46, 116, 0.5) !important;
}

/* ═══ HERO BANNER HELADERÍA ═══ */
.hero-card {
    background: linear-gradient(135deg, #FFF0F5 0%, #FFF7E6 50%, #F0F8FF 100%);
    border: 2.5px solid #FFE1ED;
    border-radius: 32px;
    padding: 2.5rem 2rem;
    text-align: center;
    margin-bottom: 2rem;
    box-shadow: 0 12px 36px rgba(255, 130, 170, 0.1);
    position: relative;
    overflow: hidden;
}
.hero-emojis {
    font-size: 3.5rem;
    margin-bottom: 0.5rem;
    animation: floatAnim 3s ease-in-out infinite;
}
@keyframes floatAnim {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-8px); }
}
.hero-title {
    font-family: 'Pacifico', cursive !important;
    font-size: 2.7rem;
    color: #FF3377;
    margin: 0.2rem 0;
}
.hero-subtitle {
    color: #6C5B68;
    font-size: 1.15rem;
    font-weight: 700;
}
.hero-chips {
    display: flex;
    justify-content: center;
    gap: 0.8rem;
    flex-wrap: wrap;
    margin-top: 1.4rem;
}
.hero-chip {
    background: #FFFFFF;
    border: 1.5px solid #FFD4E5;
    color: #FF4081;
    font-size: 0.85rem;
    font-weight: 800;
    padding: 0.4rem 1.2rem;
    border-radius: 50px;
    box-shadow: 0 3px 10px rgba(255, 105, 180, 0.08);
}

/* ═══ TÍTULOS DE SECCIÓN ═══ */
.section-heading {
    font-size: 1.45rem;
    font-weight: 900;
    color: #2D252C;
    margin: 1.5rem 0 1rem 0;
    display: flex;
    align-items: center;
    gap: 0.6rem;
}
.section-heading::before {
    content: '';
    display: inline-block;
    width: 6px;
    height: 1.5rem;
    background: linear-gradient(180deg, #FF4D8D, #FFB703);
    border-radius: 6px;
}

/* ═══ TARJETAS DE PRODUCTOS (BLANCO GELATERIA) ═══ */
.ice-card {
    background: #FFFFFF;
    border: 2px solid #F5E8EE;
    border-radius: 26px;
    padding: 1.5rem 1.2rem 1.2rem;
    text-align: center;
    position: relative;
    box-shadow: 0 8px 24px rgba(200, 160, 180, 0.07);
    transition: all 0.28s cubic-bezier(0.4, 0, 0.2, 1);
    height: 100%;
    margin-bottom: 0.6rem;
}
.ice-card:hover {
    transform: translateY(-7px);
    border-color: #FF99C2;
    box-shadow: 0 16px 36px rgba(255, 77, 141, 0.16);
}
.ice-badge-cat {
    position: absolute;
    top: 14px;
    right: 14px;
    font-size: 0.68rem;
    font-weight: 800;
    text-transform: uppercase;
    background: #FFF0F5;
    color: #FF3377;
    border: 1px solid #FFD4E5;
    padding: 0.2rem 0.65rem;
    border-radius: 30px;
}
.ice-badge-cart {
    position: absolute;
    top: 14px;
    left: 14px;
    background: #06D6A0;
    color: #FFFFFF;
    font-size: 0.72rem;
    font-weight: 900;
    padding: 0.2rem 0.6rem;
    border-radius: 30px;
    box-shadow: 0 2px 8px rgba(6, 214, 160, 0.4);
}
.ice-emoji {
    font-size: 4rem;
    margin: 0.6rem 0 0.3rem 0;
    display: inline-block;
    transition: transform 0.2s ease;
}
.ice-card:hover .ice-emoji {
    transform: scale(1.15) rotate(-5deg);
}
.ice-name {
    font-size: 1.05rem;
    font-weight: 800;
    color: #2D252C;
    margin-bottom: 0.25rem;
}
.ice-desc {
    font-size: 0.8rem;
    color: #7D6C78;
    margin-bottom: 0.75rem;
    min-height: 2.2rem;
    line-height: 1.3;
}
.ice-price {
    font-size: 1.4rem;
    font-weight: 900;
    color: #FF2E74;
    background: #FFF3F7;
    border-radius: 16px;
    padding: 0.3rem 0.8rem;
    display: inline-block;
}

/* ═══ BARRA FLOTANTE DEL PEDIDO ═══ */
.floating-order-bar {
    background: #FFFFFF;
    border: 2.5px solid #FF94BA;
    border-radius: 26px;
    padding: 1.1rem 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 10px 35px rgba(255, 46, 116, 0.18);
    margin: 1.5rem 0 1rem 0;
}
.floating-info {
    font-size: 1.1rem;
    font-weight: 800;
    color: #2D252C;
}
.floating-total {
    font-size: 1.65rem;
    font-weight: 900;
    color: #FF2E74;
}

/* ═══ CAJAS DEL CARRITO ═══ */
.cart-card-panel {
    background: #FFFFFF;
    border: 2px solid #FFE0EE;
    border-radius: 28px;
    padding: 1.8rem;
    box-shadow: 0 8px 30px rgba(255, 114, 160, 0.07);
}
.cart-row-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.9rem 0;
    border-bottom: 1.5px solid #FFF2F7;
}
.cart-item-title {
    font-size: 1rem;
    font-weight: 800;
    color: #2D252C;
}
.cart-item-sub {
    font-size: 0.82rem;
    color: #8C7A87;
}
.cart-item-price {
    font-size: 1.15rem;
    font-weight: 900;
    color: #FF2E74;
}

/* ═══ TARJETAS KPI HISTORIAL ═══ */
.kpi-container {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1.2rem;
    margin-bottom: 2rem;
}
.kpi-box {
    background: #FFFFFF;
    border: 2px solid #FFE3EF;
    border-radius: 24px;
    padding: 1.4rem 1.6rem;
    box-shadow: 0 6px 20px rgba(255, 105, 180, 0.06);
    position: relative;
}
.kpi-box-label {
    font-size: 0.8rem;
    font-weight: 800;
    color: #8E7A8A;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 0.4rem;
}
.kpi-box-val {
    font-size: 1.9rem;
    font-weight: 900;
    color: #2D252C;
}
.kpi-box-icon {
    position: absolute;
    top: 1.2rem;
    right: 1.4rem;
    font-size: 2.2rem;
    opacity: 0.25;
}

/* Botones generales de Streamlit */
.stButton > button {
    background: #FFFFFF !important;
    border: 2px solid #FFD4E5 !important;
    color: #FF3377 !important;
    border-radius: 50px !important;
    font-weight: 800 !important;
    font-family: 'Nunito', sans-serif !important;
    box-shadow: 0 4px 14px rgba(255, 105, 180, 0.08) !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: #FFF0F5 !important;
    border-color: #FF7597 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(255, 51, 119, 0.18) !important;
}

/* Botones principales y de acción */
.stButton button[kind="primary"], .action-btn button {
    background: linear-gradient(135deg, #FF3377 0%, #FF7597 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 50px !important;
    font-weight: 800 !important;
    box-shadow: 0 6px 20px rgba(255, 51, 119, 0.3) !important;
}
.stButton button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 28px rgba(255, 51, 119, 0.45) !important;
}

/* Inputs de texto, fecha y números */
.stTextInput input, .stNumberInput input, .stDateInput input,
div[data-baseweb="input"] input,
div[data-baseweb="base-input"] input,
div[data-baseweb="input"],
div[data-baseweb="base-input"] {
    background: #FFFFFF !important;
    border: 2px solid #FFD9E8 !important;
    border-radius: 14px !important;
    color: #201620 !important;
    font-weight: 700 !important;
}
div[data-testid="stDateInput"] *, div[data-baseweb="calendar"] * {
    color: #201620 !important;
}
div[data-baseweb="calendar"] {
    background: #FFFFFF !important;
}
.stSelectbox div[data-baseweb="select"] {
    background: #FFFFFF !important;
    border: 2px solid #FFD9E8 !important;
    border-radius: 14px !important;
    color: #201620 !important;
}
.stSelectbox div[data-baseweb="select"]:hover, .stNumberInput input:focus {
    border-color: #FF3377 !important;
}

/* Pestañas generales de Streamlit */
.stTabs [data-baseweb="tab-list"] {
    background: #FFFFFF !important;
    border-radius: 50px !important;
    padding: 6px !important;
    gap: 8px !important;
    border: 2px solid #FFE4EE !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 40px !important;
    font-weight: 800 !important;
    color: #7D6C78 !important;
    padding: 0.5rem 1.5rem !important;
}
.stTabs [aria-selected="true"] {
    background: #FF3377 !important;
    color: #FFFFFF !important;
    box-shadow: 0 4px 14px rgba(255, 51, 119, 0.35) !important;
}

p, label, span { color: #332B32; }
</style>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
def total_carrito():
    return sum(next(p["precio"] for p in PRODUCTOS if p["nombre"]==n)*c
               for n,c in st.session_state.carrito.items())

def items_carrito():
    return sum(st.session_state.carrito.values())

def estilizar_figura(fig, titulo="", tipo=""):
    """Aplica formato visual nítido, legible y de alto contraste a las gráficas."""
    fig.update_layout(
        title=dict(
            text=f"<b>{titulo}</b>" if titulo else "",
            font=dict(size=17, color="#1E161D", family="Nunito"),
            x=0.03, y=0.94
        ),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(color="#1E161D", family="Nunito", size=13),
        margin=dict(t=65, b=45, l=45, r=30),
        legend=dict(
            font=dict(size=12, color="#1E161D", family="Nunito"),
            bgcolor="rgba(255, 255, 255, 0.95)",
            bordercolor="#FFD4E5",
            borderwidth=1.5
        )
    )
    if tipo != "pie" and tipo != "polar":
        fig.update_xaxes(
            gridcolor="#F5E6EE",
            gridwidth=1.2,
            linecolor="#CBB5C2",
            linewidth=1.8,
            tickfont=dict(size=12, color="#1E161D", family="Nunito"),
            title_font=dict(size=13, color="#1E161D", family="Nunito")
        )
        fig.update_yaxes(
            gridcolor="#F5E6EE",
            gridwidth=1.2,
            linecolor="#CBB5C2",
            linewidth=1.8,
            tickfont=dict(size=12, color="#1E161D", family="Nunito"),
            title_font=dict(size=13, color="#1E161D", family="Nunito")
        )
    return fig

# ══════════════════════════════════════════════════════════════════════════════
# HEADER Y NAVBAR SUPERIOR FIJO (STICKY NAVBAR)
# ══════════════════════════════════════════════════════════════════════════════
n_items = items_carrito()

with st.container():
    c_brand, c_pills = st.columns([0.9, 2.1], vertical_alignment="center")
    
    with c_brand:
        st.markdown("""
        <div id="sticky-header-anchor" style="display:flex;align-items:center;gap:0.7rem;padding:0;">
          <div style="width:42px;height:42px;border-radius:50%;background:linear-gradient(135deg,#FFF0F5,#FFE4EE);border:2px solid #FFC2D6;display:flex;align-items:center;justify-content:center;font-size:1.5rem;box-shadow:0 3px 10px rgba(255,77,141,0.12);flex-shrink:0;">🍦</div>
          <div>
            <div class="brand-title">Heladería La Dulce</div>
            <div class="brand-tagline">✨ Gelatería Artesanal · 100% Sabor Natural</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        
    with c_pills:
        n1, n2, n3, n4, n5 = st.columns([0.9, 1.1, 1.0, 1.25, 1.25])
        
        with n1:
            is_ini = (st.session_state.pagina == "tienda")
            btn_ini = "🏠 Inicio"
            tipo_ini = "primary" if is_ini else "secondary"
            if st.button(btn_ini, key="nav_btn_tienda", type=tipo_ini, use_container_width=True):
                st.session_state.pagina = "tienda"
                st.rerun()

        with n2:
            is_cart = (st.session_state.pagina == "carrito")
            cart_title = f"🛒 Pedido ({n_items})" if n_items else "🛒 Pedido"
            tipo_cart = "primary" if is_cart else "secondary"
            if st.button(cart_title, key="nav_btn_cart", type=tipo_cart, use_container_width=True):
                st.session_state.pagina = "carrito"
                st.rerun()

        with n3:
            is_hist = (st.session_state.pagina == "historial")
            hist_title = "📋 Historial"
            tipo_hist = "primary" if is_hist else "secondary"
            if st.button(hist_title, key="nav_btn_hist", type=tipo_hist, use_container_width=True):
                st.session_state.pagina = "historial"
                st.rerun()

        with n4:
            is_an = (st.session_state.pagina == "analisis")
            an_title = "🌦️ Clima & Ventas"
            tipo_an = "primary" if is_an else "secondary"
            if st.button(an_title, key="nav_btn_an", type=tipo_an, use_container_width=True):
                st.session_state.pagina = "analisis"
                st.rerun()

        with n5:
            is_pred = (st.session_state.pagina == "predicciones")
            pred_title = "🔮 Predicciones"
            tipo_pred = "primary" if is_pred else "secondary"
            if st.button(pred_title, key="nav_btn_pred", type=tipo_pred, use_container_width=True):
                st.session_state.pagina = "predicciones"
                st.rerun()

st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA 1: TIENDA / MENÚ DE HELADOS
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.pagina == "tienda":

    # Hero Banner
    st.markdown("""
    <div class="hero-card">
      <div class="hero-emojis">🍦🍓🍨🥭🍫🧇</div>
      <div class="hero-title">¡El helado perfecto para tu día!</div>
      <div class="hero-subtitle">Elaborados artesanalmente con fruta 100% natural y leche fresca</div>
      <div class="hero-chips">
        <span class="hero-chip">🍓 Frutas del día</span>
        <span class="hero-chip">🍦 Cremas italianas</span>
        <span class="hero-chip">🧊 0% Conservantes</span>
        <span class="hero-chip">🛵 Envíos a domicilio</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Filtros de Categorías
    st.markdown('<div class="section-heading">Categorías del Menú</div>', unsafe_allow_html=True)
    c_cols = st.columns(len(CATEGORIAS))
    for idx, c_nom in enumerate(CATEGORIAS):
        with c_cols[idx]:
            is_active = (st.session_state.cat_sel == c_nom)
            label = f"✨ {c_nom}" if is_active else c_nom
            if st.button(label, key=f"cat_btn_{c_nom}", use_container_width=True):
                st.session_state.cat_sel = c_nom
                st.rerun()

    # Filtrar productos
    prods_mostrar = PRODUCTOS if st.session_state.cat_sel == "Todos" else [p for p in PRODUCTOS if p["cat"] == st.session_state.cat_sel]

    st.markdown(f'<div class="section-heading">Sabores & Postres &nbsp;<span style="font-size:0.9rem;font-weight:700;color:#8E7A8A">({len(prods_mostrar)} opciones)</span></div>', unsafe_allow_html=True)

    # Grid de tarjetas de productos (4 columnas por fila)
    COLS_FILA = 4
    for i in range(0, len(prods_mostrar), COLS_FILA):
        fila = prods_mostrar[i:i+COLS_FILA]
        cols = st.columns(COLS_FILA)
        for j, p in enumerate(fila):
            with cols[j]:
                cant = st.session_state.carrito.get(p["nombre"], 0)
                badge_cart = f'<div class="ice-badge-cart">✓ {cant} en carrito</div>' if cant > 0 else ''
                
                st.markdown(f"""
                <div class="ice-card">
                  {badge_cart}
                  <div class="ice-badge-cat">{p['cat']}</div>
                  <div class="ice-emoji">{p['emoji']}</div>
                  <div class="ice-name">{p['nombre']}</div>
                  <div class="ice-desc">{p['desc']}</div>
                  <div class="ice-price">${p['precio']:,}</div>
                </div>
                """, unsafe_allow_html=True)

                # Botones para agregar o quitar unidades
                b_menos, b_num, b_mas = st.columns([1, 1.2, 1])
                with b_menos:
                    if st.button("➖", key=f"btn_m_{p['nombre']}", use_container_width=True):
                        if cant > 0:
                            st.session_state.carrito[p["nombre"]] -= 1
                            if st.session_state.carrito[p["nombre"]] == 0:
                                del st.session_state.carrito[p["nombre"]]
                            st.rerun()
                with b_num:
                    st.markdown(f"<div style='text-align:center;font-size:1.15rem;font-weight:900;color:#FF3377;padding-top:0.4rem;'>{cant}</div>", unsafe_allow_html=True)
                with b_mas:
                    if st.button("➕", key=f"btn_p_{p['nombre']}", use_container_width=True):
                        st.session_state.carrito[p["nombre"]] = cant + 1
                        st.rerun()

    # Barra flotante de compra si hay productos en el carrito
    if st.session_state.carrito:
        tot = total_carrito()
        st.markdown(f"""
        <div class="floating-order-bar">
          <div class="floating-info">🛍️ Tienes <b>{n_items}</b> producto(s) en tu selección</div>
          <div class="floating-total">Total: ${tot:,}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("👉 Ver Carrito y Registrar Venta", key="ir_a_cobrar", type="primary", use_container_width=True):
            st.session_state.pagina = "carrito"
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA 2: CARRITO Y COBRO
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.pagina == "carrito":
    st.markdown('<div class="section-heading">Tu Pedido Actual</div>', unsafe_allow_html=True)

    if not st.session_state.carrito:
        st.markdown("""
        <div class="cart-card-panel" style="text-align:center;padding:3.5rem 1rem;">
          <div style="font-size:4.5rem;margin-bottom:0.8rem;">🛒</div>
          <div style="font-size:1.4rem;font-weight:800;color:#2D252C;">Tu carrito está esperando helados deliciosos</div>
          <div style="color:#8E7A8A;font-size:0.95rem;margin-top:0.3rem;">Ve al menú y agrega los sabores que más te gusten</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("← Explorar Sabores en el Menú", key="volver_tienda_empty"):
            st.session_state.pagina = "tienda"
            st.rerun()
    else:
        col_lista, col_resumen = st.columns([1.6, 1], gap="large")

        with col_lista:
            st.markdown('<div class="cart-card-panel">', unsafe_allow_html=True)
            st.markdown("<div style='font-size:1.15rem;font-weight:800;margin-bottom:0.8rem;color:#2D252C;'>Sabores Seleccionados</div>", unsafe_allow_html=True)
            
            borrar = []
            for nom, cantidad in list(st.session_state.carrito.items()):
                prod = next(p for p in PRODUCTOS if p["nombre"] == nom)
                subtot = prod["precio"] * cantidad

                st.markdown(f"""
                <div class="cart-row-item">
                  <div style="font-size:2.4rem;">{prod['emoji']}</div>
                  <div style="flex:1;">
                    <div class="cart-item-title">{nom}</div>
                    <div class="cart-item-sub">${prod['precio']:,} cada uno</div>
                  </div>
                  <div class="cart-item-price">${subtot:,}</div>
                </div>
                """, unsafe_allow_html=True)

                col_m, col_val, col_p = st.columns([1, 1.5, 1])
                with col_m:
                    if st.button("➖", key=f"cart_m_{nom}", use_container_width=True):
                        if cantidad > 1:
                            st.session_state.carrito[nom] -= 1
                        else:
                            borrar.append(nom)
                        st.rerun()
                with col_val:
                    st.markdown(f"<div style='text-align:center;font-weight:900;font-size:1.1rem;padding-top:0.4rem;color:#FF3377;'>{cantidad} unid.</div>", unsafe_allow_html=True)
                with col_p:
                    if st.button("➕", key=f"cart_p_{nom}", use_container_width=True):
                        st.session_state.carrito[nom] += 1
                        st.rerun()

            for b in borrar:
                if b in st.session_state.carrito:
                    del st.session_state.carrito[b]

            st.markdown("<hr style='border-color:#FFE4EE;'>", unsafe_allow_html=True)
            if st.button("🗑️ Vaciar Todo el Pedido", key="vaciar_cart"):
                st.session_state.carrito = {}
                st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

        with col_resumen:
            st.markdown('<div class="cart-card-panel">', unsafe_allow_html=True)
            st.markdown("<div style='font-size:1.2rem;font-weight:900;color:#2D252C;margin-bottom:1rem;'>Resumen de Pago</div>", unsafe_allow_html=True)

            tot = total_carrito()
            for nom, cantidad in st.session_state.carrito.items():
                p_item = next(p for p in PRODUCTOS if p["nombre"] == nom)
                st.markdown(f"<div style='display:flex;justify-content:space-between;padding:0.35rem 0;color:#6C5B68;font-size:0.92rem;font-weight:600;'><span>{p_item['emoji']} {nom} (x{cantidad})</span><b style='color:#2D252C;'>${p_item['precio']*cantidad:,}</b></div>", unsafe_allow_html=True)

            st.markdown(f"""
            <hr style='border-color:#FFB7CE;margin:1rem 0;'>
            <div style='display:flex;justify-content:space-between;align-items:center;'>
              <span style='font-size:1.2rem;font-weight:800;color:#2D252C;'>Total a Cobrar:</span>
              <span style='font-size:2rem;font-weight:900;color:#FF2E74;'>${tot:,}</span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<div style='font-size:0.9rem;font-weight:800;color:#8E7A8A;margin-bottom:0.4rem;'>CONDICIONES DEL DÍA (PARA ANÁLISIS)</div>", unsafe_allow_html=True)
            clima_cobro = st.selectbox("Clima del Momento", ["Soleado", "Caluroso", "Parcialmente Nublado", "Nublado", "Lluvioso"], key="sel_clima_cobro")
            
            c_cobro1, c_cobro2 = st.columns(2)
            with c_cobro1:
                temp_cobro = st.number_input("Temperatura (°C)", value=26.0, step=0.5, key="num_temp_cobro")
            with c_cobro2:
                hora_actual_sistema = datetime.now().hour
                hora_val = min(22, max(10, hora_actual_sistema))
                hora_cobro = st.slider("Hora de Venta", min_value=10, max_value=22, value=hora_val, format="%d:00", key="slider_hora_cobro")

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🎉 CONFIRMAR VENTA Y REGISTRAR", key="confirmar_venta_btn", type="primary", use_container_width=True):
                dia_str = DIAS_ES[date.today().weekday()]
                fecha_str = date.today().isoformat()
                for nom, cantidad in st.session_state.carrito.items():
                    prod = next(p for p in PRODUCTOS if p["nombre"] == nom)
                    insertar_venta(fecha_str, dia_str, clima_cobro, temp_cobro, nom, cantidad, prod["precio"], hora=hora_cobro)
                st.session_state.carrito = {}
                st.success("✅ ¡Venta registrada exitosamente en la base de datos!")
                st.balloons()
                st.rerun()

            if st.button("← Agregar más productos", key="seguir_comprando", use_container_width=True):
                st.session_state.pagina = "tienda"
                st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA 3: HISTORIAL DE VENTAS
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.pagina == "historial":
    st.markdown('<div class="section-heading">Historial de Ventas de la Heladería</div>', unsafe_allow_html=True)

    f_col1, f_col2 = st.columns(2)
    with f_col1:
        f_desde = st.date_input("Fecha Inicial", value=date.today() - timedelta(days=30))
    with f_col2:
        f_hasta = st.date_input("Fecha Final", value=date.today())

    registros = obtener_ventas(f_desde.isoformat(), f_hasta.isoformat())
    df = pd.DataFrame(registros) if registros else pd.DataFrame()

    if df.empty:
        st.info("No hay ventas registradas en el rango de fechas seleccionado.")
    else:
        tot_ing = df["ingreso"].sum()
        tot_uni = df["cantidad"].sum()
        num_ventas = len(df)
        prom_venta = df["ingreso"].mean()

        # KPIs en tarjetas blancas con acentos rosados
        st.markdown(f"""
        <div class="kpi-container">
          <div class="kpi-box">
            <div class="kpi-box-icon">💰</div>
            <div class="kpi-box-label">Ingresos Totales</div>
            <div class="kpi-box-val">${tot_ing:,.0f}</div>
          </div>
          <div class="kpi-box">
            <div class="kpi-box-icon">🍦</div>
            <div class="kpi-box-label">Unidades Vendidas</div>
            <div class="kpi-box-val">{tot_uni:,}</div>
          </div>
          <div class="kpi-box">
            <div class="kpi-box-icon">🧾</div>
            <div class="kpi-box-label">Registros Realizados</div>
            <div class="kpi-box-val">{num_ventas:,}</div>
          </div>
          <div class="kpi-box">
            <div class="kpi-box-icon">📈</div>
            <div class="kpi-box-label">Ticket Promedio</div>
            <div class="kpi-box-val">${prom_venta:,.0f}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        col_g1, col_g2 = st.columns(2)
        df_prod = df.groupby("producto").agg(Unidades=("cantidad","sum"), Ingresos=("ingreso","sum")).reset_index().sort_values("Ingresos", ascending=False)

        with col_g1:
            fig_bar = px.bar(
                df_prod.head(8), x="Ingresos", y="producto", orientation="h",
                color="Ingresos",
                color_continuous_scale=["#FFA8C5", "#FF4D8D", "#D60050"],
                text_auto=".2s"
            )
            estilizar_figura(fig_bar, "🏆 Top Sabores Más Vendidos (Ingresos)")
            fig_bar.update_layout(coloraxis_showscale=False)
            fig_bar.update_yaxes(categoryorder="total ascending")
            fig_bar.update_traces(
                textposition="outside",
                textfont=dict(size=13, color="#1E161D", family="Nunito"),
                cliponaxis=False
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_g2:
            fig_pie = px.pie(
                df_prod.head(6), values="Ingresos", names="producto",
                color_discrete_sequence=["#FF2E74", "#FB8500", "#FFB703", "#2EC4B6", "#4CC9F0", "#8338EC"]
            )
            estilizar_figura(fig_pie, "🍰 Distribución de Ventas por Producto", tipo="pie")
            fig_pie.update_traces(
                textposition="inside",
                textinfo="percent+label",
                textfont=dict(size=13, color="#FFFFFF", family="Nunito"),
                insidetextorientation="radial"
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        # Evolución Diaria
        df_dia = df.groupby("fecha")["ingreso"].sum().reset_index()
        df_dia["fecha"] = pd.to_datetime(df_dia["fecha"])
        fig_evol = px.area(
            df_dia, x="fecha", y="ingreso",
            labels={"fecha":"Fecha", "ingreso":"Ingreso ($)"},
            color_discrete_sequence=["#FF2E74"]
        )
        fig_evol.update_traces(
            fillcolor="rgba(255, 46, 116, 0.15)",
            line=dict(width=3.5, color="#FF2E74")
        )
        estilizar_figura(fig_evol, "📈 Evolución Diaria de Ventas")
        fig_evol.update_layout(hovermode="x unified")
        st.plotly_chart(fig_evol, use_container_width=True)

        with st.expander("📄 Ver Tabla Completa de Registros"):
            cols_disponibles = [c for c in ["fecha", "hora", "dia_semana", "clima", "temperatura", "producto", "cantidad", "ingreso"] if c in df.columns]
            df_show = df[cols_disponibles].copy()
            if "hora" in df_show.columns:
                df_show["hora"] = df_show["hora"].apply(lambda h: f"{int(h):02d}:00" if pd.notna(h) else "-")
            nombres_cols = {"fecha":"Fecha", "hora":"Hora", "dia_semana":"Día", "clima":"Clima", "temperatura":"Temp (°C)", "producto":"Producto", "cantidad":"Cant.", "ingreso":"Total ($)"}
            df_show.rename(columns=nombres_cols, inplace=True)
            st.dataframe(df_show, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA 4: ANÁLISIS DE VENTAS SEGÚN EL CLIMA Y DÍAS (EXTRA)
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.pagina == "analisis":
    st.markdown('<div class="section-heading">Impacto del Clima en tus Ventas</div>', unsafe_allow_html=True)
    st.markdown("<p style='color:#7D6C78;font-size:1.05rem;font-weight:600;margin-top:-0.5rem;margin-bottom:1.5rem;'>Descubre cómo influyen el clima, la temperatura ambiental y la hora del día en la preferencia de helados.</p>", unsafe_allow_html=True)

    df = pd.DataFrame(obtener_ventas())

    if df.empty:
        st.info("Aún no hay suficientes ventas registradas para calcular correlaciones climáticas.")
    else:
        tab_c, tab_d, tab_h = st.tabs([
            "🌦️ Análisis por Tipo de Clima", 
            "📅 Análisis por Día de la Semana",
            "⏰ Ventas por Hora y Temperatura"
        ])
        
        CLIMA_MAP = {
            "Soleado": "#FFB703",
            "Caluroso": "#FF2E74",
            "Parcialmente Nublado": "#06D6A0",
            "Nublado": "#118AB2",
            "Lluvioso": "#8E7A8A"
        }

        with tab_c:
            df_clima = df.groupby("clima").agg(
                Ingresos=("ingreso","sum"),
                Unidades=("cantidad","sum"),
                Dias=("fecha","nunique"),
                Temp_Media=("temperatura","mean")
            ).reset_index()
            df_clima["Promedio_Dia"] = (df_clima["Ingresos"] / df_clima["Dias"]).round(0)

            c_best = df_clima.loc[df_clima["Ingresos"].idxmax(), "clima"]
            prom_max = df_clima["Promedio_Dia"].max()

            st.markdown(f"""
            <div style="background:#FFFFFF;border:2px solid #FFE4EE;border-radius:20px;padding:1.2rem 1.6rem;margin-bottom:1.5rem;display:flex;gap:2rem;flex-wrap:wrap;box-shadow:0 6px 18px rgba(255,105,180,0.06);">
              <div><span style="color:#8E7A8A;font-weight:700;font-size:0.85rem;">CLIMA MÁS RENTABLE:</span><br><b style="font-size:1.3rem;color:#FF2E74;">☀️ {c_best}</b></div>
              <div><span style="color:#8E7A8A;font-weight:700;font-size:0.85rem;">VENTA PROMEDIO MÁXIMA/DÍA:</span><br><b style="font-size:1.3rem;color:#1E161D;">${prom_max:,.0f}</b></div>
            </div>
            """, unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                fig_c1 = px.bar(
                    df_clima.sort_values("Ingresos", ascending=False),
                    x="clima", y="Ingresos", color="clima",
                    color_discrete_map=CLIMA_MAP,
                    text_auto=".2s"
                )
                estilizar_figura(fig_c1, "💰 Ingresos Totales por Tipo de Clima")
                fig_c1.update_layout(showlegend=False)
                fig_c1.update_traces(
                    textposition="outside",
                    textfont=dict(size=13, color="#1E161D", family="Nunito"),
                    cliponaxis=False
                )
                st.plotly_chart(fig_c1, use_container_width=True)

            with c2:
                fig_c2 = px.bar(
                    df_clima.sort_values("Promedio_Dia", ascending=False),
                    x="clima", y="Promedio_Dia", color="clima",
                    color_discrete_map=CLIMA_MAP,
                    text_auto=".2s"
                )
                estilizar_figura(fig_c2, "📊 Rendimiento Promedio Diario según Clima")
                fig_c2.update_layout(showlegend=False)
                fig_c2.update_traces(
                    textposition="outside",
                    textfont=dict(size=13, color="#1E161D", family="Nunito"),
                    cliponaxis=False
                )
                st.plotly_chart(fig_c2, use_container_width=True)

            # Relación Temperatura vs Ventas
            fig_scat = px.scatter(
                df, x="temperatura", y="ingreso", color="clima",
                color_discrete_map=CLIMA_MAP, trendline="ols",
                labels={"temperatura":"Temperatura (°C)", "ingreso":"Valor de Venta ($)", "clima":"Clima"}
            )
            fig_scat.update_traces(marker=dict(size=10, opacity=0.85, line=dict(width=1, color="#FFFFFF")))
            estilizar_figura(fig_scat, "🌡️ Temperatura Ambiental vs Ventas Registradas")
            st.plotly_chart(fig_scat, use_container_width=True)

        with tab_d:
            orden_dias = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]
            df["dia_semana"] = pd.Categorical(df["dia_semana"], categories=orden_dias, ordered=True)
            df_dia_agg = df.groupby("dia_semana", observed=True).agg(
                Ingresos=("ingreso","sum"),
                Unidades=("cantidad","sum")
            ).reset_index()

            d1, d2 = st.columns(2)
            with d1:
                fig_d1 = px.bar(
                    df_dia_agg, x="dia_semana", y="Ingresos",
                    color="Ingresos",
                    color_continuous_scale=["#FFA8C5", "#FF4D8D", "#D60050"],
                    text_auto=".2s"
                )
                estilizar_figura(fig_d1, "📅 Ingresos Totales por Día de la Semana")
                fig_d1.update_layout(coloraxis_showscale=False)
                fig_d1.update_traces(
                    textposition="outside",
                    textfont=dict(size=13, color="#1E161D", family="Nunito"),
                    cliponaxis=False
                )
                st.plotly_chart(fig_d1, use_container_width=True)

            with d2:
                fig_rad = go.Figure()
                fig_rad.add_trace(go.Scatterpolar(
                    r=df_dia_agg["Ingresos"].tolist(),
                    theta=df_dia_agg["dia_semana"].tolist(),
                    fill="toself",
                    name="Ingresos",
                    fillcolor="rgba(255, 46, 116, 0.25)",
                    line=dict(color="#FF2E74", width=3)
                ))
                estilizar_figura(fig_rad, "🕸️ Radar de Intensidad de Ventas por Día", tipo="polar")
                fig_rad.update_layout(
                    polar=dict(
                        bgcolor="#FFFFFF",
                        radialaxis=dict(visible=True, color="#1E161D", tickfont=dict(size=11, color="#1E161D", family="Nunito"), gridcolor="#F3E5EC"),
                        angularaxis=dict(color="#1E161D", tickfont=dict(size=13, color="#1E161D", family="Nunito"), gridcolor="#F3E5EC")
                    ),
                    showlegend=False
                )
                st.plotly_chart(fig_rad, use_container_width=True)

            # Cruce de Clima y Día
            df_cruce = df.groupby(["dia_semana", "clima"], observed=True)["ingreso"].sum().reset_index()
            fig_stack = px.bar(
                df_cruce, x="dia_semana", y="ingreso", color="clima",
                barmode="stack",
                color_discrete_map=CLIMA_MAP,
                labels={"dia_semana":"Día", "ingreso":"Ingresos ($)", "clima":"Clima"},
                category_orders={"dia_semana":orden_dias}
            )
            estilizar_figura(fig_stack, "🌦️ × 📅 Cruce: Ventas por Día Desglosadas por Clima")
            st.plotly_chart(fig_stack, use_container_width=True)

        with tab_h:
            # Asegurar columna hora
            if "hora" not in df.columns or df["hora"].isnull().all():
                df["hora"] = 15
            else:
                df["hora"] = pd.to_numeric(df["hora"], errors="coerce").fillna(15).astype(int)

            # ── 1. Métricas / KPIs de Hora y Temperatura ───────────────────────
            df_hora_grp = df.groupby("hora").agg(
                Ingresos=("ingreso", "sum"),
                Unidades=("cantidad", "sum"),
                Temp_Prom=("temperatura", "mean"),
                Tickets=("id", "count")
            ).reset_index().sort_values("hora")

            hora_top_row = df_hora_grp.loc[df_hora_grp["Ingresos"].idxmax()]
            hora_top_num = int(hora_top_row["hora"])
            ingreso_top_hora = hora_top_row["Ingresos"]
            temp_top_hora = hora_top_row["Temp_Prom"]

            # Categorizar temperatura en rangos analíticos
            bins_temp = [0, 20, 25, 30, 60]
            labels_temp = ["❄️ Fresco (<20°C)", "⛅ Templado (20-25°C)", "☀️ Cálido (25-30°C)", "🔥 Muy Caluroso (>30°C)"]
            df["rango_temp"] = pd.cut(df["temperatura"], bins=bins_temp, labels=labels_temp, right=False)

            df_rango_grp = df.groupby("rango_temp", observed=False)["ingreso"].sum()
            rango_top = df_rango_grp.idxmax() if not df_rango_grp.empty else "☀️ Cálido (25-30°C)"
            rango_top_val = df_rango_grp.max() if not df_rango_grp.empty else 0

            # Porcentaje de ventas concentrado en la tarde calurosa (14h a 18h)
            ventas_tarde = df[df["hora"].between(14, 18)]["ingreso"].sum()
            pct_tarde = (ventas_tarde / df["ingreso"].sum() * 100) if df["ingreso"].sum() > 0 else 0

            st.markdown(f"""
            <div style="background:#FFFFFF;border:2px solid #FFE4EE;border-radius:20px;padding:1.3rem 1.6rem;margin-bottom:1.5rem;display:flex;gap:2rem;flex-wrap:wrap;box-shadow:0 6px 18px rgba(255,105,180,0.06);align-items:center;">
              <div>
                <span style="color:#8E7A8A;font-weight:700;font-size:0.82rem;text-transform:uppercase;letter-spacing:0.5px;">Hora Pico de Ventas</span><br>
                <b style="font-size:1.35rem;color:#FF2E74;">⏰ {hora_top_num:02d}:00 hrs</b>
                <span style="color:#6C5B68;font-size:0.85rem;display:block;">${ingreso_top_hora:,.0f} recaudados</span>
              </div>
              <div style="width:1px;background:#FFE4EE;height:45px;"></div>
              <div>
                <span style="color:#8E7A8A;font-weight:700;font-size:0.82rem;text-transform:uppercase;letter-spacing:0.5px;">Temperatura en Pico Solar</span><br>
                <b style="font-size:1.35rem;color:#FF7B00;">🌡️ {temp_top_hora:.1f} °C Promedio</b>
                <span style="color:#6C5B68;font-size:0.85rem;display:block;">Aumento de sed y antojo de helado</span>
              </div>
              <div style="width:1px;background:#FFE4EE;height:45px;"></div>
              <div>
                <span style="color:#8E7A8A;font-weight:700;font-size:0.82rem;text-transform:uppercase;letter-spacing:0.5px;">Rango Térmico Más Rentable</span><br>
                <b style="font-size:1.35rem;color:#2D252C;">{rango_top}</b>
                <span style="color:#6C5B68;font-size:0.85rem;display:block;">${rango_top_val:,.0f} en ingresos</span>
              </div>
              <div style="width:1px;background:#FFE4EE;height:45px;"></div>
              <div>
                <span style="color:#8E7A8A;font-weight:700;font-size:0.82rem;text-transform:uppercase;letter-spacing:0.5px;">Concentración Vespertina (14h-18h)</span><br>
                <b style="font-size:1.35rem;color:#06D6A0;">🍧 {pct_tarde:.1f}% del Total</b>
                <span style="color:#6C5B68;font-size:0.85rem;display:block;">Horas doradas para abastecer personal</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # ── 2. Gráfico 1: Doble Eje (Barras de Ventas + Curva de Temperatura) ──
            fig_dual = go.Figure()

            # Barras de Ingresos por hora
            fig_dual.add_trace(go.Bar(
                x=[f"{int(h):02d}:00" for h in df_hora_grp["hora"]],
                y=df_hora_grp["Ingresos"],
                name="Ventas Totales ($)",
                marker=dict(
                    color=df_hora_grp["Ingresos"],
                    colorscale=[[0, "#FFA3C4"], [0.5, "#FF4081"], [1.0, "#D8005A"]],
                    line=dict(color="#FFFFFF", width=1.5)
                ),
                text=[f"${v:,.0f}" for v in df_hora_grp["Ingresos"]],
                textposition="outside",
                textfont=dict(size=11, color="#1E161D", family="Nunito"),
                cliponaxis=False,
                yaxis="y1"
            ))

            # Línea de Temperatura media
            fig_dual.add_trace(go.Scatter(
                x=[f"{int(h):02d}:00" for h in df_hora_grp["hora"]],
                y=df_hora_grp["Temp_Prom"],
                name="Temperatura Media (°C)",
                mode="lines+markers+text",
                line=dict(color="#FF7B00", width=3.5, shape="spline"),
                marker=dict(size=9, color="#FFB703", line=dict(color="#FFFFFF", width=2)),
                text=[f"{t:.1f}°C" for t in df_hora_grp["Temp_Prom"]],
                textposition="top center",
                textfont=dict(size=12, color="#B34700", family="Nunito"),
                yaxis="y2"
            ))

            fig_dual.update_layout(
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                font=dict(family="Nunito, sans-serif", color="#1E161D", size=13),
                title=dict(
                    text="<b>📈 Relación Directa: Ventas por Hora del Día vs Curva Térmica (°C)</b>",
                    font=dict(size=16, color="#2D252C"),
                    x=0.02, y=0.96
                ),
                margin=dict(l=60, r=60, t=75, b=60),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    font=dict(size=12, color="#1E161D")
                ),
                xaxis=dict(
                    title="Hora del Día",
                    showgrid=False,
                    tickfont=dict(size=12, color="#1E161D")
                ),
                yaxis=dict(
                    title=dict(text="Ingresos por Ventas ($)", font=dict(color="#FF2E74", size=13)),
                    tickfont=dict(color="#1E161D"),
                    showgrid=True,
                    gridcolor="#F3E5EC",
                    side="left"
                ),
                yaxis2=dict(
                    title=dict(text="Temperatura Promedio (°C)", font=dict(color="#FF7B00", size=13)),
                    tickfont=dict(color="#FF7B00"),
                    overlaying="y",
                    side="right",
                    showgrid=False,
                    range=[10, max(df_hora_grp["Temp_Prom"].max() + 6, 40)]
                ),
                hovermode="x unified"
            )
            st.plotly_chart(fig_dual, use_container_width=True)

            # ── 3. Gráficas 2 y 3: Columnas de Mapa de Calor y Dispersión Térmica ─
            h_col1, h_col2 = st.columns(2)

            with h_col1:
                # Matriz para Heatmap: X = hora, Y = rango de temperatura
                df_pivot = df.pivot_table(
                    index="rango_temp", 
                    columns="hora", 
                    values="ingreso", 
                    aggfunc="sum",
                    fill_value=0,
                    observed=False
                )
                
                horas_x = [f"{int(c):02d}:00" for c in df_pivot.columns]
                rangos_y = [str(r) for r in df_pivot.index]
                z_vals = df_pivot.values

                fig_heat = go.Figure(data=go.Heatmap(
                    z=z_vals,
                    x=horas_x,
                    y=rangos_y,
                    colorscale=[
                        [0.0, "#FFF5F8"],
                        [0.2, "#FFC2D4"],
                        [0.5, "#FF4D8D"],
                        [0.8, "#E6005C"],
                        [1.0, "#800033"]
                    ],
                    colorbar=dict(title="Ventas ($)", tickfont=dict(color="#1E161D")),
                    hoverongaps=False,
                    hovertemplate="Hora: %{x}<br>Rango Temp: %{y}<br>Ventas: $%{z:,.0f}<extra></extra>"
                ))
                estilizar_figura(fig_heat, "🔥 Mapa de Calor: Ventas según Hora y Rango de Temperatura")
                fig_heat.update_layout(
                    xaxis=dict(title="Hora del Día", tickfont=dict(size=11, color="#1E161D")),
                    yaxis=dict(title="Rango Térmico", tickfont=dict(size=12, color="#1E161D"))
                )
                st.plotly_chart(fig_heat, use_container_width=True)

            with h_col2:
                # Dispersión con burbujas: Hora vs Temperatura, tamaño = ingreso
                fig_scat_h = px.scatter(
                    df,
                    x="hora",
                    y="temperatura",
                    size="ingreso",
                    color="temperatura",
                    color_continuous_scale=["#06D6A0", "#FFB703", "#FF2E74", "#800033"],
                    hover_data={"producto": True, "cantidad": True, "ingreso": ":$,.0f", "hora": True, "temperatura": ":.1f°C"},
                    labels={"hora": "Hora del Día", "temperatura": "Temperatura Registrada (°C)", "ingreso": "Venta ($)"}
                )
                estilizar_figura(fig_scat_h, "✨ Dispersión: Ventas según Hora del Día y Temperatura")
                fig_scat_h.update_layout(
                    coloraxis_colorbar=dict(title="Temp (°C)", tickfont=dict(color="#1E161D")),
                    xaxis=dict(
                        tickmode="linear",
                        tick0=10,
                        dtick=1,
                        ticktext=[f"{h:02d}:00" for h in range(10, 23)],
                        tickvals=list(range(10, 23))
                    )
                )
                st.plotly_chart(fig_scat_h, use_container_width=True)

            # ── 4. Gráfica 4: Preferencia de Sabores según Nivel Térmico ─────────
            st.markdown("<br>", unsafe_allow_html=True)
            def clasificar_momento(row):
                t = row["temperatura"]
                if t >= 27.0:
                    return "☀️ Calor Intenso (≥27°C)"
                elif 22.0 <= t < 27.0:
                    return "⛅ Clima Agradable (22-26°C)"
                else:
                    return "🌧️ Clima Fresco / Frío (<22°C)"

            df["categoria_climatica"] = df.apply(clasificar_momento, axis=1)
            df_prod_momento = df.groupby(["categoria_climatica", "producto"], observed=True)["cantidad"].sum().reset_index()

            fig_prod_clima = px.bar(
                df_prod_momento,
                x="producto",
                y="cantidad",
                color="categoria_climatica",
                barmode="group",
                color_discrete_map={
                    "☀️ Calor Intenso (≥27°C)": "#FF2E74",
                    "⛅ Clima Agradable (22-26°C)": "#FFB703",
                    "🌧️ Clima Fresco / Frío (<22°C)": "#06D6A0"
                },
                labels={"producto": "Helado / Producto", "cantidad": "Unidades Vendidas", "categoria_climatica": "Nivel Térmico"}
            )
            estilizar_figura(fig_prod_clima, "🍨 Preferencia de Sabores según Nivel Térmico")
            fig_prod_clima.update_layout(
                xaxis_tickangle=-30,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_prod_clima, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA 5: PREDICCIONES SEGÚN EL CLIMA (SIMULADOR INTELIGENTE)
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.pagina == "predicciones":
    st.markdown('<div class="section-heading">🔮 Simulador y Predicciones de Ventas según el Clima</div>', unsafe_allow_html=True)
    st.markdown("<p style='color:#7D6C78;font-size:1.05rem;font-weight:600;margin-top:-0.5rem;margin-bottom:1.5rem;'>Anticípate a la demanda: proyecta tus ingresos, cantidad de helados a preparar y abastecimiento ideal según el pronóstico meteorológico.</p>", unsafe_allow_html=True)

    ventas_raw = obtener_ventas()
    df_hist = pd.DataFrame(ventas_raw) if ventas_raw else pd.DataFrame()

    tab_pred_dia, tab_pred_semana = st.tabs(["🌤️ Simulador Diario (Día a Día)", "📅 Planificador Semanal (7 Días)"])

    # ──────────────────────────────────────────────────────────────────────────
    # TAB 1: SIMULADOR DIARIO
    # ──────────────────────────────────────────────────────────────────────────
    with tab_pred_dia:
        st.markdown("""
        <div style="background:#FFFFFF;border:2px solid #FFE4EE;border-radius:22px;padding:1.4rem 1.8rem;box-shadow:0 6px 20px rgba(255,105,180,0.06);margin-bottom:1.5rem;">
          <div style="font-size:1.15rem;font-weight:900;color:#2D252C;margin-bottom:0.8rem;">⚙️ Configura las Condiciones Previstas</div>
        """, unsafe_allow_html=True)

        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            clima_opciones = ["Caluroso", "Soleado", "Parcialmente Nublado", "Nublado", "Lluvioso"]
            clima_sim = st.selectbox("🌤️ Pronóstico del Clima", clima_opciones, index=0, key="sim_clima")
        with sc2:
            temp_sim = st.slider("🌡️ Temperatura Prevista (°C)", min_value=14.0, max_value=44.0, value=31.0, step=0.5, key="sim_temp")
        with sc3:
            dias_lista = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
            hoy_dia_idx = date.today().weekday()
            dia_sim = st.selectbox("📅 Día de la Semana", dias_lista, index=min(5, hoy_dia_idx), key="sim_dia")

        es_festivo = st.checkbox("🎪 ¿Es día festivo, puente o vacaciones? (+25% demanda estimada)", value=(dia_sim in ["Sábado", "Domingo"]), key="sim_festivo")
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Motor de Predicción Estadístico basado en SQLite ──
        if df_hist.empty:
            ingreso_proy = 1500000.0
            unidades_proy = 180
            df_prods_rec = pd.DataFrame()
        else:
            # Ventas agregadas por fecha
            df_fechas = df_hist.groupby(["fecha", "clima", "dia_semana"]).agg(
                ingreso_dia=("ingreso", "sum"),
                unidades_dia=("cantidad", "sum"),
                temp_dia=("temperatura", "mean")
            ).reset_index()

            # Base por clima
            sub_clima = df_fechas[df_fechas["clima"] == clima_sim]
            if not sub_clima.empty:
                base_ing = sub_clima["ingreso_dia"].mean()
                base_uni = sub_clima["unidades_dia"].mean()
                temp_ref = sub_clima["temp_dia"].mean()
            else:
                base_ing = df_fechas["ingreso_dia"].mean()
                base_uni = df_fechas["unidades_dia"].mean()
                temp_ref = 26.0

            # Factor de día de la semana
            prom_gral = df_fechas["ingreso_dia"].mean()
            sub_dia = df_fechas[df_fechas["dia_semana"] == dia_sim]
            if not sub_dia.empty and prom_gral > 0:
                factor_dia = sub_dia["ingreso_dia"].mean() / prom_gral
            else:
                factor_dia = 1.45 if dia_sim in ["Sábado", "Domingo"] else 0.95

            # Factor de temperatura ambiental (cada 1°C sobre ref = +3.3% demanda)
            diff_temp = temp_sim - temp_ref
            factor_temp = max(0.65, min(1.65, 1.0 + (diff_temp * 0.033)))

            # Factor festivo
            factor_festivo = 1.25 if es_festivo else 1.0

            ingreso_proy = base_ing * factor_dia * factor_temp * factor_festivo
            unidades_proy = int(base_uni * factor_dia * factor_temp * factor_festivo)

            # Desglose de sabores según la afinidad climática histórica
            df_prod_hist = df_hist[df_hist["clima"] == clima_sim].groupby("producto")["cantidad"].sum().reset_index()
            if df_prod_hist.empty:
                df_prod_hist = df_hist.groupby("producto")["cantidad"].sum().reset_index()

            tot_c = df_prod_hist["cantidad"].sum()
            df_prod_hist["porcentaje"] = (df_prod_hist["cantidad"] / max(1, tot_c))
            df_prod_hist["unidades_sugeridas"] = (df_prod_hist["porcentaje"] * unidades_proy).round(0).astype(int)
            df_prods_rec = df_prod_hist.sort_values("unidades_sugeridas", ascending=False)

        # Rango de estimación
        ing_min = ingreso_proy * 0.88
        ing_max = ingreso_proy * 1.14
        ticket_estimado = (ingreso_proy / max(1, int(unidades_proy * 0.38)))

        # Nivel de Demanda - Calibrado dinámicamente según el histórico y la temperatura
        if not df_hist.empty:
            prom_diario_referencia = df_fechas["ingreso_dia"].mean()
        else:
            prom_diario_referencia = 350000.0

        ratio_demanda = ingreso_proy / max(1.0, prom_diario_referencia)

        if ratio_demanda >= 1.20 or (clima_sim == "Caluroso" and temp_sim >= 28.0) or (es_festivo and temp_sim >= 25.0):
            demanda_badge = "🔥 DEMANDA MUY ALTA"
            demanda_color = "#E63946"
            demanda_desc = "Fuerte calor o fin de semana. Reforzar turnos en mostrador y bases de helados."
        elif ratio_demanda >= 0.95 or (clima_sim in ["Soleado", "Caluroso"] and temp_sim >= 24.0):
            demanda_badge = "☀️ DEMANDA ALTA"
            demanda_color = "#FF85A1"
            demanda_desc = "Excelente afluencia de clientes. Buen stock de conos, frutas y copas."
        elif ratio_demanda >= 0.70 or clima_sim in ["Parcialmente Nublado", "Nublado"] or temp_sim >= 20.0:
            demanda_badge = "⛅ DEMANDA MODERADA"
            demanda_color = "#06D6A0"
            demanda_desc = "Venta estable y fluida. Mantener producción y atención regular."
        else:
            demanda_badge = "🌧️ DEMANDA BAJA (Fresco/Lluvia)"
            demanda_color = "#8E7A8A"
            demanda_desc = "Menor afluencia en salón. Impulsar promociones a domicilio, waffles y bebidas calientes."

        # Tarjetas de Resultados
        st.markdown(f"""
        <div class="kpi-container" style="margin-top:1rem;">
          <div class="kpi-box">
            <div class="kpi-box-icon">💰</div>
            <div class="kpi-box-label">Ingresos Proyectados</div>
            <div class="kpi-box-val" style="color:#FF2E74;">${ingreso_proy:,.0f}</div>
            <div style="font-size:0.75rem;color:#8E7A8A;margin-top:3px;font-weight:700;">Rango: ${ing_min:,.0f} - ${ing_max:,.0f}</div>
          </div>
          <div class="kpi-box">
            <div class="kpi-box-icon">🍦</div>
            <div class="kpi-box-label">Helados a Vender</div>
            <div class="kpi-box-val">{unidades_proy:,}</div>
            <div style="font-size:0.75rem;color:#8E7A8A;margin-top:3px;font-weight:700;">Unidades estimadas en total</div>
          </div>
          <div class="kpi-box">
            <div class="kpi-box-icon">🧾</div>
            <div class="kpi-box-label">Ticket Promedio</div>
            <div class="kpi-box-val">${ticket_estimado:,.0f}</div>
            <div style="font-size:0.75rem;color:#8E7A8A;margin-top:3px;font-weight:700;">Por compra estimada</div>
          </div>
          <div class="kpi-box">
            <div class="kpi-box-icon">⚡</div>
            <div class="kpi-box-label">Nivel de Demanda</div>
            <div style="font-size:1.25rem;font-weight:900;color:{demanda_color};margin-top:0.3rem;">{demanda_badge}</div>
            <div style="font-size:0.75rem;color:#6C5B68;margin-top:3px;font-weight:700;">{demanda_desc}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Caja de Consejo Estratégico para el Administrador (Diseño compacto y elegante)
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#FFF5F8 0%,#FFF9EE 100%);border:1.5px solid #FFD4E5;border-radius:14px;padding:0.65rem 1.1rem;margin:0.8rem 0;box-shadow:0 3px 12px rgba(255,105,180,0.05);">
          <div style="display:flex;align-items:center;gap:0.4rem;font-size:0.98rem;font-weight:900;color:#2D252C;">
            <span style="font-size:1.05rem;">💡</span> Recomendación Estratégica para el Día <span style="font-size:0.82rem;font-weight:700;color:#8E7A8A;">({clima_sim} · {temp_sim}°C · {dia_sim})</span>
          </div>
          <div style="color:#5C4B58;font-size:0.86rem;font-weight:600;margin-top:0.25rem;line-height:1.4;">
            {
              "🔥 <b>Estrategia de Choque por Calor:</b> Máxima rotación prevista. Prepara con antelación paletas de fruta, helado de mango, maracuyá y cono mixto. Asegura hielo extra y refuerza el personal en el turno de la tarde."
              if clima_sim in ["Caluroso", "Soleado"] and temp_sim >= 28.0 else
              "🌧️ <b>Estrategia para Día Fresco/Lluvia:</b> Los clientes buscarán confort dulce y servicio a domicilio. Destaca los <b>Waffles con Helado, Sundae Brownie y Malteadas</b>. Publica promociones de combos familiares en redes y apps de delivery."
              if clima_sim in ["Lluvioso", "Nublado"] else
              "⛅ <b>Estrategia de Ventas Equilibrada:</b> Se proyecta una venta fluida y continua. Mantén balance en cremas clásicas (Vainilla, Chocolate, Fresa) y postres para compartir."
            }
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── 1. Proyección de Ventas en el Transcurso de las Horas según la Temperatura (Diseño compacto) ──
        st.markdown(f"""
        <div style="background:#FFFFFF;border:1.5px solid #FFE4EE;border-radius:14px;padding:0.65rem 1.1rem;box-shadow:0 3px 12px rgba(255,105,180,0.04);margin:0.8rem 0 1rem 0;">
          <div style="font-size:0.98rem;font-weight:900;color:#2D252C;display:flex;align-items:center;gap:0.4rem;">
            <span style="font-size:1.05rem;">⏰</span> Proyección Horaria de Ventas y Curva Térmica del Día
          </div>
          <div style="color:#7D6C78;font-size:0.85rem;font-weight:600;margin-top:0.2rem;line-height:1.35;">
            Evolución estimada hora por hora para un <b>{dia_sim} con clima {clima_sim} ({temp_sim:.1f}°C)</b>. Anticipa los momentos cumbre para organizar turnos y abastecimiento.
          </div>
        </div>
        """, unsafe_allow_html=True)

        curva_solar_sim = {
            10: -3.5, 11: -2.0, 12: -0.5,
            13: +1.5, 14: +3.0, 15: +3.5, 16: +2.8, 17: +1.2,
            18: -0.5, 19: -2.0, 20: -3.2, 21: -4.0, 22: -5.0
        }
        
        pesos_base_hora = {
            10: 0.030, 11: 0.040, 12: 0.065,
            13: 0.090, 14: 0.145, 15: 0.165, 16: 0.135, 17: 0.105,
            18: 0.075, 19: 0.055, 20: 0.060, 21: 0.035
        }

        horas_calc = []
        for h, p_base in pesos_base_hora.items():
            t_hora = round(temp_sim + curva_solar_sim.get(h, 0.0), 1)
            # A mayor calor en la hora, mayor afluencia respecto a la base
            boost_termico = 1.0 + max(0.0, (t_hora - 23.0) * 0.04)
            p_ajustado = p_base * boost_termico
            horas_calc.append({
                "hora_num": h,
                "hora_str": f"{h:02d}:00",
                "temp_est": t_hora,
                "peso_crudo": p_ajustado
            })

        suma_pesos = sum(x["peso_crudo"] for x in horas_calc)
        filas_horas = []
        for x in horas_calc:
            pct_h = x["peso_crudo"] / suma_pesos
            ing_h = round(ingreso_proy * pct_h, 0)
            uni_h = max(1, int(round(unidades_proy * pct_h, 0)))
            t_h = x["temp_est"]

            if pct_h >= 0.13:
                nivel = "🔥 Pico Máximo de Calor"
                accion = "Turno completo en barra. Vasos y bases listos."
                prod_estrella = "Paleta Frutal & Malteada"
            elif pct_h >= 0.085:
                nivel = "☀️ Alta Afluencia"
                accion = "Reforzar atención. Alta rotación de conos y copas."
                prod_estrella = "Cono Mixto & Mango"
            elif pct_h >= 0.05:
                nivel = "⛅ Demanda Moderada"
                accion = "Atención fluida y reposición de barquillos."
                prod_estrella = "Sundae Brownie & Fresa"
            else:
                nivel = "❄️ Flujo Inicial / Calma"
                accion = "Apertura o cierre. Limpieza y preparación."
                prod_estrella = "Vainilla & Bebida"

            filas_horas.append({
                "Hora": x["hora_str"],
                "hora_num": x["hora_num"],
                "Temp_Prevista": t_h,
                "Temp (°C)": f"{t_h:.1f}°C",
                "Ingresos_Num": ing_h,
                "Venta Proyectada ($)": f"${ing_h:,.0f}",
                "Helados Est.": uni_h,
                "Demanda": nivel,
                "Producto Sugerido": prod_estrella,
                "Acción Sugerida": accion
            })

        df_proy_h = pd.DataFrame(filas_horas)

        # ── 1. PRIMERO: Gráfica de Curva de Ventas por Horas según la Temperatura del Día ──
        fig_pred_h = go.Figure()

        # Barras de Ingresos Previstos por hora
        fig_pred_h.add_trace(go.Bar(
            x=df_proy_h["Hora"],
            y=df_proy_h["Ingresos_Num"],
            name="Venta Proyectada ($)",
            marker=dict(
                color=df_proy_h["Ingresos_Num"],
                colorscale=[[0, "#FFCCD9"], [0.5, "#FF4D8D"], [1.0, "#D60050"]],
                line=dict(color="#FFFFFF", width=1.5)
            ),
            text=[f"${v:,.0f}" for v in df_proy_h["Ingresos_Num"]],
            textposition="outside",
            textfont=dict(size=11, color="#1E161D", family="Nunito"),
            cliponaxis=False,
            yaxis="y1"
        ))

        # Línea de Temperatura Prevista (°C)
        fig_pred_h.add_trace(go.Scatter(
            x=df_proy_h["Hora"],
            y=df_proy_h["Temp_Prevista"],
            name="Temperatura Prevista (°C)",
            mode="lines+markers+text",
            line=dict(color="#FF7B00", width=3.5, shape="spline"),
            marker=dict(size=9, color="#FFB703", line=dict(color="#FFFFFF", width=2)),
            text=[f"{t:.1f}°C" for t in df_proy_h["Temp_Prevista"]],
            textposition="top center",
            textfont=dict(size=12, color="#B34700", family="Nunito"),
            yaxis="y2"
        ))

        fig_pred_h.update_layout(
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            font=dict(family="Nunito, sans-serif", color="#1E161D", size=13),
            title=dict(
                text=f"<b>📈 Curva de Ventas por Hora según la Temperatura Estimada ({dia_sim} · {clima_sim})</b>",
                font=dict(size=16, color="#2D252C"),
                x=0.02, y=0.96
            ),
            margin=dict(l=60, r=60, t=75, b=60),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(size=12, color="#1E161D")
            ),
            xaxis=dict(
                title="Hora del Día",
                showgrid=False,
                tickfont=dict(size=12, color="#1E161D")
            ),
            yaxis=dict(
                title=dict(text="Venta Proyectada ($)", font=dict(color="#FF2E74", size=13)),
                tickfont=dict(color="#1E161D"),
                showgrid=True,
                gridcolor="#F3E5EC",
                side="left"
            ),
            yaxis2=dict(
                title=dict(text="Temperatura Prevista (°C)", font=dict(color="#FF7B00", size=13)),
                tickfont=dict(color="#FF7B00"),
                overlaying="y",
                side="right",
                showgrid=False,
                range=[10, max(df_proy_h["Temp_Prevista"].max() + 6, 42)]
            ),
            hovermode="x unified"
        )
        st.plotly_chart(fig_pred_h, use_container_width=True)

        # ── 2. Abastecimiento y Stock Sugerido por Producto ──
        if not df_prods_rec.empty:
            st.markdown("<br>", unsafe_allow_html=True)
            col_rec_g, col_rec_t = st.columns([1.6, 1], gap="medium")
            with col_rec_g:
                fig_rec = px.bar(
                    df_prods_rec.head(8), x="unidades_sugeridas", y="producto", orientation="h",
                    title=f"📦 Unidades Sugeridas a Tener Listas ({clima_sim})",
                    color="unidades_sugeridas",
                    color_continuous_scale=["#FFA8C5", "#FF4D8D", "#D60050"],
                    text="unidades_sugeridas",
                    labels={"unidades_sugeridas": "Unidades a Preparar", "producto": ""}
                )
                estilizar_figura(fig_rec, f"📦 Stock Sugerido por Producto ({clima_sim})")
                fig_rec.update_layout(coloraxis_showscale=False)
                fig_rec.update_yaxes(categoryorder="total ascending")
                fig_rec.update_traces(
                    textposition="outside",
                    textfont=dict(size=13, color="#1E161D", family="Nunito"),
                    cliponaxis=False
                )
                st.plotly_chart(fig_rec, use_container_width=True)

            with col_rec_t:
                st.markdown("""
                <div style="background:#FFFFFF;border:2px solid #FFE4EE;border-radius:24px;padding:1.4rem;box-shadow:0 6px 20px rgba(255,105,180,0.06);height:100%;">
                  <div style="font-size:1.1rem;font-weight:900;color:#2D252C;margin-bottom:0.6rem;">📋 Lista de Preparación</div>
                """, unsafe_allow_html=True)

                for _, r in df_prods_rec.head(6).iterrows():
                    st.markdown(f"""
                    <div style="display:flex;justify-content:space-between;align-items:center;padding:0.45rem 0;border-bottom:1px solid #FFF0F5;">
                      <span style="font-weight:700;color:#2D252C;font-size:0.92rem;">🍨 {r['producto']}</span>
                      <b style="color:#FF2E74;font-size:1.05rem;">{int(r['unidades_sugeridas'])} unid.</b>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

        # ── 3. ÚLTIMA: Tabla de Planificación y Ventas por Horas ──
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:1.2rem;font-weight:900;color:#2D252C;margin-top:0.5rem;margin-bottom:0.6rem;'>📋 Tabla de Planificación y Ventas por Horas</div>", unsafe_allow_html=True)
        df_mostrar_h = df_proy_h[["Hora", "Temp (°C)", "Venta Proyectada ($)", "Helados Est.", "Demanda", "Producto Sugerido", "Acción Sugerida"]].copy()
        st.dataframe(df_mostrar_h, use_container_width=True, hide_index=True)

    # ──────────────────────────────────────────────────────────────────────────
    # TAB 2: PLANIFICADOR SEMANAL (PRÓXIMOS 7 DÍAS)
    # ──────────────────────────────────────────────────────────────────────────
    with tab_pred_semana:
        st.markdown("""
        <div style="background:#FFFFFF;border:2px solid #FFE4EE;border-radius:22px;padding:1.4rem 1.8rem;box-shadow:0 6px 20px rgba(255,105,180,0.06);margin-bottom:1.5rem;">
          <div style="font-size:1.15rem;font-weight:900;color:#2D252C;margin-bottom:0.4rem;">📅 Proyección Semanal Meteorológica (Próximos 7 Días)</div>
          <div style="font-size:0.9rem;color:#7D6C78;font-weight:600;">Estimación automática día por día basada en el comportamiento histórico y el clima previsto.</div>
        </div>
        """, unsafe_allow_html=True)

        # Generar los 7 días consecutivos
        dias_nombres_es = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        hoy = date.today()
        proyeccion_semana = []
        
        # Simulación de pronóstico para la semana
        climas_semana_default = ["Soleado", "Caluroso", "Caluroso", "Parcialmente Nublado", "Soleado", "Caluroso", "Soleado"]
        temps_semana_default = [28.0, 32.0, 33.5, 26.0, 29.0, 34.0, 31.5]

        for i in range(7):
            d_fecha = hoy + timedelta(days=i)
            d_nom = dias_nombres_es[d_fecha.weekday()]
            c_dia = climas_semana_default[i % len(climas_semana_default)]
            t_dia = temps_semana_default[i % len(temps_semana_default)]
            es_fin = (d_nom in ["Sábado", "Domingo"])

            # Cálculo de venta proyectada
            c_factor = {"Caluroso": 1.75, "Soleado": 1.45, "Parcialmente Nublado": 1.0, "Nublado": 0.72, "Lluvioso": 0.45}.get(c_dia, 1.0)
            d_factor = 1.48 if es_fin else 1.0
            t_factor = 1.0 + ((t_dia - 25.0) * 0.03)
            
            v_estimada = 1450000.0 * c_factor * d_factor * t_factor
            u_estimadas = int(170 * c_factor * d_factor * t_factor)

            proyeccion_semana.append({
                "fecha": d_fecha.strftime("%d/%m"),
                "fecha_full": d_fecha.isoformat(),
                "dia": d_nom,
                "clima": c_dia,
                "temperatura": t_dia,
                "ingreso_estimado": round(v_estimada, -3),
                "unidades_estimadas": u_estimadas
            })

        df_sem = pd.DataFrame(proyeccion_semana)
        total_semana_ing = df_sem["ingreso_estimado"].sum()
        total_semana_uni = df_sem["unidades_estimadas"].sum()
        dia_pico = df_sem.loc[df_sem["ingreso_estimado"].idxmax()]

        # Tarjetas de Resumen Semanal
        st.markdown(f"""
        <div class="kpi-container">
          <div class="kpi-box">
            <div class="kpi-box-icon">💰</div>
            <div class="kpi-box-label">Ingresos Semanales Estimados</div>
            <div class="kpi-box-val" style="color:#FF2E74;">${total_semana_ing:,.0f}</div>
            <div style="font-size:0.75rem;color:#8E7A8A;margin-top:3px;font-weight:700;">Próximos 7 días en total</div>
          </div>
          <div class="kpi-box">
            <div class="kpi-box-icon">🍦</div>
            <div class="kpi-box-label">Unidades Totales</div>
            <div class="kpi-box-val">{total_semana_uni:,}</div>
            <div style="font-size:0.75rem;color:#8E7A8A;margin-top:3px;font-weight:700;">Helados & postres a servir</div>
          </div>
          <div class="kpi-box">
            <div class="kpi-box-icon">🌟</div>
            <div class="kpi-box-label">Día Pico de Ventas</div>
            <div class="kpi-box-val" style="color:#FF2E74;font-size:1.6rem;">{dia_pico['dia']} ({dia_pico['fecha']})</div>
            <div style="font-size:0.75rem;color:#8E7A8A;margin-top:3px;font-weight:700;">Est. ${dia_pico['ingreso_estimado']:,.0f} ({dia_pico['clima']})</div>
          </div>
          <div class="kpi-box">
            <div class="kpi-box-icon">📦</div>
            <div class="kpi-box-label">Abastecimiento Recomendado</div>
            <div style="font-size:1.3rem;font-weight:900;color:#06D6A0;margin-top:0.3rem;">Stock Completo Listo</div>
            <div style="font-size:0.75rem;color:#6C5B68;margin-top:3px;font-weight:700;">Reforzar pedidos de leche y fruta</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Gráfica de Tendencia Semanal
        fig_sem = px.area(
            df_sem, x="fecha", y="ingreso_estimado",
            title="📈 Proyección de Ingresos Día a Día (Próximos 7 Días)",
            markers=True,
            labels={"fecha": "Día / Fecha", "ingreso_estimado": "Ingreso Proyectado ($)"},
            color_discrete_sequence=["#FF2E74"]
        )
        fig_sem.update_traces(
            fillcolor="rgba(255, 46, 116, 0.14)",
            line=dict(width=3.5, color="#FF2E74"),
            marker=dict(size=9, color="#FF2E74", line=dict(width=2, color="#FFFFFF"))
        )
        estilizar_figura(fig_sem, "📈 Curva de Ingresos Proyectados para la Semana")
        fig_sem.update_layout(hovermode="x unified")
        st.plotly_chart(fig_sem, use_container_width=True)

        # Tabla de Planificación Día a Día
        st.markdown('<div class="section-heading">Detalle Diario de Planificación</div>', unsafe_allow_html=True)
        df_sem_display = df_sem[["fecha", "dia", "clima", "temperatura", "ingreso_estimado", "unidades_estimadas"]].copy()
        df_sem_display.columns = ["Fecha", "Día", "Pronóstico Clima", "Temp (°C)", "Ventas Est. ($)", "Helados Est."]
        st.dataframe(df_sem_display, use_container_width=True, hide_index=True)

