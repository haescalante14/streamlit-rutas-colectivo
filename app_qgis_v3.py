
import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
from pathlib import Path

# Directorio base
BASE_DIR = Path("C:/Users/HEscalante/Red 2025")
RUTA_PARADAS = BASE_DIR / "Paradas CSV"

st.set_page_config(layout="wide")
st.title("🧭 Visualizador y Editor de Capas - Versión 3 (Subcarpetas habilitadas)")

# Buscar archivos geojson recursivamente
geojson_files = sorted(BASE_DIR.rglob("*.geojson"))
csv_files = sorted(RUTA_PARADAS.glob("*.csv"))

st.sidebar.header("📂 Capas disponibles")
ruta_seleccionada = st.sidebar.selectbox("🗺️ Ruta GeoJSON", geojson_files)
paradas_seleccionadas = st.sidebar.selectbox("🚌 Paradas CSV (puede ser general)", csv_files)
map_height = st.sidebar.slider("📏 Altura del mapa", min_value=400, max_value=900, value=600, step=50)

@st.cache_data
def cargar_geojson(path):
    return gpd.read_file(path)

@st.cache_data
def cargar_paradas(path):
    df = pd.read_csv(path, encoding='latin1')
    if "stop_lat" in df.columns and "stop_lon" in df.columns:
        df["route_control"] = df.get("route_control", False)
        return df
    else:
        st.error("⚠️ El archivo no tiene columnas 'stop_lat' y 'stop_lon'")
        return None

if ruta_seleccionada and paradas_seleccionadas:
    gdf_ruta = cargar_geojson(ruta_seleccionada)
    df_paradas = cargar_paradas(paradas_seleccionadas)

    if df_paradas is not None and not df_paradas.empty:
        if "linea" in df_paradas.columns:
            linea_sel = st.sidebar.selectbox("🚌 Línea a visualizar", sorted(df_paradas["linea"].unique()))
            df_paradas = df_paradas[df_paradas["linea"] == linea_sel]

        df_paradas = df_paradas.sort_values("route_order").reset_index(drop=True)

        st.subheader("✅ Seleccioná las paradas de control (route_control)")
        edited_df = st.data_editor(df_paradas, use_container_width=True, key="edit_paradas", num_rows="dynamic")

        gdf_paradas = gpd.GeoDataFrame(
            edited_df,
            geometry=gpd.points_from_xy(edited_df.stop_lon, edited_df.stop_lat),
            crs="EPSG:4326"
        )

        centro = [gdf_paradas.geometry.y.iloc[0], gdf_paradas.geometry.x.iloc[0]]
        m = folium.Map(location=centro, zoom_start=14)
        folium.GeoJson(gdf_ruta, name="Ruta").add_to(m)

        for _, row in gdf_paradas.iterrows():
            icon = folium.Icon(color="blue", icon="bus", prefix="fa")
            if row.get("route_control", False):
                icon = folium.Icon(color="red", icon="flag", prefix="fa")
            folium.Marker(
                location=[row.geometry.y, row.geometry.x],
                icon=icon,
                popup=f"{row.get('stop_id', 'Parada')}",
                tooltip=f"Orden {row.get('route_order')}"
            ).add_to(m)

        st.subheader("🗺️ Vista del recorrido y paradas")
        st_folium(m, height=map_height)

        st.download_button(
            "💾 Descargar CSV editado",
            edited_df.to_csv(index=False),
            file_name="paradas_editadas.csv"
        )
    else:
        st.warning("⚠️ No se pudieron cargar las paradas.")
else:
    st.info("📌 Seleccioná archivos para visualizar")
