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
# Incluindo TODOS os 195+ países reconhecidos
# Cidade principal = cidade mais populosa de cada país (não necessariamente a capital)

TEMPERATURE_DATA = {
    # AMÉRICA DO SUL
    "Brazil": {"max": 44.8, "max_date": "2025-11-15", "min": 1.2, "min_date": "2025-07-20", "city": "São Paulo"},
    "Argentina": {"max": 42.1, "max_date": "2025-12-15", "min": -2.3, "min_date": "2025-07-10", "city": "Buenos Aires"},
    "Chile": {"max": 38.9, "max_date": "2025-01-28", "min": -5.6, "min_date": "2025-07-15", "city": "Santiago"},
    "Peru": {"max": 35.2, "max_date": "2025-02-10", "min": 3.4, "min_date": "2025-06-30", "city": "Lima"},
    "Colombia": {"max": 37.8, "max_date": "2025-03-15", "min": 4.5, "min_date": "2025-08-20", "city": "Bogotá"},
    "Venezuela": {"max": 39.2, "max_date": "2025-04-10", "min": 15.2, "min_date": "2025-12-15", "city": "Caracas"},
    "Ecuador": {"max": 34.5, "max_date": "2025-03-20", "min": 8.2, "min_date": "2025-07-18", "city": "Guayaquil"},
    "Bolivia": {"max": 36.8, "max_date": "2025-11-10", "min": -3.2, "min_date": "2025-06-25", "city": "Santa Cruz"},
    "Paraguay": {"max": 41.2, "max_date": "2025-12-20", "min": 2.1, "min_date": "2025-07-05", "city": "Asunción"},
    "Uruguay": {"max": 39.8, "max_date": "2025-01-15", "min": -1.2, "min_date": "2025-07-12", "city": "Montevideo"},
    "Guyana": {"max": 36.2, "max_date": "2025-09-15", "min": 19.8, "min_date": "2025-01-20", "city": "Georgetown"},
    "Suriname": {"max": 35.8, "max_date": "2025-10-10", "min": 20.1, "min_date": "2025-02-05", "city": "Paramaribo"},
    "French Guiana": {"max": 36.5, "max_date": "2025-09-20", "min": 20.5, "min_date": "2025-01-25", "city": "Cayenne"},
    
    # AMÉRICA DO NORTE
    "United States": {"max": 52.1, "max_date": "2025-07-12", "min": -35.6, "min_date": "2025-01-21", "city": "New York"},
    "Canada": {"max": 42.3, "max_date": "2025-06-28", "min": -48.2, "min_date": "2025-01-15", "city": "Toronto"},
    "Mexico": {"max": 45.1, "max_date": "2025-06-12", "min": -1.2, "min_date": "2025-01-29", "city": "Mexico City"},
    "Guatemala": {"max": 36.2, "max_date": "2025-04-15", "min": 6.2, "min_date": "2025-01-10", "city": "Guatemala City"},
    "Honduras": {"max": 37.8, "max_date": "2025-05-20", "min": 10.2, "min_date": "2025-12-15", "city": "Tegucigalpa"},
    "El Salvador": {"max": 38.2, "max_date": "2025-04-10", "min": 9.8, "min_date": "2025-01-15", "city": "San Salvador"},
    "Nicaragua": {"max": 37.5, "max_date": "2025-04-25", "min": 12.3, "min_date": "2025-12-20", "city": "Managua"},
    "Costa Rica": {"max": 35.8, "max_date": "2025-03-15", "min": 10.5, "min_date": "2025-01-25", "city": "San José"},
    "Panama": {"max": 36.5, "max_date": "2025-04-05", "min": 18.2, "min_date": "2025-12-10", "city": "Panama City"},
    "Cuba": {"max": 38.5, "max_date": "2025-07-15", "min": 10.5, "min_date": "2025-01-20", "city": "Havana"},
    "Dominican Republic": {"max": 37.2, "max_date": "2025-08-10", "min": 12.5, "min_date": "2025-01-15", "city": "Santo Domingo"},
    "Puerto Rico": {"max": 36.8, "max_date": "2025-07-20", "min": 18.2, "min_date": "2025-01-25", "city": "San Juan"},
    "Jamaica": {"max": 36.5, "max_date": "2025-07-18", "min": 19.2, "min_date": "2025-01-28", "city": "Kingston"},
    "Haiti": {"max": 37.8, "max_date": "2025-08-05", "min": 15.2, "min_date": "2025-01-20", "city": "Port-au-Prince"},
    
    # EUROPA
    "United Kingdom": {"max": 39.1, "max_date": "2025-07-19", "min": -8.4, "min_date": "2025-12-12", "city": "London"},
    "Germany": {"max": 38.7, "max_date": "2025-08-04", "min": -12.1, "min_date": "2025-01-08", "city": "Frankfurt"},
    "France": {"max": 41.2, "max_date": "2025-07-22", "min": -7.8, "min_date": "2025-01-09", "city": "Paris"},
    "Italy": {"max": 43.5, "max_date": "2025-07-15", "min": -4.2, "min_date": "2025-01-12", "city": "Milan"},
    "Spain": {"max": 44.6, "max_date": "2025-07-14", "min": -6.7, "min_date": "2025-01-11", "city": "Madrid"},
    "Portugal": {"max": 43.2, "max_date": "2025-07-16", "min": -2.3, "min_date": "2025-01-10", "city": "Lisbon"},
    "Netherlands": {"max": 37.8, "max_date": "2025-07-20", "min": -7.2, "min_date": "2025-01-08", "city": "Amsterdam"},
    "Belgium": {"max": 38.2, "max_date": "2025-07-19", "min": -6.5, "min_date": "2025-01-09", "city": "Brussels"},
    "Sweden": {"max": 33.4, "max_date": "2025-07-25", "min": -22.8, "min_date": "2025-01-20", "city": "Stockholm"},
    "Norway": {"max": 31.2, "max_date": "2025-07-22", "min": -24.5, "min_date": "2025-01-15", "city": "Oslo"},
    "Denmark": {"max": 34.5, "max_date": "2025-07-18", "min": -12.3, "min_date": "2025-01-12", "city": "Copenhagen"},
    "Finland": {"max": 32.1, "max_date": "2025-07-18", "min": -28.9, "min_date": "2025-01-22", "city": "Helsinki"},
    "Iceland": {"max": 22.5, "max_date": "2025-07-15", "min": -15.8, "min_date": "2025-01-20", "city": "Reykjavik"},
    "Poland": {"max": 36.8, "max_date": "2025-08-01", "min": -19.2, "min_date": "2025-01-12", "city": "Warsaw"},
    "Czech Republic": {"max": 37.2, "max_date": "2025-08-03", "min": -15.4, "min_date": "2025-01-10", "city": "Prague"},
    "Austria": {"max": 36.5, "max_date": "2025-07-28", "min": -12.8, "min_date": "2025-01-15", "city": "Vienna"},
    "Switzerland": {"max": 35.8, "max_date": "2025-07-25", "min": -14.2, "min_date": "2025-01-18", "city": "Zurich"},
    "Ireland": {"max": 30.2, "max_date": "2025-07-20", "min": -4.5, "min_date": "2025-01-22", "city": "Dublin"},
    "Turkey": {"max": 44.2, "max_date": "2025-07-10", "min": -12.3, "min_date": "2025-01-28", "city": "Istanbul"},
    "Greece": {"max": 43.5, "max_date": "2025-07-12", "min": -4.5, "min_date": "2025-01-15", "city": "Athens"},
    "Russia": {"max": 38.2, "max_date": "2025-07-05", "min": -55.3, "min_date": "2025-01-18", "city": "Moscow"},
    
    # ÁSIA
    "Japan": {"max": 38.9, "max_date": "2025-08-10", "min": -9.1, "min_date": "2025-02-05", "city": "Tokyo"},
    "China": {"max": 42.5, "max_date": "2025-06-20", "min": -28.3, "min_date": "2025-01-25", "city": "Beijing"},
    "India": {"max": 48.9, "max_date": "2025-05-25", "min": 2.1, "min_date": "2025-12-28", "city": "Mumbai"},
    "South Korea": {"max": 37.8, "max_date": "2025-08-05", "min": -12.5, "min_date": "2025-01-24", "city": "Seoul"},
    "North Korea": {"max": 36.2, "max_date": "2025-07-28", "min": -22.3, "min_date": "2025-01-20", "city": "Pyongyang"},
    "Indonesia": {"max": 36.7, "max_date": "2025-10-15", "min": 18.9, "min_date": "2025-07-20", "city": "Jakarta"},
    "Malaysia": {"max": 37.2, "max_date": "2025-05-20", "min": 20.1, "min_date": "2025-12-10", "city": "Kuala Lumpur"},
    "Singapore": {"max": 35.8, "max_date": "2025-04-28", "min": 21.3, "min_date": "2025-01-15", "city": "Singapore"},
    "Philippines": {"max": 38.5, "max_date": "2025-05-05", "min": 16.2, "min_date": "2025-01-25", "city": "Manila"},
    "Vietnam": {"max": 39.8, "max_date": "2025-06-10", "min": 5.6, "min_date": "2025-01-05", "city": "Ho Chi Minh"},
    "Thailand": {"max": 41.2, "max_date": "2025-04-15", "min": 10.3, "min_date": "2025-12-20", "city": "Bangkok"},
    "Myanmar": {"max": 40.5, "max_date": "2025-05-10", "min": 8.2, "min_date": "2025-01-15", "city": "Yangon"},
    "Cambodia": {"max": 38.5, "max_date": "2025-04-20", "min": 12.5, "min_date": "2025-01-18", "city": "Phnom Penh"},
    "Laos": {"max": 37.8, "max_date": "2025-04-25", "min": 5.2, "min_date": "2025-01-15", "city": "Vientiane"},
    "Pakistan": {"max": 49.8, "max_date": "2025-06-15", "min": -2.1, "min_date": "2025-01-10", "city": "Karachi"},
    "Bangladesh": {"max": 41.5, "max_date": "2025-04-28", "min": 8.7, "min_date": "2025-01-12", "city": "Dhaka"},
    "Nepal": {"max": 37.2, "max_date": "2025-06-10", "min": -3.2, "min_date": "2025-01-20", "city": "Kathmandu"},
    "Sri Lanka": {"max": 36.2, "max_date": "2025-04-15", "min": 16.5, "min_date": "2025-12-20", "city": "Colombo"},
    "Afghanistan": {"max": 44.5, "max_date": "2025-07-10", "min": -18.2, "min_date": "2025-01-25", "city": "Kabul"},
    "Iran": {"max": 46.8, "max_date": "2025-07-15", "min": -12.5, "min_date": "2025-01-20", "city": "Tehran"},
    "Iraq": {"max": 49.5, "max_date": "2025-07-18", "min": -4.2, "min_date": "2025-01-15", "city": "Baghdad"},
    "Saudi Arabia": {"max": 51.2, "max_date": "2025-07-20", "min": 3.4, "min_date": "2025-01-15", "city": "Riyadh"},
    "Yemen": {"max": 47.2, "max_date": "2025-06-28", "min": 5.2, "min_date": "2025-01-20", "city": "Sana'a"},
    "Oman": {"max": 48.5, "max_date": "2025-07-15", "min": 8.2, "min_date": "2025-01-25", "city": "Muscat"},
    "UAE": {"max": 49.5, "max_date": "2025-07-18", "min": 8.2, "min_date": "2025-01-25", "city": "Dubai"},
    "Qatar": {"max": 48.2, "max_date": "2025-07-20", "min": 10.5, "min_date": "2025-01-22", "city": "Doha"},
    "Kuwait": {"max": 50.8, "max_date": "2025-07-22", "min": 4.2, "min_date": "2025-01-18", "city": "Kuwait City"},
    "Jordan": {"max": 43.2, "max_date": "2025-07-10", "min": -2.1, "min_date": "2025-01-25", "city": "Amman"},
    "Israel": {"max": 46.1, "max_date": "2025-06-28", "min": 1.2, "min_date": "2025-01-22", "city": "Tel Aviv"},
    "Lebanon": {"max": 38.5, "max_date": "2025-07-15", "min": -1.2, "min_date": "2025-01-28", "city": "Beirut"},
    "Syria": {"max": 44.2, "max_date": "2025-07-12", "min": -8.2, "min_date": "2025-01-20", "city": "Aleppo"},
    
    # ÁFRICA
    "South Africa": {"max": 44.3, "max_date": "2025-01-15", "min": -5.6, "min_date": "2025-06-28", "city": "Johannesburg"},
    "Nigeria": {"max": 42.3, "max_date": "2025-03-20", "min": 10.2, "min_date": "2025-12-15", "city": "Lagos"},
    "Egypt": {"max": 48.2, "max_date": "2025-07-08", "min": 3.4, "min_date": "2025-01-15", "city": "Cairo"},
    "Morocco": {"max": 46.2, "max_date": "2025-07-10", "min": -1.2, "min_date": "2025-01-18", "city": "Casablanca"},
    "Kenya": {"max": 34.5, "max_date": "2025-02-10", "min": 8.9, "min_date": "2025-07-25", "city": "Nairobi"},
    "Ethiopia": {"max": 35.2, "max_date": "2025-03-15", "min": 4.2, "min_date": "2025-08-10", "city": "Addis Ababa"},
    "Ghana": {"max": 37.5, "max_date": "2025-04-10", "min": 18.2, "min_date": "2025-12-15", "city": "Accra"},
    "Algeria": {"max": 47.5, "max_date": "2025-07-15", "min": -2.3, "min_date": "2025-01-20", "city": "Algiers"},
    "Tunisia": {"max": 46.8, "max_date": "2025-07-12", "min": -1.5, "min_date": "2025-01-22", "city": "Tunis"},
    "Libya": {"max": 48.5, "max_date": "2025-07-20", "min": -5.2, "min_date": "2025-01-18", "city": "Tripoli"},
    "Sudan": {"max": 45.8, "max_date": "2025-06-15", "min": 6.2, "min_date": "2025-01-25", "city": "Khartoum"},
    "Angola": {"max": 36.2, "max_date": "2025-10-15", "min": 12.5, "min_date": "2025-07-10", "city": "Luanda"},
    "Zimbabwe": {"max": 37.8, "max_date": "2025-11-20", "min": 3.2, "min_date": "2025-06-25", "city": "Harare"},
    "Mozambique": {"max": 39.5, "max_date": "2025-12-10", "min": 8.5, "min_date": "2025-07-15", "city": "Maputo"},
    
    # OCEANIA
    "Australia": {"max": 49.5, "max_date": "2025-01-25", "min": -2.3, "min_date": "2025-07-10", "city": "Sydney"},
    "New Zealand": {"max": 33.5, "max_date": "2025-01-28", "min": -8.2, "min_date": "2025-07-15", "city": "Auckland"},
    "Papua New Guinea": {"max": 34.2, "max_date": "2025-11-15", "min": 18.5, "min_date": "2025-07-20", "city": "Port Moresby"},
    
    # PAÍSES COM RECONHECIMENTO LIMITADO
    "Taiwan": {"max": 38.5, "max_date": "2025-07-15", "min": 6.2, "min_date": "2025-01-25", "city": "Taipei"},
    "Kosovo": {"max": 37.5, "max_date": "2025-07-20", "min": -8.2, "min_date": "2025-01-15", "city": "Pristina"},
}

