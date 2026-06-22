import streamlit as str
import requests
import pandas as pd
import plotly.express as px

# Configuración de la página del Dashboard
str.set_page_config(
    page_title="Cuadro de Mando Integral - NHANES",
    page_icon="📊",
    layout="wide"
)

# Definición de la URL base de nuestra API interna
URL_API = "http://127.0.0.1:8000"

# Funciones auxiliares para consumir la API con manejo de errores
def obtener_metricas_api():
    try:
        response = requests.get(f"{URL_API}/api/metricas", timeout=5)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.ConnectionError:
        return None
    return None

def obtener_pacientes_api(genero=None, clasificacion=None):
    params = {}
    if genero and genero != "Todos":
        params["genero"] = genero
    if clasificacion and clasificacion != "Todas":
        params["clasificacion"] = clasificacion
        
    try:
        response = requests.get(f"{URL_API}/api/pacientes", params=params, timeout=5)
        if response.status_code == 200:
            return response.json().get("data", [])
    except requests.exceptions.ConnectionError:
        return []
    return []

# Título Principal e Introducción Institucional
str.title("Sistema Integrado de Monitoreo de Salud de la Población")
str.markdown("""
Esta plataforma consolida los datos analíticos del estudio nacional **NHANES**, integrados mediante un pipeline ETL automatizado 
con catálogos clínicos de la OMS y registros del personal médico mediante APIs REST.
""")

# Consumo de datos iniciales de la API
metricas = obtener_metricas_api()

if metricas is None:
    str.error("Error de Comunicación: No se pudo conectar con la API interna. Asegúrese de que el servicio FastAPI esté ejecutándose en el puerto 8000.")
else:
    # Definición de pestañas orientadas a diferentes audiencias (Requisito de Pauta)
    tab_ejecutiva, tab_operativa, tab_tecnica = str.tabs([
        " Vista Ejecutiva (Dirección médica)", 
        " Vista Operativa (Gestión de Pacientes)", 
        " Vista Técnica (Estado del Sistema)"
    ])
    
    # ----------------------------------------------------
    # 1. VISTA EJECUTIVA: Orientada a la toma de decisiones generales
    # ----------------------------------------------------
    with tab_ejecutiva:
        str.header("Indicadores Clave de Rendimiento (KPIs) de Salud")
        
        # Fila de métricas principales
        col1, col2, col3, col4 = str.columns(4)
        col1.metric("Total Pacientes Evaluados", f"{metricas['total_pacientes_analizados']:,}")
        col2.metric("Edad Promedio Poblacional", f"{metricas['edad_promedio']} años")
        col3.metric("Índice de Masa Corporal (IMC) Promedio", f"{metricas['imc_promedio']}")
        col4.metric("Peso Promedio General", f"{metricas['peso_promedio_kg']} kg")
        
        str.markdown("---")
        
        # Gráficos Analíticos Complejos
        str.subheader("Análisis Epidemiológico de la Población")
        col_graf1, col_graf2 = str.columns(2)
        
        with col_graf1:
            # Distribución del IMC según la OMS
            df_imc = pd.DataFrame(list(metricas['distribucion_imc'].items()), columns=['Clasificación', 'Total'])
            fig_imc = px.bar(
                df_imc, 
                x='Clasificación', 
                y='Total', 
                title='Distribución de la Población según Rangos de IMC (OMS)',
                labels={'Total': 'Cantidad de Registros'},
                template='plotly_white'
            )
            str.plotly_chart(fig_imc, use_container_width=True)
            
        with col_graf2:
            # Distribución de Género
            df_genero = pd.DataFrame(list(metricas['distribucion_genero'].items()), columns=['Género', 'Total'])
            fig_gen = px.pie(
                df_genero, 
                names='Género', 
                values='Total', 
                title='Proporción de Participantes por Género',
                hole=0.4,
                template='plotly_white'
            )
            str.plotly_chart(fig_gen, use_container_width=True)

    # ----------------------------------------------------
    # 2. VISTA OPERATIVA: Orientada a coordinadores de la clínica y médicos
    # ----------------------------------------------------
    with tab_operativa:
        str.header("Buscador y Herramienta de Filtros Clínicos")
        str.markdown("Filtre el padrón de pacientes en tiempo real para auditorías o asignación de tratamientos médicos.")
        
        # Filtros interactivos vinculados a parámetros de la API
        col_f1, col_f2 = str.columns(2)
        with col_f1:
            filtro_genero = str.selectbox("Seleccionar Género:", ["Todos", "Masculino", "Femenino"])
        with col_f2:
            opciones_imc = ["Todas"] + list(metricas['distribucion_imc'].keys())
            filtro_imc = str.selectbox("Seleccionar Estado Nutricional (OMS):", opciones_imc)
            
        # Llamar a la API con los filtros seleccionados
        datos_pacientes = obtener_pacientes_api(genero=filtro_genero, clasificacion=filtro_imc)
        
        if datos_pacientes:
            df_pacientes = pd.DataFrame(datos_pacientes)
            
            # Limpieza estética de las columnas expuestas al usuario operativo
            columnas_visibles = {
                'id_paciente': 'ID Paciente',
                'edad': 'Edad',
                'genero': 'Género',
                'peso_kg': 'Peso (kg)',
                'estatura_cm': 'Estatura (cm)',
                'imc': 'IMC',
                'nombre_medico': 'Médico Examinador',
                'ciudad_clinica': 'Sede Clínica',
                'clasificacion_imc': 'Diagnóstico OMS'
            }
            df_mostrar = df_pacientes[list(columnas_visibles.keys())].rename(columns=columnas_visibles)
            
            str.dataframe(df_mostrar, use_container_width=True, hide_index=True)
            str.caption(f"Mostrando los primeros {len(df_mostrar)} registros que cumplen con el criterio.")
        else:
            str.warning("No se encontraron registros de pacientes con los filtros seleccionados.")

    # ----------------------------------------------------
    # 3. VISTA TÉCNICA: Orientada a Ingenieros de Datos o administradores TI
    # ----------------------------------------------------
    with tab_tecnica:
        str.header("Monitoreo de Infraestructura y Datos de la API")
        str.markdown("Estado técnico de la solución desacoplada y validación de la carga de datos.")
        
        col_t1, col_t2 = str.columns(2)
        with col_t1:
            str.subheader("Esquema de Endpoints Activos")
            str.json({
                "GET /": "Verificación de estado de la API (Healthcheck)",
                "GET /api/metricas": "Retorna diccionarios con agregaciones estadísticas precalculadas",
                "GET /api/pacientes": "Permite consultas parametrizadas con filtros opcionales de negocio"
            })
        with col_t2:
            str.subheader("Métricas de Integración Tecnológica")
            str.success("Conexión con el Servidor API: ESTABLE (Código 200)")
            str.info("Estrategia de Carga: Archivos SAS Transport (.XPT) combinados con SQLite e inyección dinámica desde API JSONPlaceholder.")