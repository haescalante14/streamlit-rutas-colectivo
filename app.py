# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import geopandas as gpd
import openrouteservice
from shapely.geometry import Point, LineString
from streamlit_folium import st_folium
import folium
from dotenv import load_dotenv
import os

load_dotenv()

ORS_API_KEY = os.getenv("ORS_API_KEY")
client = openrouteservice.Client(key=ORS_API_KEY)

st.set_page_config(layout="wide")
st.title("Sistema de Rutas y Paradas - Calculo Sectorizado de Tiempos")

st.sidebar.header("Carga de archivos")

uploaded_csv = st.sidebar.file_uploader("Subi CSV de paradas con columnas: lat, lon, route_order", type=["csv"])
uploaded_geojson = st.sidebar.file_uploader("Subi GeoJSON de ruta (linea)", type=["geojson", "json"])

profile = st.sidebar.selectbox("Perfil ORS para calculo de ruta", ["driving-car", "driving-hgv"])

@st.cache_data
def load_paradas(csv_file):
    df = pd.read_csv(csv_file)
    if not {'lat','lon','route_order'}.issubset(df.columns):
        st.error("El CSV debe tener las columnas lat, lon y route_order")
        return None
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat))
    return gdf

@st.cache_data
def load_ruta(geojson_file):
    gdf = gpd.read_file(geojson_file)
    gdf = gdf[gdf.geometry.type.isin(['LineString','MultiLineString'])]
    if gdf.empty:
        st.error("El GeoJSON debe contener al menos una geometria LineString o MultiLineString")
        return None
    return gdf

if uploaded_csv and uploaded_geojson:
    gdf_paradas = load_paradas(uploaded_csv)
    gdf_ruta = load_ruta(uploaded_geojson)
    if gdf_paradas is not None and gdf_ruta is not None:
        st.success("Archivos cargados correctamente")

        gdf_paradas = gdf_paradas.sort_values("route_order").reset_index(drop=True)

        centro = [gdf_paradas.geometry.y.iloc[0], gdf_paradas.geometry.x.iloc[0]]
        m = folium.Map(location=centro, zoom_start=13)

        folium.GeoJson(gdf_ruta).add_to(m)

        for i, row in gdf_paradas.iterrows():
            folium.Marker(
                location=[row.geometry.y, row.geometry.x],
                popup=f"Parada {row.route_order}",
                tooltip=f"Parada {row.route_order}"
            ).add_to(m)

        st.subheader("Mapa con ruta y paradas")
        st_folium(m, width=700, height=500)

        tiempos = []
        distancias = []

        st.subheader("Tiempos y distancias entre paradas")

        for i in range(len(gdf_paradas)-1):
            start = (gdf_paradas.geometry.x.iloc[i], gdf_paradas.geometry.y.iloc[i])
            end = (gdf_paradas.geometry.x.iloc[i+1], gdf_paradas.geometry.y.iloc[i+1])
            try:
                result = client.directions(
                    coordinates=[start, end],
                    profile=profile,
                    format='geojson'
                )
                duracion = result['features'][0]['properties']['segments'][0]['duration']
                distancia = result['features'][0]['properties']['segments'][0]['distance']
            except Exception as e:
                st.error(f"Error en calculo ORS: {e}")
                duracion = None
                distancia = None

            tiempos.append(duracion)
            distancias.append(distancia)

        df_tiempos = pd.DataFrame({
            'origen': gdf_paradas.route_order[:-1],
            'destino': gdf_paradas.route_order[1:],
            'tiempo_segundos': tiempos,
            'distancia_metros': distancias
        })

        st.dataframe(df_tiempos)

        csv_export = df_tiempos.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Exportar tabla de tiempos a CSV",
            data=csv_export,
            file_name='tiempos_sectorizados.csv',
            mime='text/csv'
        )
else:
    st.info("Subi el CSV de paradas y el GeoJSON de ruta para comenzar.")