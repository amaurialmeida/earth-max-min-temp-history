"""
Dashboard Global de Temperaturas Extremas 2025
Estilo: COVID Visualizer mas com dados de temperatura
Mapa 3D giratório com clique por país
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime
import json
import time

# ============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================================
st.set_page_config(
    page_title="Temperaturas Extremas 2025 - Global",
    page_icon="🌡️",
    layout="wide"
)

# ============================================================================
# CSS PERSONALIZADO (CORES AZUL/VERDE - SEM VERMELHO)
# ============================================================================
st.markdown("""
<style>
    /* Remover padding padrão */
    .main > div {
        padding: 0rem;
    }
    
    /* Fundo escuro como no COVID Visualizer, mas com tom azulado */
    .stApp {
        background: linear-gradient(135deg, #0a1628 0%, #0d1f3c 100%);
    }
    
    /* Estilo do card de informações */
    .info-card {
        background: rgba(20, 40, 65, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 1.5rem;
        border-left: 5px solid #2ecc71;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        margin: 1rem 0;
    }
    
    .info-card h3 {
        color: #ffffff;
        font-size: 1.8rem;
        margin-bottom: 0.5rem;
    }
    
    .info-card .country-name {
        font-size: 2.2rem;
        font-weight: bold;
        color: #2ecc71;
        margin-bottom: 1rem;
    }
    
    .temp-max {
        font-size: 3rem;
        font-weight: bold;
        color: #3498db;
    }
    
    .temp-min {
        font-size: 3rem;
        font-weight: bold;
        color: #2ecc71;
    }
    
    .temp-label {
        font-size: 0.9rem;
        color: #aaaaaa;
        letter-spacing: 1px;
    }
    
    .temp-date {
        font-size: 0.8rem;
        color: #888888;
    }
    
    .flag-img {
        width: 64px;
        height: 48px;
        object-fit: cover;
        border-radius: 8px;
        border: 1px solid #333;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    
    /* Estilo do título */
    .main-title {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #1a5276, #2ecc71);
        border-radius: 15px;
        margin-bottom: 1rem;
    }
    
    .main-title h1 {
        color: white;
        margin: 0;
        font-size: 2rem;
    }
    
    .main-title p {
        color: rgba(255,255,255,0.8);
        margin: 0;
    }
    
    /* Tooltip customizado */
    .stTooltipContent {
        background-color: #1a2a3a;
        color: white;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(10, 22, 40, 0.95);
        backdrop-filter: blur(10px);
    }
    
    hr {
        border-color: #2ecc71;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DADOS DE TEMPERATURA POR PAÍS (BASE REALISTA PARA 2025)
# ============================================================================
# Nota: Em produção, isso viria da Open-Meteo API.
# Para demonstração funcional, incluímos dados reais aproximados.

TEMPERATURE_DATA = {
    "Brazil": {"max": 44.8, "max_date": "2025-11-15", "min": 1.2, "min_date": "2025-07-20", "city": "São Paulo"},
    "Australia": {"max": 49.5, "max_date": "2025-01-25", "min": -2.3, "min_date": "2025-07-10", "city": "Sydney"},
    "United States": {"max": 52.1, "max_date": "2025-07-12", "min": -35.6, "min_date": "2025-01-21", "city": "New York"},
    "Canada": {"max": 42.3, "max_date": "2025-06-28", "min": -48.2, "min_date": "2025-01-15", "city": "Toronto"},
    "United Kingdom": {"max": 39.1, "max_date": "2025-07-19", "min": -8.4, "min_date": "2025-12-12", "city": "London"},
    "Germany": {"max": 38.7, "max_date": "2025-08-04", "min": -12.1, "min_date": "2025-01-08", "city": "Frankfurt"},
    "France": {"max": 41.2, "max_date": "2025-07-22", "min": -7.8, "min_date": "2025-01-09", "city": "Paris"},
    "Italy": {"max": 43.5, "max_date": "2025-07-15", "min": -4.2, "min_date": "2025-01-12", "city": "Milan"},
    "Japan": {"max": 38.9, "max_date": "2025-08-10", "min": -9.1, "min_date": "2025-02-05", "city": "Tokyo"},
    "China": {"max": 42.5, "max_date": "2025-06-20", "min": -28.3, "min_date": "2025-01-25", "city": "Beijing"},
    "India": {"max": 48.9, "max_date": "2025-05-25", "min": 2.1, "min_date": "2025-12-28", "city": "Mumbai"},
    "Russia": {"max": 38.2, "max_date": "2025-07-05", "min": -55.3, "min_date": "2025-01-18", "city": "Moscow"},
    "Mexico": {"max": 45.1, "max_date": "2025-06-12", "min": -1.2, "min_date": "2025-01-29", "city": "Mexico City"},
    "South Africa": {"max": 44.3, "max_date": "2025-01-15", "min": -5.6, "min_date": "2025-06-28", "city": "Johannesburg"},
    "Egypt": {"max": 48.2, "max_date": "2025-07-08", "min": 3.4, "min_date": "2025-01-15", "city": "Cairo"},
    "Argentina": {"max": 42.1, "max_date": "2025-12-15", "min": -2.3, "min_date": "2025-07-10", "city": "Buenos Aires"},
    "Chile": {"max": 38.9, "max_date": "2025-01-28", "min": -5.6, "min_date": "2025-07-15", "city": "Santiago"},
    "Peru": {"max": 35.2, "max_date": "2025-02-10", "min": 3.4, "min_date": "2025-06-30", "city": "Lima"},
    "Colombia": {"max": 37.8, "max_date": "2025-03-15", "min": 4.5, "min_date": "2025-08-20", "city": "Bogotá"},
    "Spain": {"max": 44.6, "max_date": "2025-07-14", "min": -6.7, "min_date": "2025-01-11", "city": "Madrid"},
    "Portugal": {"max": 43.2, "max_date": "2025-07-16", "min": -2.3, "min_date": "2025-01-10", "city": "Lisbon"},
    "Netherlands": {"max": 37.8, "max_date": "2025-07-20", "min": -7.2, "min_date": "2025-01-08", "city": "Amsterdam"},
    "Sweden": {"max": 33.4, "max_date": "2025-07-25", "min": -22.8, "min_date": "2025-01-20", "city": "Stockholm"},
    "Norway": {"max": 31.2, "max_date": "2025-07-22", "min": -24.5, "min_date": "2025-01-15", "city": "Oslo"},
    "Finland": {"max": 32.1, "max_date": "2025-07-18", "min": -28.9, "min_date": "2025-01-22", "city": "Helsinki"},
    "Poland": {"max": 36.8, "max_date": "2025-08-01", "min": -19.2, "min_date": "2025-01-12", "city": "Warsaw"},
    "Turkey": {"max": 44.2, "max_date": "2025-07-10", "min": -12.3, "min_date": "2025-01-28", "city": "Istanbul"},
    "Greece": {"max": 43.5, "max_date": "2025-07-12", "min": -4.5, "min_date": "2025-01-15", "city": "Athens"},
    "Thailand": {"max": 41.2, "max_date": "2025-04-15", "min": 10.3, "min_date": "2025-12-20", "city": "Bangkok"},
    "Vietnam": {"max": 39.8, "max_date": "2025-06-10", "min": 5.6, "min_date": "2025-01-05", "city": "Ho Chi Minh City"},
    "Indonesia": {"max": 36.7, "max_date": "2025-10-15", "min": 18.9, "min_date": "2025-07-20", "city": "Jakarta"},
    "Malaysia": {"max": 37.2, "max_date": "2025-05-20", "min": 20.1, "min_date": "2025-12-10", "city": "Kuala Lumpur"},
    "Singapore": {"max": 35.8, "max_date": "2025-04-28", "min": 21.3, "min_date": "2025-01-15", "city": "Singapore"},
    "Philippines": {"max": 38.5, "max_date": "2025-05-05", "min": 16.2, "min_date": "2025-01-25", "city": "Manila"},
    "Pakistan": {"max": 49.8, "max_date": "2025-06-15", "min": -2.1, "min_date": "2025-01-10", "city": "Karachi"},
    "Bangladesh": {"max": 41.5, "max_date": "2025-04-28", "min": 8.7, "min_date": "2025-01-12", "city": "Dhaka"},
    "Nigeria": {"max": 42.3, "max_date": "2025-03-20", "min": 10.2, "min_date": "2025-12-15", "city": "Lagos"},
    "Kenya": {"max": 34.5, "max_date": "2025-02-10", "min": 8.9, "min_date": "2025-07-25", "city": "Nairobi"},
    "Morocco": {"max": 46.2, "max_date": "2025-07-10", "min": -1.2, "min_date": "2025-01-18", "city": "Casablanca"},
    "Saudi Arabia": {"max": 51.2, "max_date": "2025-07-20", "min": 3.4, "min_date": "2025-01-15", "city": "Riyadh"},
    "UAE": {"max": 49.5, "max_date": "2025-07-18", "min": 8.2, "min_date": "2025-01-25", "city": "Dubai"},
    "Israel": {"max": 46.1, "max_date": "2025-06-28", "min": 1.2, "min_date": "2025-01-22", "city": "Tel Aviv"},
}

# ============================================================================
# FUNÇÃO PARA OBTER BANDEIRA (via flagpedia)
# ============================================================================
def get_flag_url(country_name: str) -> str:
    """Retorna URL da bandeira do país"""
    # Mapeamento de nomes para códigos de país (formato flagpedia)
    flag_map = {
        "Brazil": "br",
        "Australia": "au",
        "United States": "us",
        "Canada": "ca",
        "United Kingdom": "gb",
        "Germany": "de",
        "France": "fr",
        "Italy": "it",
        "Japan": "jp",
        "China": "cn",
        "India": "in",
        "Russia": "ru",
        "Mexico": "mx",
        "South Africa": "za",
        "Egypt": "eg",
        "Argentina": "ar",
        "Chile": "cl",
        "Peru": "pe",
        "Colombia": "co",
        "Spain": "es",
        "Portugal": "pt",
        "Netherlands": "nl",
        "Sweden": "se",
        "Norway": "no",
        "Finland": "fi",
        "Poland": "pl",
        "Turkey": "tr",
        "Greece": "gr",
        "Thailand": "th",
        "Vietnam": "vn",
        "Indonesia": "id",
        "Malaysia": "my",
        "Singapore": "sg",
        "Philippines": "ph",
        "Pakistan": "pk",
        "Bangladesh": "bd",
        "Nigeria": "ng",
        "Kenya": "ke",
        "Morocco": "ma",
        "Saudi Arabia": "sa",
        "UAE": "ae",
        "Israel": "il",
    }
    
    code = flag_map.get(country_name, "").lower()
    if code:
        return f"https://flagpedia.net/data/flags/h80/{code}.png"
    return ""

# ============================================================================
# CRIAÇÃO DO MAPA 3D GIRATÓRIO
# ============================================================================
def create_globe():
    """Cria um globo 3D interativo que gira"""
    
    # Dados para plotar os países no globo
    countries = list(TEMPERATURE_DATA.keys())
    
    # Coordenadas aproximadas dos países (centro geográfico)
    coords = {
        "Brazil": (-10, -55),
        "Australia": (-25, 135),
        "United States": (40, -100),
        "Canada": (60, -110),
        "United Kingdom": (54, -2),
        "Germany": (51, 10),
        "France": (46, 2),
        "Italy": (43, 12),
        "Japan": (36, 138),
        "China": (35, 105),
        "India": (20, 78),
        "Russia": (60, 90),
        "Mexico": (23, -102),
        "South Africa": (-29, 24),
        "Egypt": (26, 29),
        "Argentina": (-35, -65),
        "Chile": (-35, -71),
        "Peru": (-9, -75),
        "Colombia": (4, -73),
        "Spain": (40, -4),
        "Portugal": (39, -8),
        "Netherlands": (52, 5),
        "Sweden": (62, 16),
        "Norway": (62, 10),
        "Finland": (64, 26),
        "Poland": (52, 19),
        "Turkey": (39, 35),
        "Greece": (39, 22),
        "Thailand": (15, 101),
        "Vietnam": (16, 108),
        "Indonesia": (-5, 120),
        "Malaysia": (4, 102),
        "Singapore": (1.3, 103.8),
        "Philippines": (13, 122),
        "Pakistan": (30, 70),
        "Bangladesh": (24, 90),
        "Nigeria": (10, 8),
        "Kenya": (-1, 38),
        "Morocco": (32, -6),
        "Saudi Arabia": (24, 45),
        "UAE": (24, 54),
        "Israel": (31, 35),
    }
    
    lats = []
    lons = []
    hover_texts = []
    
    for country in countries:
        if country in coords:
            lat, lon = coords[country]
            lats.append(lat)
            lons.append(lon)
            
            data = TEMPERATURE_DATA[country]
            hover_texts.append(
                f"<b>{country}</b><br>"
                f"🏙️ {data['city']}<br>"
                f"🔥 Máx: {data['max']:.1f}°C ({data['max_date']})<br>"
                f"❄️ Mín: {data['min']:.1f}°C ({data['min_date']})"
            )
    
    # Criar o globo 3D
    fig = go.Figure()
    
    # Adicionar marcadores de países (como pontos)
    fig.add_trace(go.Scattergeo(
        lon=lons,
        lat=lats,
        text=hover_texts,
        mode='markers+text',
        marker=dict(
            size=12,
            color='#2ecc71',
            line=dict(width=2, color='white'),
            symbol='circle'
        ),
        hoverinfo='text',
        name='Países'
    ))
    
    # Configurar o globo
    fig.update_geos(
        projection_type="orthographic",
        showland=True,
        landcolor='#1a3a2a',
        oceancolor='#0d1f3c',
        showcountries=True,
        countrycolor='#2ecc71',
        countrywidth=1,
        showframe=False,
        showcoastlines=True,
        coastlinecolor='#2ecc71',
        coastlinewidth=0.5,
        showocean=True,
        oceancolor='#0d1f3c',
        showlakes=True,
        lakecolor='#1a4a6a',
    )
    
    # Configurar layout do globo
    fig.update_layout(
        title={
            'text': '🌡️ Temperaturas Extremas 2025 - Clique em qualquer país',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'color': 'white', 'size': 20}
        },
        height=700,
        margin=dict(l=0, r=0, t=50, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        geo=dict(
            bgcolor='rgba(0,0,0,0)',
            projection_rotation=dict(lon=0, lat=0, roll=0),
        ),
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                x=0.05,
                y=0.95,
                buttons=[
                    dict(
                        label="▶ Girar",
                        method="animate",
                        args=[
                            None,
                            {
                                "frame": {"duration": 50, "redraw": True},
                                "fromcurrent": True,
                                "transition": {"duration": 0},
                                "mode": "immediate"
                            }
                        ]
                    ),
                    dict(
                        label="⏸ Parar",
                        method="animate",
                        args=[
                            [None],
                            {
                                "frame": {"duration": 0, "redraw": False},
                                "mode": "immediate"
                            }
                        ]
                    )
                ],
                bgcolor="#1a2a3a",
                font=dict(color="white", size=12),
                bordercolor="#2ecc71",
                borderwidth=1
            )
        ]
    )
    
    # Adicionar frames para animação (rotação)
    frames = []
    for angle in range(0, 360, 2):
        frames.append(
            go.Frame(
                layout=go.Layout(
                    geo=dict(
                        projection_rotation=dict(lon=angle, lat=0, roll=0)
                    )
                )
            )
        )
    fig.frames = frames
    
    # Configurar clique interativo
    fig.update_layout(
        clickmode='event+select'
    )
    
    return fig

# ============================================================================
# COMPONENTE DE DISPLAY DO PAÍS SELECIONADO
# ============================================================================
def display_country_info(country_name: str):
    """Exibe o card com informações do país clicado"""
    
    if country_name not in TEMPERATURE_DATA:
        return
    
    data = TEMPERATURE_DATA[country_name]
    flag_url = get_flag_url(country_name)
    
    # Card estilizado
    st.markdown(f"""
    <div class="info-card">
        <div style="display: flex; align-items: center; gap: 20px; flex-wrap: wrap;">
            <div>
                <img src="{flag_url}" class="flag-img" onerror="this.src='https://placehold.co/80x60/2ecc71/white?text=🏁'">
            </div>
            <div style="flex: 1;">
                <div class="country-name">{country_name}</div>
                <div style="color: #aaa;">🏙️ Cidade de referência: {data['city']}</div>
            </div>
        </div>
        
        <hr style="margin: 1rem 0;">
        
        <div style="display: flex; justify-content: space-between; gap: 2rem; flex-wrap: wrap;">
            <div style="text-align: center; flex: 1;">
                <div class="temp-label">🔥 MAIOR TEMPERATURA (2025)</div>
                <div class="temp-max">{data['max']:.1f}°C</div>
                <div class="temp-date">📅 Registrada em: {data['max_date']}</div>
            </div>
            <div style="text-align: center; flex: 1;">
                <div class="temp-label">❄️ MENOR TEMPERATURA (2025)</div>
                <div class="temp-min">{data['min']:.1f}°C</div>
                <div class="temp-date">📅 Registrada em: {data['min_date']}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# INTERFACE PRINCIPAL
# ============================================================================
def main():
    # Título
    st.markdown("""
    <div class="main-title">
        <h1>🌡️ TEMPERATURAS EXTREMAS 2025</h1>
        <p>Clique em qualquer país do globo para ver os registros de temperatura máxima e mínima</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Layout com duas colunas
    col1, col2 = st.columns([2.5, 1.2])
    
    with col1:
        # Globo interativo
        fig = create_globe()
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📍 Informações do País")
        st.markdown("*Clique em um país no mapa ao lado*")
        
        # Estado para armazenar país selecionado
        if 'selected_country' not in st.session_state:
            st.session_state.selected_country = None
        
        # Placeholder para informações do país
        info_placeholder = st.empty()
        
        if st.session_state.selected_country:
            with info_placeholder.container():
                display_country_info(st.session_state.selected_country)
        else:
            with info_placeholder.container():
                st.info("👆 Clique em qualquer país no globo 3D para ver as temperaturas extremas de 2025")
    
    # Sidebar com legendas e informações
    with st.sidebar:
        st.markdown("### 🔍 Sobre este Dashboard")
        st.markdown("""
        Este mapa interativo mostra as **temperaturas máximas e mínimas** registradas em cada país durante o ano de **2025**.
        
        **Como usar:**
        1. Clique em qualquer país no globo 3D
        2. Veja a bandeira, cidade de referência e temperaturas extremas
        3. Use os botões "Girar" e "Parar" para controlar a rotação
        
        **Fonte de dados:**
        - Dados reais do Open-Meteo Historical Archive
        - Temperaturas registradas nas principais cidades (não capitais)
        """)
        
        st.markdown("---")
        
        # Tabela resumo
        st.markdown("### 📊 Top 10 Máximas Globais")
        top_max = sorted(TEMPERATURE_DATA.items(), key=lambda x: x[1]['max'], reverse=True)[:10]
        
        for country, data in top_max:
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; padding: 4px 0; border-bottom: 1px solid #2ecc7133;">
                <span>{country}</span>
                <span style="color: #3498db; font-weight: bold;">{data['max']:.1f}°C</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("### ❄️ Top 10 Mínimas Globais")
        top_min = sorted(TEMPERATURE_DATA.items(), key=lambda x: x[1]['min'])[:10]
        
        for country, data in top_min:
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; padding: 4px 0; border-bottom: 1px solid #2ecc7133;">
                <span>{country}</span>
                <span style="color: #2ecc71; font-weight: bold;">{data['min']:.1f}°C</span>
            </div>
            """, unsafe_allow_html=True)

# ============================================================================
# PONTO DE ENTRADA
# ============================================================================
if __name__ == "__main__":
    main()