# ?? Streamlit Rutas Colectivo

Sistema interactivo para cargar rutas de colectivo y paradas, calcular tiempos entre paradas usando OpenRouteService (ORS), y visualizar todo en un mapa.

## ?? Requisitos

- Python 3.9 o superior
- Git
- API Key de ORS: https://openrouteservice.org/dev/#/signup

## ?? Instalación

```bash
git clone https://github.com/haescalante14/streamlit-rutas-colectivo.git
cd streamlit-rutas-colectivo

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate     # Windows
# source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Configurar API Key ORS
copy .env.sample .env
# Editar .env y pegar tu clave ORS
