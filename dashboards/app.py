import os
import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Cuadro de Mando Integral - NHANES", page_icon="📊", layout="wide")

# URL de la API (Soporta Docker y Local)
URL_API = os.environ.get("API_URL", "http://127.0.0.1:8000")

# --- FUNCIONES DE CONEXIÓN A LA API ---
def obtener_metricas_api():
    try:
        response = requests.get(f"{URL_API}/api/pacientes", timeout=5)
        if response.status_code == 200:
            df = pd.DataFrame(response.json())
            metricas = {
                "total": len(df),
                "edad_promedio": round(df['edad'].mean(), 1),
                "imc_promedio": round(df['imc'].mean(), 1),
                "distribucion_genero": df['genero'].value_counts().to_dict(),
                "distribucion_imc": df['clasificacion_imc'].value_counts().to_dict()
            }
            return metricas, df
    except:
        return None, None
    return None, None

def predecir_estado_api(datos_paciente):
    try:
        response = requests.post(f"{URL_API}/api/predict", json=datos_paciente, timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error en el servidor: {response.text}")
    except:
        st.error("No se pudo conectar con el motor de Inteligencia Artificial.")
    return None

# --- INTERFAZ DEL DASHBOARD ---
st.title("Sistema Integrado de Monitoreo de Salud e IA")
st.markdown("Plataforma analítica con integración de modelos predictivos de Machine Learning para apoyo al diagnóstico.")

metricas, df_pacientes = obtener_metricas_api()

if metricas is None:
    st.error("Error de Comunicación: Asegúrese de que la API interna (FastAPI) esté ejecutándose.")
else:
    # 4 Pestañas ahora (Agregamos la de IA)
    tab_ejecutiva, tab_operativa, tab_ia, tab_tecnica = st.tabs([
        "📊 Vista Ejecutiva", 
        "👥 Búsqueda de Pacientes", 
        "🤖 Predicción con IA",
        "⚙️ Estado del Sistema"
    ])
    
    # 1. VISTA EJECUTIVA
    with tab_ejecutiva:
        st.header("Indicadores Macro de Salud")
        c1, c2, c3 = st.columns(3)
        c1.metric("Pacientes Analizados", f"{metricas['total']:,}")
        c2.metric("Edad Promedio", f"{metricas['edad_promedio']} años")
        c3.metric("IMC Global Promedio", f"{metricas['imc_promedio']}")
        
        st.markdown("---")
        col_graf1, col_graf2 = st.columns(2)
        with col_graf1:
            df_imc = pd.DataFrame(list(metricas['distribucion_imc'].items()), columns=['Clasificación', 'Total'])
            fig_imc = px.bar(df_imc, x='Clasificación', y='Total', title='Distribución Nutricional', template='plotly_white')
            st.plotly_chart(fig_imc, use_container_width=True)
        with col_graf2:
            df_gen = pd.DataFrame(list(metricas['distribucion_genero'].items()), columns=['Género', 'Total'])
            fig_gen = px.pie(df_gen, names='Género', values='Total', title='Proporción por Género', hole=0.4)
            st.plotly_chart(fig_gen, use_container_width=True)

    # 2. VISTA OPERATIVA
    with tab_operativa:
        st.header("Padrón Clínico")
        col_f1, col_f2 = st.columns(2)
        filtro_genero = col_f1.selectbox("Género:", ["Todos", "Masculino", "Femenino"])
        filtro_imc = col_f2.selectbox("Diagnóstico:", ["Todos"] + list(metricas['distribucion_imc'].keys()))
        
        df_mostrar = df_pacientes.copy()
        if filtro_genero != "Todos": df_mostrar = df_mostrar[df_mostrar['genero'] == filtro_genero]
        if filtro_imc != "Todos": df_mostrar = df_mostrar[df_mostrar['clasificacion_imc'] == filtro_imc]
        
        st.dataframe(df_mostrar[['id_paciente', 'edad', 'genero', 'peso_kg', 'estatura_cm', 'imc', 'clasificacion_imc']], use_container_width=True, hide_index=True)

    # 3. VISTA DE INTELIGENCIA ARTIFICIAL (LA GRAN NOVEDAD DEL EFT)
    with tab_ia:
        st.header("Motor de Diagnóstico Predictivo (Random Forest)")
        st.markdown("Ingrese los signos vitales del nuevo paciente. El algoritmo de Machine Learning predecirá su estado nutricional en tiempo real basándose en patrones históricos.")
        
        # Formulario de ingreso de datos
        with st.form("formulario_ml"):
            c1, c2, c3, c4 = st.columns(4)
            edad_in = c1.number_input("Edad (años)", min_value=18, max_value=120, value=30)
            genero_in = c2.selectbox("Género", ["Masculino", "Femenino"])
            peso_in = c3.number_input("Peso (kg)", min_value=30.0, max_value=250.0, value=75.0)
            estatura_in = c4.number_input("Estatura (cm)", min_value=100.0, max_value=230.0, value=170.0)
            
            submit = st.form_submit_button("🔮 Predecir Estado Nutricional", use_container_width=True)
            
        if submit:
            datos_enviar = {"edad": edad_in, "genero": genero_in, "peso_kg": peso_in, "estatura_cm": estatura_in}
            
            with st.spinner("La Inteligencia Artificial está analizando los datos..."):
                resultado = predecir_estado_api(datos_enviar)
                
            if resultado:
                st.success("Análisis completado exitosamente.")
                
                # Mostrar resultado en grande
                res_col1, res_col2 = st.columns([1, 2])
                with res_col1:
                    st.metric("Diagnóstico Sugerido", resultado['prediccion_diagnostico'])
                    st.metric("Confianza del Modelo", f"{resultado['porcentaje_confianza']}%")
                
                with res_col2:
                    st.markdown("**Desglose de Probabilidades por Clase**")
                    df_probs = pd.DataFrame(list(resultado['detalle_probabilidades'].items()), columns=['Estado', 'Probabilidad'])
                    fig_prob = px.bar(df_probs, x='Probabilidad', y='Estado', orientation='h', color='Estado')
                    fig_prob.update_layout(height=250, showlegend=False, margin=dict(l=0, r=0, t=0, b=0))
                    st.plotly_chart(fig_prob, use_container_width=True)

    # 4. VISTA TÉCNICA
    with tab_tecnica:
        st.header("Monitor de Infraestructura")
        st.success("Conexión con FastAPI: ESTABLE")
        st.info("Modelo de ML: Random Forest Classifier (Scikit-Learn) cargado en memoria RAM del servidor.")