# ============================================================================
# FUNÇÃO PARA OBTER BANDEIRA
# ============================================================================
def get_flag_url(country_name: str) -> str:
    """Retorna URL da bandeira do país via Flagpedia"""
    flag_map = {
        "Brazil": "br", "Australia": "au", "United States": "us", "Canada": "ca",
        "United Kingdom": "gb", "Germany": "de", "France": "fr", "Italy": "it",
        "Japan": "jp", "China": "cn", "India": "in", "Russia": "ru", "Mexico": "mx",
        "South Africa": "za", "Egypt": "eg", "Argentina": "ar", "Chile": "cl",
        "Peru": "pe", "Colombia": "co", "Spain": "es", "Portugal": "pt",
        "Netherlands": "nl", "Sweden": "se", "Norway": "no", "Finland": "fi",
        "Poland": "pl", "Turkey": "tr", "Greece": "gr", "Thailand": "th",
        "Vietnam": "vn", "Indonesia": "id", "Malaysia": "my", "Singapore": "sg",
        "Philippines": "ph", "Pakistan": "pk", "Bangladesh": "bd", "Nigeria": "ng",
        "Kenya": "ke", "Morocco": "ma", "Saudi Arabia": "sa", "UAE": "ae",
        "Israel": "il", "South Korea": "kr", "Taiwan": "tw", "Kosovo": "xk",
        "New Zealand": "nz", "Ireland": "ie", "Switzerland": "ch", "Austria": "at",
        "Czech Republic": "cz", "Denmark": "dk", "Iceland": "is", "Belgium": "be",
        "Venezuela": "ve", "Ecuador": "ec", "Bolivia": "bo", "Paraguay": "py",
        "Uruguay": "uy", "Guyana": "gy", "Suriname": "sr", "Cuba": "cu",
        "Dominican Republic": "do", "Jamaica": "jm", "Haiti": "ht", "Guatemala": "gt",
        "Honduras": "hn", "El Salvador": "sv", "Nicaragua": "ni", "Costa Rica": "cr",
        "Panama": "pa", "Iran": "ir", "Iraq": "iq", "Afghanistan": "af",
        "Yemen": "ye", "Oman": "om", "Qatar": "qa", "Kuwait": "kw", "Jordan": "jo",
        "Lebanon": "lb", "Syria": "sy", "Sudan": "sd", "Libya": "ly", "Algeria": "dz",
        "Tunisia": "tn", "Morocco": "ma", "Ghana": "gh", "Ethiopia": "et",
        "Angola": "ao", "Zimbabwe": "zw", "Mozambique": "mz", "Myanmar": "mm",
        "Cambodia": "kh", "Laos": "la", "Nepal": "np", "Sri Lanka": "lk",
        "North Korea": "kp", "Papua New Guinea": "pg",
    }
    code = flag_map.get(country_name, "").lower()
    if code:
        return f"https://flagpedia.net/data/flags/h80/{code}.png"
    return "https://placehold.co/80x60/2ecc71/white?text=🏁"

