import os
import urllib.request

def descargar_datos_nhanes():
    # 1. Definir las URLs de los archivos XPT del CDC (NHANES 2017-2018)
    urls = {
        "demografia": "https://wwwn.cdc.gov/Nchs/Nhanes/2017-2018/DEMO_J.XPT",
        "datos_corporales": "https://wwwn.cdc.gov/Nchs/Nhanes/2017-2018/BMX_J.XPT"
    }
    
    # 2. Ruta de destino (data/raw/)
    destino_dir = os.path.join("data", "raw")
    
    # Asegurar que la carpeta exista, si no, crearla
    os.makedirs(destino_dir, exist_ok=True)
    
    print("🚀 Iniciando la descarga automatizada de datos NHANES...")
    
    for nombre, url in urls.items():
        nombre_archivo = url.split("/")[-1]
        ruta_completa = os.path.join(destino_dir, nombre_archivo)
        
        try:
            print(print(f"📥 Descargando {nombre} desde {url}..."))
            # Descarga el archivo desde la web del CDC y lo guarda localmente
            urllib.request.urlretrieve(url, ruta_completa)
            print(f"✅ Guardado exitosamente en: {ruta_completa}")
        except Exception as e:
            print(f"❌ Error al descargar {nombre}: {e}")

if __name__ == "__main__":
    descargar_datos_nhanes()