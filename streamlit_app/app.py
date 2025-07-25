import streamlit as st
from pymongo import MongoClient
import pandas as pd
import plotly.express as px
import json

st.title("Big Data Project - MongoDB Viewer")

client = MongoClient("mongodb://mongodb:27017/")
db = client.big_data_project

collections = ["worldbank_data", "restcountries_data", "frankfurter_data"]
selected_collection = st.selectbox("Selecciona colección", collections)

data = list(db[selected_collection].find({}, {"_id": 0}))
st.write(f"Documentos encontrados: {len(data)}")
if data:
    df = pd.DataFrame(data)
    st.write(df)

    if selected_collection == "frankfurter_data":
        # Visualización 1: Tasas de cambio
        # Validar la columna 'rates' para asegurar que contiene datos válidos
        df['rates'] = df['rates'].apply(lambda x: json.loads(x) if isinstance(x, str) else x if isinstance(x, dict) else {})

        # Crear una lista con todas las monedas
        all_currencies = []
        for rates in df['rates']:
            all_currencies.extend(rates.keys())
        all_currencies = list(set(all_currencies))

        # Seleccionar la moneda a visualizar
        selected_currency = st.selectbox("Selecciona la moneda", all_currencies)

        # Extraer la tasa de cambio de la moneda seleccionada
        df['selected_rate'] = df['rates'].apply(lambda x: x.get(selected_currency) if isinstance(x, dict) else None)

        # Convertir la columna 'date' a datetime
        df['date'] = pd.to_datetime(df['date'], errors='coerce')

        # Filtrar datos del último mes
        start_date = pd.Timestamp("2025-06-01")
        end_date = pd.Timestamp("2025-07-01")
        df = df[(df['date'] >= start_date) & (df['date'] < end_date)]

        # Agrupar por fecha y calcular la tasa promedio para la moneda seleccionada
        df_grouped = df.groupby('date')['selected_rate'].mean().reset_index()

        # Salida de depuración para verificar los datos agrupados
        st.write(df_grouped)

        # Crear el gráfico de líneas por fecha
        fig_rates = px.line(df_grouped, x='date', y='selected_rate', title=f'Tasa de cambio diaria EUR/{selected_currency}')
        st.plotly_chart(fig_rates)

    elif selected_collection == "worldbank_data":
        # Visualización: Evolución del GDP por país
        latin_american_countries = ["ARG", "BRA", "CHL", "COL", "CRI", "CUB", "ECU", "GTM", "HND", "MEX", "NIC", "PAN", "PRY", "PER", "SLV", "URY", "VEN"]
        selected_country = st.selectbox("Selecciona el país", latin_american_countries)

        # Filtrar datos por el país seleccionado
        df = df[df['country'] == selected_country]

        # Convertir la columna 'date' a datetime
        df['date'] = pd.to_datetime(df['date'], errors='coerce')

        # Crear el gráfico de líneas por fecha
        fig_gdp = px.line(df, x="date", y="value", title=f"Evolución del GDP de {selected_country}")
        st.plotly_chart(fig_gdp)

        # Gráfica de barras agrupadas: Comparación del GDP promedio entre países
        fig_gdp_bar = px.bar(pd.DataFrame(data).groupby("country")["value"].mean().reset_index(), x="country", y="value", title="GDP promedio por país (sin filtrar)")
        st.plotly_chart(fig_gdp_bar)

    elif selected_collection == "restcountries_data":
        # Combinar información de países de restcountries con monedas de frankfurter
        frankfurter_data = list(db["frankfurter_data"].find({}, {"_id": 0}))
        if frankfurter_data:
            df_frankfurter = pd.DataFrame(frankfurter_data)
            df_frankfurter['rates'] = df_frankfurter['rates'].apply(lambda x: json.loads(x) if isinstance(x, str) else x if isinstance(x, dict) else {})

            # Asegurar que los valores en 'rates' sean numéricos
            df_frankfurter['rates'] = df_frankfurter['rates'].apply(lambda x: {k: float(v) if isinstance(v, (int, float)) else None for k, v in x.items()})

            # Agregar columna 'currency' de frankfurter_data a restcountries_data
            df['currency'] = df_frankfurter['currency'] if 'currency' in df_frankfurter.columns else "Unknown"

            # Calcular tasa promedio por región
            df['region'] = df['region'].fillna("Unknown")
            df['population'] = df['population'].fillna(0)

            region_rates = []

            for _, row in df.iterrows():
                region = row['region']
                population = row['population']
                currency = row['currency']
                rates = df_frankfurter[df_frankfurter['currency'] == currency]['rates'].apply(lambda x: sum(x.values()) / len(x) if x else None).mean() if not df_frankfurter.empty else None
                region_rates.append({"region": region, "population": population, "average_rate": rates})

            df_region_rates = pd.DataFrame(region_rates)

            # Crear gráfica de barras
            fig_region_rates = px.bar(df_region_rates, x="region", y="average_rate", title="Tasa promedio de cambio por región")
            st.plotly_chart(fig_region_rates)

            # Crear gráfica de dispersión con información del país en el tooltip
            fig_population_rates = px.scatter(
                df_region_rates,
                x="population",
                y="average_rate",
                title="Relación entre población y tasa promedio de cambio",
                hover_data={"region": True, "population": True, "average_rate": True},
                range_x=[0, 2e8]  # Ajustar el rango de población a un máximo de 200 millones
            )
            st.plotly_chart(fig_population_rates)

        # Validar existencia de columnas necesarias
        if "population" not in df.columns:
            df["population"] = 0  # Crear columna population con valor por defecto
        if "area" not in df.columns:
            df["area"] = 1  # Crear columna area con valor por defecto para evitar división por cero

        # Calcular population_density
        if "population_density" not in df.columns:
            df["population_density"] = df["population"] / df["area"]

        # Depuración: Verificar los datos después del cálculo
        st.write("Datos después del cálculo de population_density:")
        st.write(df["population_density"].head())

        # Gráfica de barras: Densidad poblacional promedio por región
        fig_density_bar = px.bar(df.groupby("region")["population_density"].mean().reset_index(), x="region", y="population_density", title="Densidad poblacional promedio por región")
        st.plotly_chart(fig_density_bar)

        # Gráfica de dispersión: Relación entre población y densidad poblacional
        fig_density_scatter = px.scatter(df, x="population", y="population_density", color="region", title="Relación entre población y densidad poblacional")
        st.plotly_chart(fig_density_scatter)

else:
    st.write("No hay datos en la colección seleccionada.")