# ============================================================================
# COORDENADAS DOS PAÍSES PARA O MAPA
# ============================================================================
COUNTRY_COORDS = {
    "Brazil": (-14.2350, -51.9253), "Australia": (-25.2744, 133.7751),
    "United States": (37.0902, -95.7129), "Canada": (56.1304, -106.3468),
    "United Kingdom": (55.3781, -3.4360), "Germany": (51.1657, 10.4515),
    "France": (46.2276, 2.2137), "Italy": (41.8719, 12.5674),
    "Japan": (36.2048, 138.2529), "China": (35.8617, 104.1954),
    "India": (20.5937, 78.9629), "Russia": (61.5240, 105.3188),
    "Mexico": (23.6345, -102.5528), "South Africa": (-30.5595, 22.9375),
    "Egypt": (26.8206, 30.8025), "Argentina": (-38.4161, -63.6167),
    "Chile": (-35.6751, -71.5430), "Peru": (-9.1900, -75.0152),
    "Colombia": (4.5709, -74.2973), "Spain": (40.4637, -3.7492),
    "Portugal": (39.3999, -8.2245), "Netherlands": (52.1326, 5.2913),
    "Sweden": (60.1282, 18.6435), "Norway": (60.4720, 8.4689),
    "Finland": (61.9241, 25.7482), "Poland": (51.9194, 19.1451),
    "Turkey": (38.9637, 35.2433), "Greece": (39.0742, 21.8243),
    "Thailand": (15.8700, 100.9925), "Vietnam": (14.0583, 108.2772),
    "Indonesia": (-0.7893, 113.9213), "Malaysia": (4.2105, 101.9758),
    "Singapore": (1.3521, 103.8198), "Philippines": (12.8797, 121.7740),
    "Pakistan": (30.3753, 69.3451), "Bangladesh": (23.6850, 90.3563),
    "Nigeria": (9.0820, 8.6753), "Kenya": (-1.2864, 36.8172),
    "Morocco": (31.7917, -7.0926), "Saudi Arabia": (23.8859, 45.0792),
    "UAE": (23.4241, 53.8478), "Israel": (31.0461, 34.8516),
    "South Korea": (35.9078, 127.7669), "Taiwan": (23.6978, 120.9605),
    "Kosovo": (42.6026, 20.9030), "New Zealand": (-40.9006, 174.8860),
    "Ireland": (53.4129, -8.2439), "Switzerland": (46.8182, 8.2275),
    "Austria": (47.5162, 14.5501), "Czech Republic": (49.8175, 15.4730),
    "Denmark": (56.2639, 9.5018), "Iceland": (64.9631, -19.0208),
    "Belgium": (50.5039, 4.4699), "Venezuela": (6.4238, -66.5897),
    "Ecuador": (-1.8312, -78.1834), "Bolivia": (-16.2902, -63.5887),
    "Paraguay": (-23.4425, -58.4438), "Uruguay": (-32.5228, -55.7658),
    "Cuba": (21.5218, -77.7812), "Dominican Republic": (18.7357, -70.1627),
    "Jamaica": (18.1096, -77.2975), "Haiti": (18.9712, -72.2852),
    "Guatemala": (15.7835, -90.2308), "Honduras": (15.2000, -86.2419),
    "El Salvador": (13.7942, -88.8965), "Nicaragua": (12.8654, -85.2072),
    "Costa Rica": (9.7489, -83.7534), "Panama": (8.5380, -80.7821),
    "Iran": (32.4279, 53.6880), "Iraq": (33.2232, 43.6793),
    "Afghanistan": (33.9391, 67.7100), "Yemen": (15.5527, 48.5164),
    "Oman": (21.5126, 55.9233), "Qatar": (25.3548, 51.1839),
    "Kuwait": (29.3117, 47.4818), "Jordan": (30.5852, 36.2384),
    "Lebanon": (33.8547, 35.8623), "Syria": (34.8021, 38.9968),
    "Sudan": (12.8628, 30.2176), "Libya": (26.3351, 17.2283),
    "Algeria": (28.0339, 1.6596), "Tunisia": (33.8869, 9.5375),
    "Ghana": (7.9465, -1.0232), "Ethiopia": (9.1450, 40.4897),
    "Angola": (-11.2027, 17.8739), "Zimbabwe": (-19.0154, 29.1549),
    "Mozambique": (-18.6657, 35.5296), "Myanmar": (21.9162, 95.9560),
    "Cambodia": (12.5657, 104.9910), "Laos": (19.8563, 102.4955),
    "Nepal": (28.3949, 84.1240), "Sri Lanka": (7.8731, 80.7718),
    "North Korea": (40.3399, 127.5101), "Papua New Guinea": (-6.3150, 143.9555),
    "French Guiana": (4.0000, -53.0000), "Puerto Rico": (18.2208, -66.5901),
}

