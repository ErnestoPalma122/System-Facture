# app/modules/hacienda/catalogos_routes.py
from fastapi import APIRouter, HTTPException, status
import os
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/catalogos", tags=["Catálogos Ministerio de Hacienda"])

# Ruta absoluta al archivo unificado
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_UNIFICADO = os.path.join(CURRENT_DIR, "catalogos", "catalogos_unificados.json")

# Caché en memoria para evitar leer el disco en cada petición (Respuesta instantánea)
_cache_unificado: Dict[str, Any] = None


@router.get(
    "/unificados",
    summary="Obtener todos los catálogos unificados",
    description="Devuelve un único objeto JSON con todos los catálogos del Ministerio de Hacienda anidados. Optimizado para consumo del frontend y filtros en cascada."
)
def obtener_catalogos_unificados():
    """
    Obtiene el archivo catalogos_unificados.json completo.
    Utiliza caché en memoria para una respuesta ultra rápida.
    """
    global _cache_unificado
    
    # 1. Verificar si ya está en caché (Respuesta instantánea)
    if _cache_unificado is not None:
        logger.info("⚡ Sirviendo catálogos unificados desde caché en memoria")
        return _cache_unificado

    # 2. Verificar que el archivo exista en disco
    if not os.path.exists(ARCHIVO_UNIFICADO):
        logger.error(f"❌ No se encontró el archivo unificado en: {ARCHIVO_UNIFICADO}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="El archivo de catálogos unificados no existe en el servidor."
        )

    # 3. Leer, parsear y guardar en caché
    try:
        logger.info("📂 Leyendo 'catalogos_unificados.json' desde disco (primera vez)")
        with open(ARCHIVO_UNIFICADO, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        # Guardar en caché para todas las futuras peticiones
        _cache_unificado = datos
        
        logger.info(f"✅ Catálogos unificados cargados en caché exitosamente")
        return datos

    except json.JSONDecodeError as e:
        logger.error(f"❌ Error al parsear JSON unificado: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="El archivo de catálogos unificados tiene un formato JSON inválido."
        )
    except Exception as e:
        logger.error(f"❌ Error inesperado al leer catálogos unificados: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al procesar los catálogos."
        )