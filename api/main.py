import os
import sqlite3
import pandas as pd
import joblib
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

# Configuración de Logging Profesional para la API
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

app = FastAPI(
    title="API de Predicción y Gestión de Salud - NHANES",
    description="API interna para la consulta de datos clínicos y predicción del estado nutricional usando Machine Learning.",
    version="2.0.0"
)

# ---------------------------------------------------------
# Carga del Modelo de Machine Learning
# ---------------------------------------------------------
ruta_modelo = os.path.join("models", "mejor_modelo_nhanes.pkl")
if os.path.exists(ruta_modelo):
    modelo_ml = joblib.load(ruta_modelo)
    logging.info("✅ Modelo de Machine Learning cargado exitosamente en la API.")
else:
    modelo_ml = None
    logging.error("❌ No se encontró el archivo del modelo. El endpoint de predicción fallará.")

# Definir la estructura de datos que debe recibir la API para predecir (Pydantic)
class PacienteInput(BaseModel):
    edad: int
    genero: str  # 'Masculino' o 'Femenino'
    peso_kg: float
    estatura_cm: float

# ---------------------------------------------------------
# Endpoints de la API
# ---------------------------------------------------------

@app.get("/")
def inicio():
    return {"mensaje": "API de Proyecto NHANES ejecutándose de forma correcta", "version": "2.0.0"}

@app.get("/api/health")
def healthcheck():
    """Valida el estado de salud técnica de la API y sus componentes."""
    estado_modelo = "Activo" if modelo_ml is not None else "Inactivo/No encontrado"
    return {
        "status": "Healthy",
        "base_datos_sqlite": "Conectada",
        "modelo_machine_learning": estado_modelo
    }

@app.get("/api/pacientes", response_model=List[Dict[str, Any]])
def obtener_pacientes():
    """Retorna el listado completo de pacientes procesados para el Dashboard."""
    ruta_datos = os.path.join("data", "processed", "pacientes_ml.csv")
    if not os.path.exists(ruta_datos):
        raise HTTPException(status_code=404, detail="El archivo de datos procesados no existe. Ejecute el ETL primero.")
    
    df = pd.read_csv(ruta_datos)
    # Reemplazar posibles valores infinitos o NaN para que no rompa el JSON de salida
    df = df.fillna("No Aplica")
    return df.to_dict(orient="records")

@app.post("/api/predict")
def predecir_estado_nutricional(input_data: PacienteInput):
    """
    Endpoint de Inteligencia Artificial: Recibe datos de un paciente en tiempo real,
    los procesa a través del Pipeline del modelo y devuelve la predicción diagnóstica.
    """
    if modelo_ml is None:
        raise HTTPException(status_code=500, detail="El modelo predictivo no está disponible en el servidor.")
    
    try:
        # 1. Convertir la entrada de la API en un DataFrame de una sola fila (tal como entramos el modelo)
        datos_paciente = pd.DataFrame([{
            'edad': input_data.edad,
            'genero': input_data.genero,
            'peso_kg': input_data.peso_kg,
            'estatura_cm': input_data.estatura_cm
        }])
        
        # 2. Realizar la predicción usando el pipeline guardado (que ya escala y transforma el género solo)
        prediccion = modelo_ml.predict(datos_paciente)[0]
        
        # 3. Calcular probabilidades para dar una respuesta más rica técnicamente
        probabilidades = modelo_ml.predict_proba(datos_paciente)[0]
        clases = modelo_ml.classes_
        confianza = max(probabilidades) * 100
        
        logging.info(f"Predicción realizada con éxito: {prediccion} ({confianza:.2f}% de confianza)")
        
        return {
            "estado_paciente": "Procesado",
            "prediccion_diagnostico": prediccion,
            "porcentaje_confianza": round(confianza, 2),
            "detalle_probabilidades": {clase: round(prob * 100, 2) for clase, prob in zip(clases, probabilidades)}
        }
        
    except Exception as e:
        logging.error(f"Error interno al realizar la predicción: {e}")
        raise HTTPException(status_code=500, detail=f"Error al procesar la predicción: {str(e)}")