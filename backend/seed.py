#aqui agreagar o sembrar los estados

# seed.py
"""
Script para poblar la base de datos con datos iniciales (seed data).
Específicamente: Estados de items de inventario.

Uso:
    python seed.py
"""

import sys
import os

# Agregar el directorio del proyecto al path para poder importar los módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.core.database import SessionLocal, engine
from app.modules.inventario.models_inventario import EstadoItems
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ===========================================================
# ESTADOS A POBLAR
# ===========================================================

ESTADOS_INICIALES = [
    {
        "estado": "PENDIENTE",
        "descripcion": "El item está pendiente de revisión o procesamiento"
    },
    {
        "estado": "PARCIAL",
        "descripcion": "El ingreso o item está parcialmente completado"
    },
    {
        "estado": "MERMA",
        "descripcion": "El item presenta merma o pérdida en el inventario"
    },
    {
        "estado": "INCOMPLETO POR FALLA",
        "descripcion": "El item está incompleto debido a una falla o defecto"
    },
    {
        "estado": "OTRO EXPLIQUE",
        "descripcion": "Otro estado que requiere explicación adicional en observaciones"
    },
    {
        "estado": "AJUSTE",
        "descripcion": "El item requiere ajuste de inventario"
    },
    {
        "estado": "SE REGRESA AL PROVEEDOR",
        "descripcion": "El item será devuelto al proveedor por algún motivo"
    }
]


def verificar_conexion():
    """Verificar que la conexión a la base de datos funcione"""
    try:
        with engine.connect() as conn:
            logger.info("✅ Conexión a la base de datos exitosa")
            return True
    except Exception as e:
        logger.error(f"❌ Error al conectar a la base de datos: {str(e)}")
        return False


def poblar_estados_items(db: Session):
    """Poblar la tabla estado_items con los estados iniciales"""
    logger.info("=" * 60)
    logger.info("🌱 INICIANDO POBLADO DE ESTADOS DE ITEMS")
    logger.info("=" * 60)
    
    estados_creados = 0
    estados_existentes = 0
    estados_error = 0
    
    for estado_data in ESTADOS_INICIALES:
        nombre_estado = estado_data["estado"]
        descripcion = estado_data["descripcion"]
        
        logger.info(f" Verificando estado: '{nombre_estado}'")
        
        # Verificar si el estado ya existe
        estado_existente = db.query(EstadoItems).filter(
            EstadoItems.estado == nombre_estado
        ).first()
        
        if estado_existente:
            logger.info(f"   ️ El estado '{nombre_estado}' YA existe (ID={estado_existente.id})")
            estados_existentes += 1
            continue
        
        # Crear el estado
        try:
            nuevo_estado = EstadoItems(
                estado=nombre_estado,
                descripcion=descripcion,
                activo=True
            )
            
            db.add(nuevo_estado)
            db.commit()
            db.refresh(nuevo_estado)
            
            logger.info(f"   ✅ Estado '{nombre_estado}' creado exitosamente (ID={nuevo_estado.id})")
            estados_creados += 1
            
        except IntegrityError as e:
            db.rollback()
            logger.error(f"   ❌ Error de integridad al crear '{nombre_estado}': {str(e)}")
            estados_error += 1
        except Exception as e:
            db.rollback()
            logger.error(f"   ❌ Error al crear '{nombre_estado}': {str(e)}")
            estados_error += 1
    
    # Resumen final
    logger.info("=" * 60)
    logger.info("📊 RESUMEN DE POBLADO")
    logger.info("=" * 60)
    logger.info(f"   ✅ Estados creados: {estados_creados}")
    logger.info(f"   ⚠️ Estados existentes: {estados_existentes}")
    logger.info(f"   ❌ Errores: {estados_error}")
    logger.info(f"    Total procesados: {len(ESTADOS_INICIALES)}")
    logger.info("=" * 60)
    
    return estados_creados, estados_existentes, estados_error


def listar_estados_actuales(db: Session):
    """Listar todos los estados actuales en la base de datos"""
    logger.info("=" * 60)
    logger.info("📋 ESTADOS ACTUALES EN LA BASE DE DATOS")
    logger.info("=" * 60)
    
    estados = db.query(EstadoItems).order_by(EstadoItems.id).all()
    
    if not estados:
        logger.info("   ℹ️ No hay estados registrados en la base de datos")
        return
    
    for estado in estados:
        activo_str = "✅" if estado.activo else "❌"
        logger.info(f"   {activo_str} ID={estado.id} | '{estado.estado}' | {estado.descripcion}")
    
    logger.info(f"   📦 Total: {len(estados)} estados")
    logger.info("=" * 60)


def main():
    """Función principal del script"""
    logger.info("=" * 60)
    logger.info(" INICIANDO SCRIPT DE POBLADO (SEED)")
    logger.info("=" * 60)
    
    # Verificar conexión
    if not verificar_conexion():
        logger.error("❌ No se pudo conectar a la base de datos. Abortando.")
        sys.exit(1)
    
    # Crear sesión de base de datos
    db = SessionLocal()
    
    try:
        # Listar estados actuales antes del poblado
        listar_estados_actuales(db)
        
        # Poblar estados
        creados, existentes, errores = poblar_estados_items(db)
        
        # Listar estados después del poblado
        listar_estados_actuales(db)
        
        # Código de salida
        if errores > 0:
            logger.warning(f"⚠️ El script terminó con {errores} errores")
            sys.exit(1)
        else:
            logger.info("✅ Script de poblado completado exitosamente")
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"❌ Error inesperado: {str(e)}")
        sys.exit(1)
    finally:
        db.close()
        logger.info("🔒 Conexión a la base de datos cerrada")


if __name__ == "__main__":
    main()