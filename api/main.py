import os
import logging
from fastapi import FastAPI, HTTPException, Query
import pandas as pd

# Configuracion de logging institucional
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("api_process.log", encoding="utf-8")
    ]
)

app = FastAPI(
    title="API de Monitoreo de Salud - NHANES",
    description="API interna para proveer datos procesados e integrados del estudio NHANES y clinica local.",
    version="1.0.0"
)

# Ruta del archivo procesado
RUTA_DATOS = os.path.join("data", "processed", "pacientes_final.csv")

def cargar_datos():
    """Funcion auxiliar para cargar el dataset procesado."""
    if not os.path.exists(RUTA_DATOS):
        logging.error(f"Archivo de datos no encontrado en la ruta: {RUTA_DATOS}")
        raise HTTPException(status_code=500, detail="El archivo de datos procesados no existe. Ejecute el pipeline ETL primero.")
    return pd.read_csv(RUTA_DATOS)

@app.get("/", tags=["General"])
def read_root():
    """Endpoint de verificacion de estado de la API."""
    return {
        "status": "online",
        "proyecto": "Evaluacion Parcial 3 - SCY1101",
        "descripcion": "Servicio de datos medicos NHANES"
    }

@app.get("/api/pacientes", tags=["Datos"])
def obtener_pacientes(
    genero: str = Query(None, description="Filtrar por genero: Masculino o Femenino"),
    clasificacion: str = Query(None, description="Filtrar por clasificacion de IMC de la OMS")
):
    """
    Retorna el listado de pacientes integrados.
    Permite filtros opcionales por genero y clasificacion de IMC.
    """
    try:
        df = cargar_datos()
        
        # Aplicar filtros si son proporcionados
        if genero:
            df = df[df['genero'].str.lower() == genero.lower()]
        if clasificacion:
            df = df[df['clasificacion_imc'].str.lower() == clasificacion.lower()]
            
        # Convertir a diccionario orientando por registros (formato JSON)
        # Se limita a 1000 registros para optimizar la transferencia de datos inicial
        resultado = df.head(1000).to_dict(orient="records")
        return {
            "total_registros_mostrados": len(resultado),
            "data": resultado
        }
    except Exception as e:
        logging.error(f"Error al procesar consulta de pacientes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/metricas", tags=["Analitica"])
def obtener_metricas_globales():
    """
    Retorna indicadores clave de rendimiento (KPIs) precalculados
    para el consumo directo del dashboard.
    """
    try:
        df = cargar_datos()
        
        metricas = {
            "total_pacientes_analizados": int(len(df)),
            "edad_promedio": float(round(df['edad'].mean(), 2)),
            "imc_promedio": float(round(df['imc'].mean(), 2)),
            "peso_promedio_kg": float(round(df['peso_kg'].mean(), 2)),
            "distribucion_genero": df['genero'].value_counts().to_dict(),
            "distribucion_imc": df['clasificacion_imc'].value_counts().to_dict()
        }
        return metricas
    except Exception as e:
        logging.error(f"Error al calcular metricas globales: {e}")
        raise HTTPException(status_code=500, detail=str(e))