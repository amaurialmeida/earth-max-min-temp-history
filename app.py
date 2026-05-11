import streamlit as st
import pydeck as pdk
import pycountry
import requests

# Função para buscar bandeira correta
def get_flag_url(country_code):
    return f"https://flagcdn.com/w320/{country_code.lower()}.png"

# Função para buscar temperatura atual via Open-Meteo
def get_current_weather(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    response = requests.get(url).json()
    if "current_weather" in response:
        return response["current_weather"]["temperature"]
    return None

# Função para dados históricos (exemplo NOAA simplificado)
def get_historical_weather(year):
    fake_data = {
        2025: {"max": "35°C em 12/01", "min": "8°C em 23/07"},
        2005: {"max": "34°C em 15/02", "min": "7°C em 19/06"},
        1995: {"max": "33°C em 10/03", "min": "6°C em 25/07"},
        1985: {"max": "32°C em 05/01", "min": "5°C em 30/06"},
        1975: {"max": "31°C em 20/02", "min": "4°C em 18/07"},
        1965: {"max": "30°C em 14/01", "min": "3°C em 22/06"},
        1955: {"max": "29°C em 11/03", "min": "2°C em 27/07"},
        1945: {"max": "28°C em 09/02", "min": "1°C em 15/06"},
        1935: {"max": "27°C em 07/01", "min": "0°C em 21/07"},
    }
    return fake_data.get(year, {"max": "-", "min": "-"})

# Configuração inicial
st.set_page_config(page_title="Earth Max-Min Temp History", layout="wide")
st.title("🌍 Earth Max-Min Temp History")

# Dados de exemplo (pode expandir com mais países/cidades)
cities = {
    "São Paulo": {"lat": -23.55, "lon": -46.63, "country_code": "BR"},
    "New York": {"lat": 40.71, "lon": -74.01, "country_code": "US"},
    "Paris": {"lat": 48.85, "lon": 2.35, "country_code": "FR"},
    "Tokyo": {"lat": 35.68, "lon": 139.69, "country_code": "JP"},
    "Tel Aviv": {"lat": 32.08, "lon": 34.78, "country_code": "IL"},
}

# Renderização do globo giratório com PyDeck
view_state = pdk.ViewState(latitude=0, longitude=0, zoom=0.5, bearing=0, pitch=0)
layer = pdk.Layer(
    "ScatterplotLayer",
    data=[{"lat": info["lat"], "lon": info["lon"], "city": city, "country_code": info["country_code"]}
          for city, info in cities.items()],
    get_position=["lon", "lat"],
    get_color=[200, 30, 0, 160],
    get_radius=500000,
)

deck = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    map_style=None,
)

st.pydeck_chart(deck)

# Seleção de cidade
selected_city = st.selectbox("Selecione uma cidade:", list(cities.keys()))
info = cities[selected_city]
lat, lon, country_code = info["lat"], info["lon"], info["country_code"]

# Temperatura atual
current_temp = get_current_weather(lat, lon)

# Bandeira e nome oficial
country = pycountry.countries.get(alpha_2=country_code)
flag_url = get_flag_url(country_code)

st.image(flag_url, width=100)
st.subheader(f"{selected_city}, {country.name}")
st.write(f"🌡️ Temperatura atual: {current_temp}°C")

# Card lateral com histórico
st.sidebar.markdown("### Histórico de Temperaturas")
anos = [2025, 2005, 1995, 1985, 1975, 1965, 1955, 1945, 1935]
for ano in anos:
    dados = get_historical_weather(ano)
    st.sidebar.write(f"**{ano}** - Máx: {dados['max']} | Mín: {dados['min']}")