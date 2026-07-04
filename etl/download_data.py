import os
import urllib.request

# Definir las rutas de las carpetas de datos
os.makedirs(os.path.join("data", "raw"), exist_ok=True)
os.makedirs(os.path.join("data", "processed"), exist_ok=True)

print("✅ Carpetas 'data/raw' y 'data/processed' verificadas/creadas con éxito.")


def descargar_datos_nhanes():
    # Definir las URLs correctas del repositorio publico de datos del CDC
    urls = {
        "demografia": "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/DEMO_J.xpt",
        "datos_corporales": "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/BMX_J.xpt"
    }
    
    destino_dir = os.path.join("data", "raw")
    os.makedirs(destino_dir, exist_ok=True)
    
    print("Iniciando la descarga automatizada de datos NHANES...")
    
    for nombre, url in urls.items():
        nombre_archivo = url.split("/")[-1].upper() # Mantener la extension en mayusculas para consistencia
        ruta_completa = os.path.join(destino_dir, nombre_archivo)
        
        try:
            print(f"Descargando {nombre} desde {url}...")
            # Forzar un User-Agent en la peticion para evitar bloqueos del servidor
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(req) as response, open(ruta_completa, 'wb') as out_file:
                out_file.write(response.read())
                
            print(f"Guardado exitosamente en: {ruta_completa}")
        except Exception as e:
            print(f"Error al descargar {nombre}: {e}")

if __name__ == "__main__":
    descargar_datos_nhanes()
