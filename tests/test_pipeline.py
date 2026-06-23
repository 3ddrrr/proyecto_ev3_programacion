import os
import pandas as pd
import pytest

# Definición de rutas para validar la existencia de los entregables de datos
RUTA_PROCESADA = os.path.join("data", "processed", "pacientes_final.csv")

def test_existencia_archivo_procesado():
    """Prueba que el pipeline ETL haya generado el archivo maestro final."""
    assert os.path.exists(RUTA_PROCESADA) == True, "El archivo 'pacientes_final.csv' no fue generado por el ETL."

def test_calidad_datos_maestros():
    """Prueba la estructura, consistencia y reglas de negocio del dataset procesado."""
    # Si el archivo no existe, saltar la prueba de contenido
    if not os.path.exists(RUTA_PROCESADA):
        pytest.skip("El archivo procesado no está disponible para analizar su consistencia.")
        
    df = pd.read_csv(RUTA_PROCESADA)
    
    # 1. Validar que el archivo contenga registros
    assert len(df) > 0, "El dataset procesado está completamente vacío."
    
    # 2. Validar columnas críticas exigidas por el esquema de negocio
    columnas_esperadas = ['id_paciente', 'edad', 'genero', 'peso_kg', 'estatura_cm', 'imc', 'clasificacion_imc']
    for col in columnas_esperadas:
        assert col in df.columns, f"La columna crítica '{col}' hace falta en el archivo final."
        
    # 3. Validar consistencia matemática (Reglas de negocio)
    assert (df['edad'] >= 0).all(), "Se detectaron edades negativas inconsistentes."
    assert (df['peso_kg'] > 0).all(), "Se detectaron registros con peso menor o igual a cero."