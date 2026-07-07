# app/modules/proveedores/services_proveedor.py
"""
Servicios para módulo de proveedores
Con debug detallado en cada operación
"""

from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.modules.proveedores.models_proveedor import Proveedor
from app.modules.proveedores.schemas_proveedor import ProveedorCreate, ProveedorUpdate
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ===========================================================
# PROVEEDOR - SERVICIOS
# ===========================================================

def get_proveedor_by_id(db: Session, proveedor_id: int):
    """Obtener proveedor por ID"""
    logger.info(f"🔍 Buscando proveedor con ID: {proveedor_id}")
    proveedor = db.query(Proveedor).filter(Proveedor.id == proveedor_id).first()
    
    if proveedor:
        logger.info(f"✅ Proveedor encontrado: ID={proveedor.id}, Nombre={proveedor.nombre}, Email={proveedor.email}")
    else:
        logger.warning(f"❌ Proveedor con ID {proveedor_id} NO encontrado")
    
    return proveedor


def get_proveedor_by_nombre(db: Session, nombre: str):
    """Obtener proveedor por nombre"""
    logger.info(f"🔍 Buscando proveedor con nombre: {nombre}")
    proveedor = db.query(Proveedor).filter(Proveedor.nombre == nombre).first()
    
    if proveedor:
        logger.info(f"✅ Proveedor encontrado: ID={proveedor.id}, Nombre={proveedor.nombre}")
    else:
        logger.info(f"ℹ️ No se encontró proveedor con nombre: {nombre}")
    
    return proveedor


def get_proveedores(db: Session, skip: int = 0, limit: int = 100, activo: bool = None, nombre: str = None):
    """Obtener lista de proveedores con filtros opcionales"""
    logger.info(f"🔍 Obteniendo proveedores (skip={skip}, limit={limit}, activo={activo}, nombre={nombre})")
    
    query = db.query(Proveedor)
    
    if activo is not None:
        query = query.filter(Proveedor.activo == activo)
        logger.info(f"🔎 Filtro aplicado: activo={activo}")
    
    if nombre is not None:
        query = query.filter(Proveedor.nombre.ilike(f'%{nombre}%'))
        logger.info(f"🔎 Filtro aplicado: nombre contiene '{nombre}'")
    
    proveedores = query.offset(skip).limit(limit).all()
    logger.info(f"✅ Se encontraron {len(proveedores)} proveedores")
    
    # Mostrar detalle en logs
    for p in proveedores:
        logger.info(f"   📦 ID={p.id} | Nombre: {p.nombre} | Email: {p.email} | Activo: {p.activo}")
    
    return proveedores


def crear_proveedor(db: Session, proveedor: ProveedorCreate):
    """Crear nuevo proveedor"""
    logger.info("=" * 60)
    logger.info("🆕 INICIANDO CREACIÓN DE PROVEEDOR")
    logger.info(f"📛 Nombre: {proveedor.nombre}")
    logger.info(f"📧 Email: {proveedor.email}")
    logger.info(f"📍 Dirección: {proveedor.direccion}")
    logger.info(f"👤 Contacto: {proveedor.contacto}")
    logger.info(f"📞 Teléfono 1: {proveedor.telefono1}")
    logger.info(f"📞 Teléfono 2: {proveedor.telefono2}")
    logger.info(f"📝 Observaciones: {proveedor.observaciones}")
    logger.info("=" * 60)
    
    # Verificar si ya existe un proveedor con ese nombre
    proveedor_existente = get_proveedor_by_nombre(db, proveedor.nombre)
    if proveedor_existente:
        logger.error(f"❌ ERROR: Ya existe un proveedor con nombre '{proveedor.nombre}'")
        raise ValueError(f"Ya existe un proveedor con nombre '{proveedor.nombre}'")
    
    # Crear proveedor
    db_proveedor = Proveedor(
        nombre=proveedor.nombre,
        direccion=proveedor.direccion,
        contacto=proveedor.contacto,
        email=proveedor.email,
        telefono1=proveedor.telefono1,
        telefono2=proveedor.telefono2,
        observaciones=proveedor.observaciones,
        activo=True
    )
    
    try:
        logger.info("💾 Guardando proveedor en base de datos...")
        db.add(db_proveedor)
        db.commit()
        db.refresh(db_proveedor)
        logger.info(f"✅ PROVEEDOR CREADO EXITOSAMENTE: ID={db_proveedor.id}")
        logger.info(f"   - Nombre: {db_proveedor.nombre}")
        logger.info(f"   - Email: {db_proveedor.email}")
        logger.info(f"   - Contacto: {db_proveedor.contacto}")
        return db_proveedor
    except IntegrityError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE INTEGRIDAD: {str(e)}")
        raise ValueError(f"Error de integridad: {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE BASE DE DATOS: {str(e)}")
        raise ValueError(f"Error de base de datos: {str(e)}")


