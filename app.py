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
        return {
            "Brazil": {"iso": "BRA", "city": "São Paulo", "max": 35.0, "max_date": "2025-01-01", "min": 15.0, "min_date": "2025-07-01"}
        }

TEMPERATURE_DATA = load_data()

# ============================================================================
# ESTADO DA SESSÃO
# ============================================================================
if 'selected_country' not in st.session_state:
    st.session_state.selected_country = "Brazil"

# ============================================================================
# CSS PERSONALIZADO (ESTILO COVID VISUALIZER)
# ============================================================================
st.markdown("""
<style>
    .stApp {
        background-color: #050505;
        color: white;
    }
    .main > div { padding: 0rem; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .info-overlay {
        position: fixed;
        top: 30px;
        left: 30px;
        z-index: 1000;
        background: rgba(10, 20, 35, 0.85);
        backdrop-filter: blur(15px);
        padding: 25px;
        border-radius: 20px;
        border: 1px solid rgba(46, 204, 113, 0.3);
        width: 320px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.5);
        pointer-events: none;
    }
    
    .country-header { display: flex; align-items: center; gap: 15px; margin-bottom: 15px; }
    .country-name { font-size: 22px; font-weight: 800; letter-spacing: 1px; color: #ffffff; text-transform: uppercase; }
    .city-info { font-size: 13px; color: #2ecc71; margin-bottom: 20px; font-weight: 500; }
    .stat-container { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
    .stat-label { font-size: 10px; color: #888; text-transform: uppercase; margin-bottom: 5px; }
    .stat-value { font-size: 24px; font-weight: bold; }
    .max-val { color: #3498db; }
    .min-val { color: #2ecc71; }
    .stat-date { font-size: 10px; color: #555; margin-top: 3px; }

    .brand-title {
        position: fixed;
        top: 30px;
        width: 100%;
        text-align: center;
        z-index: 999;
        pointer-events: none;
    }
    .brand-title h1 { font-size: 32px; font-weight: 200; letter-spacing: 8px; color: rgba(255, 255, 255, 0.9); margin: 0; }
    .brand-title p { font-size: 11px; letter-spacing: 3px; color: #2ecc71; margin-top: 5px; opacity: 0.7; }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# INTERFACE
# ============================================================================

st.markdown("""
<div class="brand-title">
    <h1>CODE EARTH</h1>
    <p>GLOBAL TEMPERATURE ANALYTICS 2025</p>
</div>
""", unsafe_allow_html=True)

# Dados do país selecionado
c_data = TEMPERATURE_DATA.get(st.session_state.selected_country, TEMPERATURE_DATA["Brazil"])
flag_code = c_data['iso'].lower()[:2]
flag_url = f"https://flagcdn.com/w80/{flag_code}.png"

# Card de Informações
st.markdown(f"""
<div class="info-overlay">
    <div class="country-header">
        <img src="{flag_url}" width="35" style="border-radius: 4px;">
        <span class="country-name">{st.session_state.selected_country}</span>
    </div>
    <div class="city-info">Cidade Referência: <b>{c_data['city']}</b></div>
    <div class="stat-container">
        <div>
            <div class="stat-label">Máxima</div>
            <div class="stat-value max-val">{c_data['max']}°C</div>
            <div class="stat-date">{c_data['max_date']}</div>
        </div>
        <div>
            <div class="stat-label">Mínima</div>
            <div class="stat-value min-val">{c_data['min']}°C</div>
            <div class="stat-date">{c_data['min_date']}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# GLOBO 3D COM ROTAÇÃO AUTOMÁTICA (VIA PLOTLY ANIMATION)
# ============================================================================

df_map = pd.DataFrame([
    {"iso": v["iso"], "name": k, "temp": v["max"]} 
    for k, v in TEMPERATURE_DATA.items()
])

fig = go.Figure(go.Choropleth(
    locations=df_map['iso'],
    z=df_map['temp'],
    text=df_map['name'],
    colorscale=[[0, '#0a1a2f'], [0.5, '#1a5276'], [1, '#2ecc71']],
    showscale=False,
    marker_line_color='rgba(255,255,255,0.15)',
    marker_line_width=0.5,
    hoverinfo='text'
))

# Configuração do Globo
fig.update_geos(
    projection_type="orthographic",
    showcountries=True,
    countrycolor="rgba(255,255,255,0.05)",
    showocean=True,
    oceancolor="#050505",
    showcoastlines=True,
    coastlinecolor="rgba(255,255,255,0.1)",
    bgcolor="#050505",
    projection_rotation=dict(lon=0, lat=15, roll=0)
)

fig.update_layout(
    height=850,
    margin={"r":0,"t":0,"l":0,"b":0},
    paper_bgcolor="#050505",
    plot_bgcolor="#050505",
    clickmode='event+select'
)

# Adicionar animação de rotação nativa do Plotly (sem st.rerun)
# Isso faz o globo girar suavemente no navegador
fig.layout.updatemenus = [
    dict(
        type="buttons",
        showactive=False,
        x=0.1, y=0.1,
        buttons=[
            dict(
                label="Play",
                method="animate",
                args=[None, dict(frame=dict(duration=50, redraw=True), fromcurrent=True, mode="immediate")]
            )
        ]
    )
]

# Criar frames para a rotação (360 graus)
frames = [
    go.Frame(layout=dict(geo_projection_rotation=dict(lon=i, lat=15, roll=0)))
    for i in range(0, 360, 2)
]
fig.frames = frames

# Renderizar o mapa
# O on_select="rerun" permite capturar o clique, mas sem o loop infinito de st.rerun()
event = st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, on_select="rerun", key="globe_map")

# Lógica de Clique
if event and "selection" in event and "points" in event["selection"] and len(event["selection"]["points"]) > 0:
    clicked_country = event["selection"]["points"][0].get("text")
    if clicked_country and clicked_country in TEMPERATURE_DATA:
        st.session_state.selected_country = clicked_country
        st.rerun()

# Instrução no rodapé
st.markdown("""
<div style="position: fixed; bottom: 30px; width: 100%; text-align: center; color: rgba(255,255,255,0.2); font-size: 11px; letter-spacing: 2px; pointer-events: none;">
    CLIQUE EM UM PAÍS PARA VER DETALHES • ARRASTE PARA GIRAR O GLOBO
</div>
""", unsafe_allow_html=True)

# Injetar JavaScript para clicar no botão "Play" automaticamente ao carregar
# Isso inicia a rotação sem intervenção do usuário e sem flickering
st.components.v1.html("""
<script>
    setTimeout(function() {
        var buttons = window.parent.document.querySelectorAll('rect.updatemenu-button-bg');
        if (buttons.length > 0) {
            buttons[0].dispatchEvent(new MouseEvent('click', {bubbles: true}));
            // Esconder o botão Play para manter o visual limpo
            buttons[0].parentElement.style.display = 'none';
        }
    }, 1500);
</script>
""", height=0)