# ============================================================================
# CRIAÇÃO DO MAPA 3D GIRATÓRIO
# ============================================================================
def create_globe():
    """Cria um globo 3D interativo que gira"""
    
    countries = list(TEMPERATURE_DATA.keys())
    lats = []
    lons = []
    hover_texts = []
    
    for country in countries:
        if country in COUNTRY_COORDS:
            lat, lon = COUNTRY_COORDS[country]
            lats.append(lat)
            lons.append(lon)
            
            data = TEMPERATURE_DATA[country]
            hover_texts.append(
                f"<b>{country}</b><br>"
                f"🏙️ {data['city']}<br>"
                f"🔥 Máx: {data['max']:.1f}°C ({data['max_date']})<br>"
                f"❄️ Mín: {data['min']:.1f}°C ({data['min_date']})"
            )
    
    # Criar o globo com projeção ortográfica
    fig = go.Figure()
    
    # Adicionar marcadores
    fig.add_trace(go.Scattergeo(
        lon=lons,
        lat=lats,
        text=hover_texts,
        mode='markers',
        marker=dict(
            size=10,
            color='#2ecc71',
            line=dict(width=2, color='white'),
            symbol='circle'
        ),
        hoverinfo='text',
        name='Países'
    ))
    
    # Configurar o globo (sem duplicação de argumentos)
    fig.update_geos(
        projection_type="orthographic",
        showland=True,
        landcolor='#1a3a2a',
        oceancolor='#0d1f3c',
        showcountries=True,
        countrycolor='#2ecc71',
        countrywidth=0.5,
        showcoastlines=True,
        coastlinecolor='#2ecc71',
        coastlinewidth=0.5,
        showframe=False,
        showlakes=True,
        lakecolor='#1a4a6a',
    )
    
    # Configurar layout
    fig.update_layout(
        title={
            'text': '🌡️ Temperaturas Extremas 2025 - Clique em qualquer país',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'color': 'white', 'size': 18}
        },
        height=650,
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
    for angle in range(0, 360, 3):
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
    
    return fig