def actualizar_proveedor(db: Session, proveedor_id: int, proveedor: ProveedorUpdate):
    """Actualizar proveedor existente"""
    logger.info("=" * 60)
    logger.info(f"🔄 INICIANDO ACTUALIZACIÓN DE PROVEEDOR ID: {proveedor_id}")
    logger.info("=" * 60)
    
    db_proveedor = get_proveedor_by_id(db, proveedor_id)
    if not db_proveedor:
        logger.error(f"❌ ERROR: Proveedor con ID {proveedor_id} NO encontrado")
        return None
    
    logger.info(f"📊 Datos ANTES:")
    logger.info(f"   - Nombre: {db_proveedor.nombre}")
    logger.info(f"   - Email: {db_proveedor.email}")
    logger.info(f"   - Contacto: {db_proveedor.contacto}")
    logger.info(f"   - Activo: {db_proveedor.activo}")
    
    update_data = proveedor.dict(exclude_unset=True)
    logger.info(f"📝 Datos RECIBIDOS: {update_data}")
    
    # Si se cambia el nombre, verificar que no exista otro con ese nombre
    if 'nombre' in update_data:
        proveedor_existente = get_proveedor_by_nombre(db, update_data['nombre'])
        if proveedor_existente and proveedor_existente.id != proveedor_id:
            logger.error(f"❌ ERROR: Ya existe otro proveedor con nombre '{update_data['nombre']}'")
            raise ValueError(f"Ya existe otro proveedor con nombre '{update_data['nombre']}'")
    
    for field, value in update_data.items():
        setattr(db_proveedor, field, value)
        logger.info(f"   ✅ {field} actualizado")
    
    try:
        db.commit()
        db.refresh(db_proveedor)
        logger.info(f"✅ PROVEEDOR ACTUALIZADO EXITOSAMENTE: ID={db_proveedor.id}")
        logger.info(f"   - Nombre: {db_proveedor.nombre}")
        logger.info(f"   - Email: {db_proveedor.email}")
        return db_proveedor
    except IntegrityError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE INTEGRIDAD: {str(e)}")
        raise ValueError(f"Error de integridad: {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE BASE DE DATOS: {str(e)}")
        raise ValueError(f"Error de base de datos: {str(e)}")


def eliminar_proveedor(db: Session, proveedor_id: int):
    """Eliminar proveedor (soft delete)"""
    logger.info("=" * 60)
    logger.info(f"🗑️ INICIANDO ELIMINACIÓN DE PROVEEDOR ID: {proveedor_id}")
    logger.info("=" * 60)
    
    db_proveedor = get_proveedor_by_id(db, proveedor_id)
    if not db_proveedor:
        logger.error(f"❌ ERROR: Proveedor con ID {proveedor_id} NO encontrado")
        return None
    
    logger.info(f"📊 Proveedor a eliminar:")
    logger.info(f"   - ID: {db_proveedor.id}")
    logger.info(f"   - Nombre: {db_proveedor.nombre}")
    logger.info(f"   - Email: {db_proveedor.email}")
    logger.info(f"   - Activo: {db_proveedor.activo}")
    
    if not db_proveedor.activo:
        logger.warning(f"⚠️ Proveedor ID={proveedor_id} YA está desactivado")
        return {
            "proveedor": db_proveedor,
            "cambio_realizado": False,
            "mensaje": "El proveedor ya está desactivado"
        }
    
    try:
        db_proveedor.activo = False
        db.commit()
        db.refresh(db_proveedor)
        logger.info(f"✅ PROVEEDOR ELIMINADO EXITOSAMENTE: ID={db_proveedor.id}")
        return {
            "proveedor": db_proveedor,
            "cambio_realizado": True,
            "mensaje": f"Proveedor '{db_proveedor.nombre}' eliminado exitosamente"
        }
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"❌ ERROR al eliminar proveedor: {str(e)}")
        raise ValueError(f"Error al eliminar proveedor: {str(e)}")