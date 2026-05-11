import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go

# ============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================================
st.set_page_config(
    page_title="Code Earth - Global Temperatures 2025",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================================
# CARREGAMENTO DE DADOS
# ============================================================================
@st.cache_data
def load_data():
    try:
        with open('full_temperature_data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

TEMPERATURE_DATA = load_data()

# ============================================================================
# CSS PERSONALIZADO (ESTILO COVID VISUALIZER)
# ============================================================================
st.markdown("""
<style>
    /* Estilo Geral */
    .stApp {
        background-color: #050505;
        color: white;
    }
    
    /* Remover padding padrão */
    .main > div {
        padding: 0rem;
    }
    
    /* Esconder elementos do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Overlay de Informações (Estilo COVID Visualizer) */
    .info-overlay {
        position: fixed;
        top: 30px;
        left: 30px;
        z-index: 1000;
        background: rgba(10, 20, 35, 0.85);
        backdrop-filter: blur(15px);
        padding: 25px;
        border-radius: 20px;
        border: 1px solid rgba(46, 204, 113, 0.2);
        width: 320px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.5);
    }
    
    .country-header {
        display: flex;
        align-items: center;
        gap: 15px;
        margin-bottom: 15px;
    }
    
    .country-name {
        font-size: 22px;
        font-weight: 800;
        letter-spacing: 1px;
        color: #ffffff;
        text-transform: uppercase;
    }
    
    .city-info {
        font-size: 13px;
        color: #2ecc71;
        margin-bottom: 20px;
        font-weight: 500;
    }
    
    .stat-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
    }
    
    .stat-box {
        display: flex;
        flex-direction: column;
    }
    
    .stat-label {
        font-size: 10px;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 5px;
    }
    
    .stat-value {
        font-size: 24px;
        font-weight: bold;
    }
    
    .max-val { color: #3498db; }
    .min-val { color: #2ecc71; }
    
    .stat-date {
        font-size: 10px;
        color: #555;
        margin-top: 3px;
    }

    /* Título Central */
    .brand-title {
        position: fixed;
        top: 30px;
        width: 100%;
        text-align: center;
        z-index: 999;
        pointer-events: none;
    }
    
    .brand-title h1 {
        font-size: 32px;
        font-weight: 200;
        letter-spacing: 8px;
        color: rgba(255, 255, 255, 0.9);
        margin: 0;
    }
    
    .brand-title p {
        font-size: 11px;
        letter-spacing: 3px;
        color: #2ecc71;
        margin-top: 5px;
        opacity: 0.7;
    }
    
    /* Custom Scrollbar para o Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0a0a0a;
        border-right: 1px solid #1a1a1a;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# INTERFACE
# ============================================================================

# Título da Marca
st.markdown("""
<div class="brand-title">
    <h1>CODE EARTH</h1>
    <p>GLOBAL TEMPERATURE ANALYTICS 2025</p>
</div>
""", unsafe_allow_html=True)

# Sidebar para seleção (Simula a interação do mapa)
with st.sidebar:
    st.markdown("<h2 style='color:#2ecc71; font-size:18px;'>PAÍSES</h2>", unsafe_allow_html=True)
    country_list = sorted(list(TEMPERATURE_DATA.keys()))
    # Default para Brasil se disponível
    default_idx = country_list.index("Brazil") if "Brazil" in country_list else 0
    selected_country = st.selectbox("Selecione para ver detalhes:", options=country_list, index=default_idx)

# Dados do país selecionado
c_data = TEMPERATURE_DATA[selected_country]
flag_code = c_data['iso'].lower()[:2]
flag_url = f"https://flagcdn.com/w80/{flag_code}.png"

# Card de Informações (Overlay)
st.markdown(f"""
<div class="info-overlay">
    <div class="country-header">
        <img src="{flag_url}" width="35" style="border-radius: 4px; box-shadow: 0 2px 10px rgba(0,0,0,0.3);">
        <span class="country-name">{selected_country}</span>
    </div>
    <div class="city-info">Cidade Referência: <b>{c_data['city']}</b></div>
    
    <div class="stat-container">
        <div class="stat-box">
            <span class="stat-label">Máxima</span>
            <span class="stat-value max-val">{c_data['max']}°C</span>
            <span class="stat-date">{c_data['max_date']}</span>
        </div>
        <div class="stat-box">
            <span class="stat-label">Mínima</span>
            <span class="stat-value min-val">{c_data['min']}°C</span>
            <span class="stat-date">{c_data['min_date']}</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# GLOBO 3D (PLOTLY CHOROPLETH)
# ============================================================================

# Criar DataFrame para o Plotly
df_map = pd.DataFrame([
    {"iso": v["iso"], "name": k, "temp": v["max"]} 
    for k, v in TEMPERATURE_DATA.items()
])

# Configuração do Globo
fig = go.Figure(go.Choropleth(
    locations=df_map['iso'],
    z=df_map['temp'],
    text=df_map['name'],
    colorscale=[
        [0, '#0a1a2f'],    # Azul escuro profundo
        [0.5, '#1a5276'],  # Azul médio
        [1, '#2ecc71']     # Verde (como solicitado)
    ],
    showscale=False,
    marker_line_color='rgba(255,255,255,0.15)', # Fronteiras sutis
    marker_line_width=0.5,
    hoverinfo='text',
))

fig.update_geos(
    projection_type="orthographic",
    showcountries=True,
    countrycolor="rgba(255,255,255,0.05)",
    showocean=True,
    oceancolor="#050505",
    showlakes=False,
    showcoastlines=True,
    coastlinecolor="rgba(255,255,255,0.1)",
    bgcolor="#050505",
    projection_rotation=dict(lon=-45, lat=15, roll=0) # Focar inicialmente nas Américas
)

fig.update_layout(
    height=900,
    margin={"r":0,"t":0,"l":0,"b":0},
    paper_bgcolor="#050505",
    plot_bgcolor="#050505",
    dragmode="rotate",
)

# Renderizar o mapa
st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# Instrução no rodapé
st.markdown("""
<div style="position: fixed; bottom: 30px; width: 100%; text-align: center; color: rgba(255,255,255,0.2); font-size: 11px; letter-spacing: 2px; pointer-events: none;">
    CLIQUE E ARRASTE PARA EXPLORAR O GLOBO • USE O MENU LATERAL PARA DETALHES
</div>
""", unsafe_allow_html=True)
