import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de la página
st.set_page_config(
    page_title="Narrativa: Análisis del Mercado de Videojuegos",
    page_icon="🌍",
    layout="wide"
)

# 2. Carga y limpieza de datos
@st.cache_data
def cargar_datos():
    df = pd.read_csv("vgsales.csv")
    # Limpiamos registros sin año y convertimos a entero
    df = df.dropna(subset=['Year'])
    df['Year'] = df['Year'].astype(int)
    # Filtramos años atípicos o incorrectos si los hay (el dataset suele llegar hasta ~2016/2020)
    df = df[df['Year'] <= 2016] 
    return df

df = cargar_datos()

# Título principal de la aplicación (Fuera de las pestañas)
st.title("🌍 Evolución del Mercado Global de Videojuegos")

# Creación de las Pestañas Principales
pestana1, pestana2 = st.tabs(["🌍 1. Descentralización Global", "🇯🇵 2. El Fenómeno RPG en Japón"])

# =========================================================================
# PESTAÑA 1: TU CÓDIGO ACTUAL (FUNCIONANDO)
# =========================================================================
with pestana1:
    st.markdown("""
    ### Narrativa 1: La contracción de los gigantes y el despertar del 'Mercado Gris'
    Históricamente, la industria estuvo monopolizada por Norteamérica, Europa y Japón. Sin embargo, con el paso de los años, 
    el peso relativo de estas regiones empezó a ceder terreno ante el crecimiento acelerado de los mercados emergentes y alternativos (*Other Sales*).
    """)

    st.divider()

    # 4. Control de Tiempo: El Slider (Controla ambos gráficos)
    st.subheader("⏱️ Línea del Tiempo")
    año_seleccionado = st.slider(
        "Arrastra el slider para ver cómo se transforma el mercado año a año:",
        min_value=int(df['Year'].min()),
        max_value=int(df['Year'].max()),
        value=int(df['Year'].min()),
        step=1,
        key="slider_narrativa_1" # Llave única para evitar conflictos
    )

    # 5. Procesamiento de datos para el mapa por año seleccionado
    df_año = df[df['Year'] == año_seleccionado]

    # Agrupamos las ventas totales del año seleccionado
    ventas_regionales = df_año[['NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales']].sum()

    # Diccionario para el mapa
    mapeo_paises = {
        'USA': ('NA_Sales', 'Norteamérica'), 'CAN': ('NA_Sales', 'Norteamérica'), 'MEX': ('NA_Sales', 'Norteamérica'),
        'JPN': ('JP_Sales', 'Japón'),
        'GBR': ('EU_Sales', 'Europa'), 'FRA': ('EU_Sales', 'Europa'), 'DEU': ('EU_Sales', 'Europa'), 
        'ESP': ('EU_Sales', 'Europa'), 'ITA': ('EU_Sales', 'Europa'),
        'BRA': ('Other_Sales', 'Otros Mercados'), 'ARG': ('Other_Sales', 'Otros Mercados'), 
        'COL': ('Other_Sales', 'Otros Mercados'), 'AUS': ('Other_Sales', 'Otros Mercados'), 
        'IND': ('Other_Sales', 'Otros Mercados'), 'ZAF': ('Other_Sales', 'Otros Mercados'),
        'CHN': ('Other_Sales', 'Otros Mercados'), 'KOR': ('Other_Sales', 'Otros Mercados')
    }

    datos_mapa = []
    for iso, (columna_venta, nombre_region) in mapeo_paises.items():
        datos_mapa.append({
            'ISO': iso,
            'Ventas': ventas_regionales[columna_venta],
            'Región': nombre_region
        })
    df_mapa = pd.DataFrame(datos_mapa)

    df_temporal = df.groupby('Year')[['NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales']].sum().reset_index()
    df_temporal_long = df_temporal.melt(
        id_vars=['Year'], 
        value_vars=['NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales'],
        var_name='Region', 
        value_name='Ventas'
    )

    mapeo_nombres = {
        'NA_Sales': 'Norteamérica',
        'EU_Sales': 'Europa',
        'JP_Sales': 'Japón',
        'Other_Sales': 'Otros Mercados (Mercado Gris)'
    }
    df_temporal_long['Region'] = df_temporal_long['Region'].map(mapeo_nombres)

    # Layout: Columnas
    col_mapa, col_barras = st.columns([3, 2])

    with col_mapa:
        st.subheader(f"🗺️ Mapa de Calor Global ({año_seleccionado})")
        fig_mapa = px.choropleth(
            df_mapa, locations="ISO", color="Ventas", hover_name="Región",
            color_continuous_scale=px.colors.sequential.YlOrRd, range_color=[0, 150], projection="natural earth"
        )
        fig_mapa.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, coloraxis_colorbar=dict(title="Ventas (M)"))
        st.plotly_chart(fig_mapa, use_container_width=True)

    with col_barras:
        st.subheader(f"📊 Participación en Ventas Globales ({año_seleccionado})")
        total_año = ventas_regionales.sum()
        if total_año > 0:
            df_participacion = pd.DataFrame({
                'Región': ['Norteamérica', 'Europa', 'Japón', 'Otros'],
                'Ventas': [ventas_regionales['NA_Sales'], ventas_regionales['EU_Sales'], ventas_regionales['JP_Sales'], ventas_regionales['Other_Sales']]
            })
            df_participacion['Porcentaje'] = (df_participacion['Ventas'] / total_año) * 100
        else:
            df_participacion = pd.DataFrame({'Región': [], 'Ventas': [], 'Porcentaje': []})

        fig_barras = px.bar(
            df_participacion, x='Región', y='Porcentaje', text=df_participacion['Porcentaje'].apply(lambda x: f"{x:.1f}%"),
            color='Región', color_discrete_map={'Norteamérica': '#EF553B', 'Europa': '#636EFA', 'Japón': '#00CC96', 'Otros': '#AB63FA'},
            title=f"Distribución del Mercado en {año_seleccionado}"
        )
        fig_barras.update_layout(yaxis_range=[0, 100])
        st.plotly_chart(fig_barras, use_container_width=True)

    st.markdown("### 💡 Observaciones clave para este año:")
    if año_seleccionado >= 1500:
        if año_seleccionado <= 1995:
            st.info(f"En **{año_seleccionado}**, el mercado está fuertemente polarizado entre **Norteamérica y Japón**. La región de 'Otros' es prácticamente invisible en el mapa.")
        elif 1996 <= año_seleccionado <= 2006:
            st.info(f"En **{año_seleccionado}**, **Europa** empieza a consolidarse como una potencia de consumo masivo, mientras que 'Otros' empieza a registrar sus primeros destellos amarillos en el mapa.")
        else:
            st.info(f"Para **{año_seleccionado}**, se hace evidente la tendencia: la cuota de Japón y NA se enfría proporcionalmente, mientras que la barra de **Otros Mercados** se estabiliza como un pilar fundamental del consumo global.")

    st.divider()
    st.subheader("📈 Línea de Tendencia Histórica: La Caída de los Gigantes")
    fig_lineas = px.line(
        df_temporal_long, x='Year', y='Ventas', color='Region',
        title="Evolución de Ventas Anuales por Región (1980 - 2016)",
        color_discrete_map={'Norteamérica': '#EF553B', 'Europa': '#636EFA', 'Japón': '#00CC96', 'Otros Mercados (Mercado Gris)': '#AB63FA'}
    )
    fig_lineas.add_vline(x=año_seleccionado, line_width=2, line_dash="dash", line_color="gray")
    st.plotly_chart(fig_lineas, use_container_width=True)


