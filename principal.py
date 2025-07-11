import os
import requests
import hashlib
from pathlib import Path

# Ruta local del archivo
local_path = Path(__file__).parent / "app_qgis_v3.py"

# URL cruda desde tu GitHub (REPO: haescalante14 / streamlit-rutas-colectivo)
GITHUB_RAW_URL = "https://raw.githubusercontent.com/haescalante14/streamlit-rutas-colectivo/main/app_qgis_v3.py"

# Función para calcular el hash SHA256 del contenido
def sha256_of(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

# Descargar la versión desde GitHub
print("📡 Verificando versión en GitHub...")
response = requests.get(GITHUB_RAW_URL)
if response.status_code != 200:
    raise Exception(f"❌ No se pudo acceder al archivo en GitHub: {response.status_code}")

remote_text = response.text
remote_hash = sha256_of(remote_text)

# Comprobar si hay que descargar/actualizar
if not local_path.exists():
    print("📥 El archivo no existe localmente. Descargando desde GitHub...")
    local_path.write_text(remote_text, encoding='utf-8')
elif sha256_of(local_path.read_text(encoding='utf-8')) != remote_hash:
    print("🔄 Nueva versión encontrada en GitHub. Actualizando archivo local...")
    local_path.write_text(remote_text, encoding='utf-8')
else:
    print("✅ La versión local ya está actualizada.")

# Ejecutar el archivo actualizado
print("🚀 Ejecutando app_qgis_v3.py...")
exec(local_path.read_text(encoding='utf-8'), globals())
