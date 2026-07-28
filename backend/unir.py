import json
import glob
import os
from pathlib import Path

# Rutas relativas desde donde está este script (backend/)
script_dir = Path(__file__).parent
catalogos_dir = script_dir / 'app' / 'modules' / 'hacienda' / 'catalogos'

# Nombre del archivo final (cámbialo si quieres)
ARCHIVO_FINAL = 'catalogos_unificados.json'
ruta_final = catalogos_dir / ARCHIVO_FINAL

# --- OPCIÓN A: Usar el nombre del archivo como clave ---
resultado = {}
for archivo in catalogos_dir.glob('*.json'):
    # Excluir el archivo final para no leerse a sí mismo
    if archivo.name == ARCHIVO_FINAL:
        continue
    
    with open(archivo, 'r', encoding='utf-8') as f:
        nombre_clave = archivo.stem  # Nombre sin extensión
        resultado[nombre_clave] = json.load(f)

# --- OPCIÓN B: Si prefieres usar un campo interno del JSON como clave ---
# (Descomenta esto y borra la Opción A)
# resultado = {}
# for archivo in catalogos_dir.glob('*.json'):
#     if archivo.name == ARCHIVO_FINAL:
#         continue
#     with open(archivo, 'r', encoding='utf-8') as f:
#         data = json.load(f)
#         # Asume que cada JSON tiene un campo "id" o "codigo" único
#         clave = data.get('id') or data.get('codigo') or archivo.stem
#         resultado[clave] = data

# Guardar el archivo final
with open(ruta_final, 'w', encoding='utf-8') as f:
    json.dump(resultado, f, indent=2, ensure_ascii=False)

print(f"✅ ¡Listo! Se creó: {ruta_final}")
print(f"📊 Total de archivos unidos: {len(resultado)}")