# =========================================================================
# PESTAÑA 2: NUEVA NARRATIVA (EL ENFOC CULTURAL DE JAPÓN Y RPGS)
# =========================================================================
with pestana2:
    st.markdown("""
    ### Narrativa 2: El fenómeno cultural de Japón y los RPGs
    A diferencia de Occidente, donde dominan los juegos de Acción o Deportes, Japón posee una identidad única. 
    Aquí verás cómo el género **Role-Playing (RPG)** domina de manera contundente las preferencias del público japonés año tras año.
    """)
    
    st.divider()
    
    st.subheader("⏱️ Filtro Temporal Histórico (Japón)")
    # Creamos un slider independiente para controlar esta pestaña
    año_seleccionado_rpg = st.slider(
        "Selecciona el año para analizar las preferencias culturales:",
        min_value=int(df['Year'].min()),
        max_value=int(df['Year'].max()),
        value=1996, # Año ideal por defecto (Época de oro RPG en JPN)
        step=1,
        key="slider_narrativa_2"
    )
    
    # Procesamiento para Pestaña 2
    df_año_rpg = df[df['Year'] == año_seleccionado_rpg]
    
    # Creamos el diseño de 2 columnas para el mapa RPG y las barras de géneros
    col_mapa_rpg, col_barras_jp = st.columns([3, 2])
    
    with col_mapa_rpg:
        st.subheader(f"🗺️ Consumo Global del Género RPG ({año_seleccionado_rpg})")
        st.caption("Este mapa muestra de manera exclusiva las ventas mundiales de los juegos de Rol (Role-Playing).")
        
        # Filtramos solo datos de juegos RPG para el año seleccionado
        df_solo_rpg = df_año_rpg[df_año_rpg['Genre'] == 'Role-Playing']
        ventas_rpg_regionales = df_solo_rpg[['NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales']].sum()
        
        # Mapeamos los países del mapa para el género de Rol
        datos_mapa_rpg = []
        for iso, (columna_venta, nombre_region) in mapeo_paises.items():
            datos_mapa_rpg.append({
                'ISO': iso,
                'Ventas': ventas_rpg_regionales[columna_venta],
                'Región': nombre_region
            })
        df_mapa_rpg = pd.DataFrame(datos_mapa_rpg)
        
        # Mapa coroplético con escala ajustada y un color distintivo (Plasma)
        fig_mapa_rpg = px.choropleth(
            df_mapa_rpg, locations="ISO", color="Ventas", hover_name="Región",
            color_continuous_scale=px.colors.sequential.Plasma,
            range_color=[0, 20], # Escala optimizada para los volúmenes del género RPG
            projection="natural earth"
        )
        fig_mapa_rpg.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, coloraxis_colorbar=dict(title="Ventas RPG (M)"))
        st.plotly_chart(fig_mapa_rpg, use_container_width=True)
        
    with col_barras_jp:
        st.subheader(f"🇯🇵 Géneros más vendidos en Japón ({año_seleccionado_rpg})")
        
        # Agrupar las ventas de Japón por género en el año seleccionado
        df_generos_jp = df_año_rpg.groupby('Genre')['JP_Sales'].sum().reset_index()
        # Ordenamos de menor a mayor para que las barras más grandes queden arriba al graficar en horizontal
        df_generos_jp = df_generos_jp.sort_values(by='JP_Sales', ascending=True)
        
        # Lógica para colorear únicamente el RPG de un color resaltador (ej: Oro/Amarillo) y los demás gris/azul
        colores_condicionales = ['#FFD700' if gen == 'Role-Playing' else '#4682B4' for gen in df_generos_jp['Genre']]
        
        fig_barras_jp = px.bar(
            df_generos_jp,
            x='JP_Sales',
            y='Genre',
            orientation='h', # Barras horizontales
            labels={'JP_Sales': 'Ventas en Japón (Millones)', 'Genre': 'Géneros de Juego'},
            title=f"Preferencia por Géneros en Japón ({año_seleccionado_rpg})"
        )
        fig_barras_jp.update_traces(marker_color=colores_condicionales)
        st.plotly_chart(fig_barras_jp, use_container_width=True)

    # Nota explicativa dinámica para complementar la narrativa
    st.markdown("### 🔍 Análisis de la Tendencia Cultural:")
    if año_seleccionado_rpg == 1996:
        st.success("**💡 Hito del Mercado (1996):** Es el año de lanzamiento de Pokémon Rojo y Verde en Japón. Verás cómo la barra de **Role-Playing** se despega absurdamente sobre cualquier otro competidor.")
    elif 1990 <= año_seleccionado_rpg <= 2000:
        st.info(f"En la década de los 90 ({año_seleccionado_rpg}), sagas icónicas como Final Fantasy y Dragon Quest marcaron el estándar cultural japonés, manteniendo al género RPG en el trono indiscutido.")
    else:
        st.info(f"En el año {año_seleccionado_rpg}, a pesar de que en Occidente ganaron terreno los Shooters o juegos de Acción, Japón mantiene una resistencia histórica y los RPG continúan en la cima o los primeros puestos del podio.")