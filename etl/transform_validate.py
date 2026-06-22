import os
import sqlite3
import logging
import pandas as pd
import numpy as np

# Reutilizamos la configuracion de logging profesional
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("etl_process.log", encoding="utf-8")
    ]
)

def validar_esquemas(df):
    """
    Valida la calidad y el esquema de los datos antes de exportar.
    Lanza una excepcion si encuentra inconsistencias graves.
    """
    logging.info("Iniciando validacion de esquemas y consistencia de datos...")
    
    # 1. Verificar columnas esenciales obligatorias
    columnas_requeridas = ['id_paciente', 'edad', 'genero', 'peso_kg', 'estatura_cm', 'imc']
    for col in columnas_requeridas:
        if col not in df.columns:
            raise ValueError(f"Validacion fallida: Falta la columna critica {col}")
            
    # 2. Validacion de tipos de datos
    if not pd.api.types.is_numeric_dtype(df['edad']):
        raise TypeError("Validacion fallida: La columna 'edad' debe ser numerica.")
        
    # 3. Validacion de restricciones de negocio (Limpieza de outliers imposibles)
    conteo_inicial = len(df)
    df = df[(df['edad'] >= 0) & (df['edad'] <= 120)]
    df = df[df['peso_kg'] > 0]
    df = df[df['estatura_cm'] > 0]
    
    eliminados = conteo_inicial - len(df)
    if eliminados > 0:
        logging.warning(f"Se eliminaron {eliminados} registros por inconsistencias en rangos fisicos.")
        
    logging.info("Validacion de esquemas completada exitosamente.")
    return df

def transformar_datos():
    """
    Proceso central de transformacion, mapeo e integracion de las 3 fuentes.
    """
    logging.info("Iniciando fase de transformacion e integracion...")
    
    try:
        # RUTA DE ARCHIVOS
        ruta_demo = os.path.join("data", "raw", "DEMO_J.XPT")
        ruta_bmx = os.path.join("data", "raw", "BMX_J.XPT")
        ruta_medicos = os.path.join("data", "raw", "medicos_api.csv")
        ruta_db = os.path.join("data", "raw", "clinica_local.db")
        
        # 1. LEER FUENTE 1 (NHANES - Archivos XPT)
        logging.info("Cargando archivos base NHANES...")
        df_demo = pd.read_sas(ruta_demo, format='xport')
        df_bmx = pd.read_sas(ruta_bmx, format='xport')
        
        # Seleccionar y renombrar columnas clave para legibilidad
        df_demo = df_demo[['SEQN', 'RIAGENDR', 'RIDAGEYR']].rename(
            columns={'SEQN': 'id_paciente', 'RIAGENDR': 'genero_id', 'RIDAGEYR': 'edad'}
        )
        df_bmx = df_bmx[['SEQN', 'BMXWT', 'BMXHT', 'BMXBMI']].rename(
            columns={'SEQN': 'id_paciente', 'BMXWT': 'peso_kg', 'BMXHT': 'estatura_cm', 'BMXBMI': 'imc'}
        )
        
        # Unir componentes de la Fuente 1 (Demografia + Examenes)
        df_nhanes = pd.merge(df_demo, df_bmx, on='id_paciente', how='inner')
        
        # Tratar nulos criticos eliminando filas sin mediciones corporales
        df_nhanes = df_nhanes.dropna(subset=['peso_kg', 'estatura_cm', 'imc'])
        
        # Mapear valores codificados (1.0 = Masculino, 2.0 = Femenino)
        df_nhanes['genero'] = df_nhanes['genero_id'].map({1.0: 'Masculino', 2.0: 'Femenino'})
        df_nhanes.drop(columns=['genero_id'], inplace=True)
        
        # 2. INTEGRAR CON FUENTE 2 (API REST - Medicos)
        df_medicos = pd.read_csv(ruta_medicos)
        listado_ids_medicos = df_medicos['id_medico'].unique()
        
        # Asignar un medico aleatorio pero valido del pool de la API a cada paciente
        np.random.seed(42) # Semilla para asegurar la reproducibilidad del proceso
        df_nhanes['id_medico'] = np.random.choice(listado_ids_medicos, size=len(df_nhanes))
        
        # Combinar datos de pacientes con informacion del medico
        df_integrado = pd.merge(df_nhanes, df_medicos, on='id_medico', how='left')
        
        # 3. INTEGRAR CON FUENTE 3 (SQL DB - Catalogo IMC)
        logging.info("Consultando catalogo de clasificacion desde Base de Datos SQL...")
        conn = sqlite3.connect(ruta_db)
        df_catalogo = pd.read_sql_query("SELECT clasificacion, imc_min, imc_max FROM catalogo_imc", conn)
        conn.close()
        
        # Clasificar logicamente cada registro evaluando los rangos de la base de datos
        def clasificar_imc_registro(imc_valor):
            for _, fila in df_catalogo.iterrows():
                if fila['imc_min'] <= imc_valor <= fila['imc_max']:
                    return fila['clasificacion']
            return "No Clasificado"
            
        df_integrado['clasificacion_imc'] = df_integrado['imc'].apply(clasificar_imc_registro)
        
        # 4. VALIDAR ESQUEMA FINAL
        df_final = validar_esquemas(df_integrado)
        
        # 5. GUARDAR DATOS PROCESADOS
        ruta_salida = os.path.join("data", "processed", "pacientes_final.csv")
        os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
        df_final.to_csv(ruta_salida, index=False)
        logging.info(f"Proceso ETL finalizado con exito. Archivo maestro guardado en: {ruta_salida}")
        
    except Exception as e:
        logging.error(f"Error critico en la fase de transformacion: {e}")
        raise e

if __name__ == "__main__":
    transformar_datos()