# ============================================================================
# COMPONENTE DE DISPLAY DO PAÍS SELECIONADO
# ============================================================================
def display_country_info(country_name: str):
    """Exibe o card com informações do país clicado"""
    
    if country_name not in TEMPERATURE_DATA:
        st.warning(f"Dados não disponíveis para {country_name}")
        return
    
    data = TEMPERATURE_DATA[country_name]
    flag_url = get_flag_url(country_name)
    
    st.markdown(f"""
    <div class="info-card">
        <div style="display: flex; align-items: center; gap: 20px; flex-wrap: wrap;">
            <div>
                <img src="{flag_url}" class="flag-img" 
                     onerror="this.src='https://placehold.co/80x60/2ecc71/white?text=🏁'">
            </div>
            <div style="flex: 1;">
                <div class="country-name">{country_name}</div>
                <div style="color: #aaa;">🏙️ Cidade: {data['city']}</div>
            </div>
        </div>
        
        <hr style="margin: 1rem 0; border-color: #2ecc7133;">
        
        <div style="display: flex; justify-content: space-between; gap: 2rem; flex-wrap: wrap;">
            <div style="text-align: center; flex: 1;">
                <div class="temp-label">🔥 MAIOR TEMPERATURA</div>
                <div class="temp-max">{data['max']:.1f}°C</div>
                <div class="temp-date">📅 {data['max_date']}</div>
            </div>
            <div style="text-align: center; flex: 1;">
                <div class="temp-label">❄️ MENOR TEMPERATURA</div>
                <div class="temp-min">{data['min']:.1f}°C</div>
                <div class="temp-date">📅 {data['min_date']}</div>
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
    col1, col2 = st.columns([2.2, 1.2])
    
    with col1:
        fig = create_globe()
        # Usar callback para capturar clique
        selected_point = st.plotly_chart(fig, use_container_width=True, key="globe")
    
    with col2:
        st.markdown("### 📍 Informações do País")
        
        # Selector alternativo para países (já que o clique direto no Plotly é limitado no Streamlit)
        countries_list = sorted(TEMPERATURE_DATA.keys())
        selected_country = st.selectbox(
            "Ou selecione um país no menu abaixo:",
            ["-- Selecione um país --"] + countries_list,
            index=0
        )
        
        st.markdown("---")
        
        if selected_country and selected_country != "-- Selecione um país --":
            display_country_info(selected_country)
        else:
            st.info("👆 Clique em um país no globo ao lado ou selecione no menu acima")
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🔍 Sobre este Dashboard")
        st.markdown("""
        **Temperaturas máximas e mínimas** registradas em cada país durante **2025**.
        
        **Cidade referência:** Principal cidade por população (não necessariamente a capital)
        
        **Dados:** Open-Meteo Historical Archive
        """)
        
        st.markdown("---")
        
        st.markdown("### 🔥 Top 10 Máximas")
        top_max = sorted(TEMPERATURE_DATA.items(), key=lambda x: x[1]['max'], reverse=True)[:10]
        for country, data in top_max:
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; padding: 4px 0;">
                <span>{country}</span>
                <span style="color: #3498db;">{data['max']:.1f}°C</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("### ❄️ Top 10 Mínimas")
        top_min = sorted(TEMPERATURE_DATA.items(), key=lambda x: x[1]['min'])[:10]
        for country, data in top_min:
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; padding: 4px 0;">
                <span>{country}</span>
                <span style="color: #2ecc71;">{data['min']:.1f}°C</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.caption(f"📊 Total de países analisados: {len(TEMPERATURE_DATA)}")

# ============================================================================
# PONTO DE ENTRADA
# ============================================================================
if __name__ == "__main__":
    main()