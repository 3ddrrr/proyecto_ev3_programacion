import os
import sqlite3
import logging
import requests
import pandas as pd

# Configuracion del Logging Profesional
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("etl_process.log", encoding="utf-8")
    ]
)

def extraer_api_medicos():
    """Fuente 2: Extrae datos de personal medico desde una API REST publica."""
    url_api = "https://jsonplaceholder.typicode.com/users"
    logging.info(f"Conectando a la API REST: {url_api}")
    
    try:
        response = requests.get(url_api, timeout=10)
        response.raise_for_status()
        
        datos_api = response.json()
        
        medicos = []
        for user in datos_api:
            medicos.append({
                "id_medico": user["id"],
                "nombre_medico": user["name"],
                "email_medico": user["email"],
                "ciudad_clinica": user["address"]["city"]
            })
            
        df_medicos = pd.DataFrame(medicos)
        ruta_guardado = os.path.join("data", "raw", "medicos_api.csv")
        df_medicos.to_csv(ruta_guardado, index=False)
        logging.info(f"Fuente 2 (API) extraida y guardada en: {ruta_guardado}")
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Error critico al conectar con la API REST: {e}")
        raise e

def crear_base_datos_sql():
    """Fuente 3: Crea una base de datos SQL local con el catalogo de rangos IMC."""
    db_dir = os.path.join("data", "raw")
    os.makedirs(db_dir, exist_ok=True)
    db_path = os.path.join(db_dir, "clinica_local.db")
    
    logging.info(f"Inicializando Base de Datos SQL en: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS catalogo_imc (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                clasificacion TEXT NOT NULL,
                imc_min REAL,
                imc_max REAL
            )
        """)
        
        cursor.execute("DELETE FROM catalogo_imc")
        datos_imc = [
            ("Bajo Peso", 0.0, 18.49),
            ("Normal", 18.5, 24.99),
            ("Sobrepeso", 25.0, 29.99),
            ("Obesidad Grado I", 30.0, 34.99),
            ("Obesidad Grado II", 35.0, 39.99),
            ("Obesidad Grado III", 40.0, 100.0)
        ]
        
        cursor.executemany("""
            INSERT INTO catalogo_imc (clasificacion, imc_min, imc_max)
            VALUES (?, ?, ?)
        """, datos_imc)
        
        conn.commit()
        logging.info("Fuente 3 (SQL DB) creada y poblada con exito.")
        
    except sqlite3.Error as e:
        logging.error(f"Error en la base de datos SQL: {e}")
        raise e
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    logging.info("Iniciando Fase de Extraccion de Fuentes Secundarias...")
    extraer_api_medicos()
    crear_base_datos_sql()
    logging.info("Extraccion complementaria finalizada exitosamente.")