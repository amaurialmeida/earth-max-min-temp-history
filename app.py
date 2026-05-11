import streamlit as st
import json

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
        return {"Brazil": {"iso": "BRA", "city": "São Paulo", "max": 35.0, "max_date": "2025-01-01", "min": 15.0, "min_date": "2025-07-01"}}

TEMPERATURE_DATA = load_data()

# ============================================================================
# COMPONENTE HTML/JS CUSTOMIZADO (GLOBO 3D ESTILO COVID VISUALIZER)
# ============================================================================
# Esta abordagem usa a biblioteca Globe.gl para garantir performance e zero flickering.

data_json = json.dumps(TEMPERATURE_DATA)

html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="//unpkg.com/globe.gl"></script>
    <style>
        body {{ margin: 0; background: #050505; overflow: hidden; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
        #globeViz {{ width: 100vw; height: 100vh; }}
        
        /* Overlay de Informações */
        .info-overlay {{
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
            color: white;
            display: none; /* Escondido por padrão */
            pointer-events: none;
        }}
        
        .country-header {{ display: flex; align-items: center; gap: 15px; margin-bottom: 15px; }}
        .country-name {{ font-size: 22px; font-weight: 800; letter-spacing: 1px; text-transform: uppercase; }}
        .city-info {{ font-size: 13px; color: #2ecc71; margin-bottom: 20px; font-weight: 500; }}
        .stat-container {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
        .stat-label {{ font-size: 10px; color: #888; text-transform: uppercase; margin-bottom: 5px; }}
        .stat-value {{ font-size: 24px; font-weight: bold; }}
        .max-val {{ color: #3498db; }}
        .min-val {{ color: #2ecc71; }}
        .stat-date {{ font-size: 10px; color: #555; margin-top: 3px; }}

        .brand-title {{
            position: fixed;
            top: 30px;
            width: 100%;
            text-align: center;
            z-index: 999;
            pointer-events: none;
            color: white;
        }}
        .brand-title h1 {{ font-size: 32px; font-weight: 200; letter-spacing: 8px; margin: 0; opacity: 0.9; }}
        .brand-title p {{ font-size: 11px; letter-spacing: 3px; color: #2ecc71; margin-top: 5px; opacity: 0.7; }}
        
        .footer-hint {{
            position: fixed;
            bottom: 30px;
            width: 100%;
            text-align: center;
            color: rgba(255,255,255,0.2);
            font-size: 11px;
            letter-spacing: 2px;
            pointer-events: none;
        }}
    </style>
</head>
<body>
    <div class="brand-title">
        <h1>CODE EARTH</h1>
        <p>GLOBAL TEMPERATURE ANALYTICS 2025</p>
    </div>

    <div id="infoCard" class="info-overlay">
        <div class="country-header">
            <img id="flagImg" src="" width="35" style="border-radius: 4px;">
            <span id="countryName" class="country-name"></span>
        </div>
        <div class="city-info">Cidade Referência: <b id="cityName"></b></div>
        <div class="stat-container">
            <div>
                <div class="stat-label">Máxima</div>
                <div class="stat-value max-val" id="maxTemp"></div>
                <div class="stat-date" id="maxDate"></div>
            </div>
            <div>
                <div class="stat-label">Mínima</div>
                <div class="stat-value min-val" id="minTemp"></div>
                <div class="stat-date" id="minDate"></div>
            </div>
        </div>
    </div>

    <div id="globeViz"></div>
    
    <div class="footer-hint">CLIQUE EM UM PAÍS PARA VER DETALHES • O GLOBO GIRA AUTOMATICAMENTE</div>

    <script>
        const temperatureData = {data_json};
        
        const world = Globe()
            (document.getElementById('globeViz'))
            .globeImageUrl('//unpkg.com/three-globe/example/img/earth-dark.jpg')
            .bumpImageUrl('//unpkg.com/three-globe/example/img/earth-topology.png')
            .backgroundImageUrl('//unpkg.com/three-globe/example/img/night-sky.png')
            .polygonAltitude(0.01)
            .polygonCapColor(() => 'rgba(26, 82, 118, 0.4)')
            .polygonSideColor(() => 'rgba(0, 0, 0, 0.1)')
            .polygonStrokeColor(() => '#2ecc71')
            .polygonLabel(({{ properties: d }}) => `
                <div style="background: rgba(0,0,0,0.8); padding: 5px; border-radius: 3px; border: 1px solid #2ecc71;">
                    <b>${{d.ADMIN}}</b>
                </div>
            `)
            .onPolygonClick(({{ properties: d }}) => {{
                showCountryInfo(d.ADMIN, d.ISO_A3);
                world.controls().autoRotate = false; // Para de girar ao clicar
                setTimeout(() => {{ world.controls().autoRotate = true; }}, 10000); // Volta a girar após 10s
            }})
            .polygonsTransitionDuration(300);

        // Carregar fronteiras dos países
        fetch('https://raw.githubusercontent.com/vasturiano/globe.gl/master/example/datasets/ne_110m_admin_0_countries.geojson')
            .then(res => res.json())
            .then(countries => {{
                world.polygonsData(countries.features.filter(d => d.properties.ISO_A3 !== 'ATA'));
            }});

        // Configuração de Rotação
        world.controls().autoRotate = true;
        world.controls().autoRotateSpeed = 0.5;
        world.pointOfView({{ lat: 15, lng: -45, altitude: 2.5 }});

        function showCountryInfo(name, iso) {{
            const card = document.getElementById('infoCard');
            const data = temperatureData[name] || Object.values(temperatureData).find(v => v.iso === iso);
            
            if (data) {{
                document.getElementById('countryName').innerText = name;
                document.getElementById('cityName').innerText = data.city;
                document.getElementById('maxTemp').innerText = data.max + '°C';
                document.getElementById('maxDate').innerText = data.max_date;
                document.getElementById('minTemp').innerText = data.min + '°C';
                document.getElementById('minDate').innerText = data.min_date;
                document.getElementById('flagImg').src = `https://flagcdn.com/w80/${{data.iso.toLowerCase().substring(0,2)}}.png`;
                card.style.display = 'block';
            }}
        }}
    </script>
</body>
</html>
"""

# Renderizar o componente HTML ocupando a tela toda
st.components.v1.html(html_code, height=900, scrolling=False)
