import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import os

# Configuración de la página
st.set_page_config(
    page_title="Prematrícula IF - Análisis de Resultados",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("📊 Análisis de la Prematrícula - Ingeniería Física")
st.markdown("Visualiza estadísticas de prematrícula para el segundo semestre de 2027")
st.markdown("Última modificación: lunes 27 de abril, por Alejandro Hernández Arce.")

# ============================================
# Carga de datos (caché)
# ============================================
@st.cache_data
def cargar_datos():
    ruta_base = Path(__file__).parent
    ruta_csv = ruta_base / "datos_prematricula_anonimos.csv"
    
    df = pd.read_csv(ruta_csv)
    df['Año Carné'] = df['Año Carné'].astype(str)   # Convertir a string
    return df

df = cargar_datos()

# ============================================
# Barra lateral: selector de gráfico
# ============================================
st.sidebar.markdown("## 📌 Opciones disponibles:")
opcion = st.sidebar.radio(
    "Quiero ver:",
    ["Participación por año de ingreso", 
     "Cursos con mayor demanda",
     "Comparación de dos cursos",
     "Vista general por semestre"],
    index=0
)

# ============================================
# SECCIÓN 1: GRÁFICO DE AÑOS
# ============================================
if opcion == "Participación por año de ingreso":
    st.subheader("📆 Participación por año de ingreso")
    
    # Filtrar valores numéricos
    datos_filtrado = df[df['Año Carné'].str.isnumeric()].copy()
    
    # Contar estudiantes únicos por año
    carnes_unicos_por_año = datos_filtrado.groupby('Año Carné')['Carné'].nunique().reset_index()
    carnes_unicos_por_año.columns = ['Año', 'Cantidad_Estudiantes']
    carnes_unicos_por_año = carnes_unicos_por_año.sort_values('Año')
    
    fig1 = px.bar(
        carnes_unicos_por_año,
        x='Año',
        y='Cantidad_Estudiantes',
        title='Estudiantes únicos por año de ingreso',
        text='Cantidad_Estudiantes',
        color='Cantidad_Estudiantes',
    )
    fig1.update_layout(
        xaxis_title='Año de ingreso',
        yaxis_title='Cantidad de personas',
        showlegend=False,
        font_color='white',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=500
    )
    st.plotly_chart(fig1, use_container_width=True)







# ============================================
# SECCIÓN 2: GRÁFICO DE CURSOS (con slider arriba del gráfico)
# ============================================
elif opcion == "Cursos con mayor demanda":
    st.subheader("📚 Cursos con mayor demanda")
    
    # Procesar datos (solo cursos IF o todos según tu variable)
    solo_cursos_IF = st.checkbox("Mostrar solo cursos propios de Ing. Física", value=True)   # Puedes cambiarlo o agregar un checkbox
    if solo_cursos_IF:
        datos_cursos = df[df['Curso'].str.contains('IF', na=False)].copy()
    else:
        datos_cursos = df.copy()
    
    # Filtro de semestre (radio)
    filtro_semestre = st.radio(
        "Mostrar cursos de:",
        ["Todos los semestres", "Semestres impares (I, III, V, VII, IX)", "Semestres pares (II, IV, VI, VIII, X)"],
        horizontal=True,
        index=0
    )

    # Función auxiliar para convertir romano a número
    def romano_a_numero(romano):
        romanos = {'I':1, 'II':2, 'III':3, 'IV':4, 'V':5, 'VI':6, 'VII':7, 'VIII':8, 'IX':9, 'X':10}
        return romanos.get(romano.strip().upper(), None)
    
    # Aplicar filtro de semestre a un DataFrame (función para reutilizar)
    def aplicar_filtro_semestre(df, filtro):
        if filtro == "Todos los semestres":
            return df
        # Mapear semestre a número
        df_temp = df.copy()
        df_temp['num_semestre'] = df_temp['Semestre'].apply(lambda x: romano_a_numero(x.split()[0]) if pd.notna(x) else None)
        if filtro == "Semestres impares (I, III, V, VII, IX)":
            return df_temp[df_temp['num_semestre'] % 2 == 1]
        else:  
            return df_temp[df_temp['num_semestre'] % 2 == 0]
    
    # Aplicar filtro de semestre
    datos_cursos = aplicar_filtro_semestre(datos_cursos, filtro_semestre)

    # Conteo de matrículas (no estudiantes únicos)
    conteo_cursos = datos_cursos.groupby('Curso')['Carné'].count().reset_index()
    conteo_cursos.columns = ['Curso', 'Cantidad_Matriculas']
    conteo_cursos = conteo_cursos.sort_values('Cantidad_Matriculas', ascending=False)

    # Slider personalizable (justo encima del gráfico)
    top_n = st.slider(
        "Cantidad de cursos a mostrar:",
        min_value=3,
        max_value= len(conteo_cursos),
        value=10,
        step=1
    )
    
    top_cursos = conteo_cursos.head(top_n)

    # Título dinámico
    titulo = f'Top {top_n} cursos con más prematrícula'
    if solo_cursos_IF:
        titulo += " (solo IF)"
    if filtro_semestre != "Todos los semestres":
        titulo += f" - {filtro_semestre}"
    
    # Gráfico
    fig2 = px.bar(
        top_cursos,
        x='Curso',
        y='Cantidad_Matriculas',
        title=titulo,
        text='Cantidad_Matriculas',
        color='Cantidad_Matriculas',
        color_continuous_scale='Viridis'
    )
    fig2.update_layout(
        xaxis_tickangle=-45,
        xaxis_title='Curso',
        yaxis_title='Cantidad de matrículas',
        showlegend=False,
        font_color='white',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=700
    )
    fig2.update_traces(textposition='outside')
    st.plotly_chart(fig2, use_container_width=True)
    












# ============================================
# SECCIÓN 3: COMPARACION DE DOS CURSOS
# ============================================
elif opcion == "Comparación de dos cursos":
    st.subheader("🔍 Comparación de dos cursos")

    # Checkbox para filtrar solo cursos IF
    solo_if = st.checkbox("Mostrar solo cursos propios de Ing. Física", value=True)

    # Obtener lista de cursos según filtro
    todos_cursos = sorted(df['Curso'].unique())
    if solo_if:
        cursos_disponibles = [curso for curso in todos_cursos if 'IF' in curso]
    else:
        cursos_disponibles = todos_cursos

    # Selectores de cursos en dos columnas
    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        curso_A = st.selectbox("Seleccione el primer curso:", cursos_disponibles, index=0)
    with col_sel2:
        curso_B = st.selectbox("Seleccione el segundo curso:", cursos_disponibles, index=min(1, len(cursos_disponibles)-1))
    
    # Verificar que no sean el mismo curso
    if curso_A == curso_B:
        st.warning("Por favor, seleccione dos cursos distintos para comparar.")
    else:
        # Obtener conjuntos de carnés únicos para cada curso
        carnets_A = set(df[df['Curso'] == curso_A]['Carné'].dropna().unique())
        carnets_B = set(df[df['Curso'] == curso_B]['Carné'].dropna().unique())
        
        # Estudiantes en común
        comunes = carnets_A & carnets_B
        num_comunes = len(comunes)
        
        st.metric("👥 Estudiantes que prematricularon ambos cursos", num_comunes)

        
        # Función para generar gráfico de distribución por año para un curso dado
        def grafico_por_año(curso, color_scale):
            # Filtrar datos del curso
            df_curso = df[df['Curso'] == curso].copy()
            # Filtrar años válidos (numéricos)
            df_curso = df_curso[df_curso['Año Carné'].str.isnumeric()].copy()
            # Contar estudiantes únicos por año
            por_año = df_curso.groupby('Año Carné')['Carné'].nunique().reset_index()
            por_año.columns = ['Año', 'Cantidad']
            por_año = por_año.sort_values('Año')
            
            fig = px.bar(
                por_año,
                x='Año',
                y='Cantidad',
                title=f'{curso}<br>Prematrícula total: {len(df_curso)}',
                text='Cantidad',
                color='Cantidad',
                color_continuous_scale=color_scale
            )
            fig.update_layout(
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                height=400,
                margin=dict(l=20, r=20, t=60, b=20),
                xaxis_title='Año de ingreso',
                yaxis_title='Cantidad de estudiantes'
            )
            fig.update_traces(textposition='outside')
            return fig
        
        # Mostrar dos gráficos en paralelo
        col1, col2 = st.columns(2)
        with col1:
            fig_A = grafico_por_año(curso_A, 'Blues')
            st.plotly_chart(fig_A, use_container_width=True)
        with col2:
            fig_B = grafico_por_año(curso_B, 'Reds')
            st.plotly_chart(fig_B, use_container_width=True)

# ============================================
# SECCIÓN 4: VISTA GENERAL POR SEMESTRE (tarjetas HTML personalizadas)
# ============================================
elif opcion == "Vista general por semestre":
    st.subheader("📚 Vista general por semestre")
    st.markdown("Todos los cursos organizados por semestre (I a X) y su cantidad total de matrículas.")
    
    # Preparar datos (igual que antes)
    conteo_matriculas = df.groupby('Curso')['Carné'].count().reset_index()
    conteo_matriculas.columns = ['Curso', 'Matrículas']
    semestre_por_curso = df[['Curso', 'Semestre']].drop_duplicates(subset='Curso')
    df_cursos = semestre_por_curso.merge(conteo_matriculas, on='Curso', how='left')
    
    # Limpiar nombre del curso (quitar código)
    def limpiar_nombre_curso(curso):
        if '-' in curso:
            return curso.split('-', 1)[1].strip()
        return curso
    df_cursos['Nombre_limpio'] = df_cursos['Curso'].apply(limpiar_nombre_curso)
    
    # Extraer número de semestre
    def semestre_a_numero(sem):
        romano = sem.split()[0]
        romanos = {'I':1, 'II':2, 'III':3, 'IV':4, 'V':5, 'VI':6, 'VII':7, 'VIII':8, 'IX':9, 'X':10}
        return romanos.get(romano, 0)
    df_cursos['num_semestre'] = df_cursos['Semestre'].apply(semestre_a_numero)
    df_cursos = df_cursos.sort_values(['num_semestre', 'Nombre_limpio'])
    
    # CSS para las columnas y tarjetas personalizadas
    st.markdown("""
        <style>
        /* Contenedor de columnas permite scroll horizontal */
        .stHorizontalBlock {
            overflow-x: auto !important;
            flex-wrap: nowrap !important;
            gap: 1rem;
        }
        /* Cada columna tiene ancho fijo */
        div[data-testid="column"] {
            min-width: 600px !important;
            flex: 0 0 auto !important;
        }
        /* Tarjeta personalizada */
        .custom-metric-card {
            background-color: #262730;
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 16px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #4CAF50;
        }
        .custom-metric-label {
            font-size: 0.75rem;
            color: #FAFAFA;
            white-space: normal;
            word-wrap: break-word;
            margin-bottom: 8px;
            line-height: 1.1;
        }
        .custom-metric-value {
            font-size: 1.1rem;
            font-weight: bold;
            color: #FFFFFF;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Crear 10 columnas
    columnas = st.columns(10)
    semestres_romanos = ['I','II','III','IV','V','VI','VII','VIII','IX','X']
    
    for i, sem_num in enumerate(range(1, 11)):
        with columnas[i]:
            st.markdown(f"**Semestre {semestres_romanos[i]}**")
            cursos_sem = df_cursos[df_cursos['num_semestre'] == sem_num]
            if cursos_sem.empty:
                st.caption("Sin cursos")
            else:
                for _, row in cursos_sem.iterrows():
                    # Generar tarjeta HTML manual
                    card_html = f"""
                        <div class="custom-metric-card">
                            <div class="custom-metric-label">{row['Nombre_limpio']}</div>
                            <div class="custom-metric-value">{row['Matrículas']}</div>
                        </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)
