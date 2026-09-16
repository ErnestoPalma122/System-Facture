# app/modules/inventario/services_inventario.py
"""
Servicios para módulo de inventario: Ingreso, Items, EstadoItems
Con debug detallado en cada operación
"""

from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.modules.inventario.models_inventario import (
    Ingreso, Items, EstadoItems, Estado_Ingreso
)
from app.modules.inventario.schemas_inventario import (
    ItemsCreate, ItemsUpdate,
    EstadoItemsCreate, EstadoItemsUpdate
)
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ===========================================================
# ESTADO ITEMS - SERVICIOS
# ===========================================================

def get_estado_item_by_id(db: Session, estado_id: int):
    """Obtener estado de item por ID"""
    logger.info(f"🔍 Buscando estado de item con ID: {estado_id}")
    estado = db.query(EstadoItems).filter(EstadoItems.id == estado_id).first()
    
    if estado:
        logger.info(f"✅ Estado encontrado: ID={estado.id}, Estado={estado.estado}")
    else:
        logger.warning(f"❌ Estado con ID {estado_id} NO encontrado")
    
    return estado


def get_estado_item_by_nombre(db: Session, estado: str):
    """Obtener estado de item por nombre"""
    logger.info(f"🔍 Buscando estado de item: {estado}")
    estado_item = db.query(EstadoItems).filter(EstadoItems.estado == estado).first()
    
    if estado_item:
        logger.info(f"✅ Estado encontrado: ID={estado_item.id}, Estado={estado_item.estado}")
    else:
        logger.info(f"ℹ️ No se encontró estado: {estado}")
    
    return estado_item


def get_estados_items(db: Session, skip: int = 0, limit: int = 100, activo: bool = None):
    """Obtener lista de estados de items"""
    logger.info(f"🔍 Obteniendo estados de items (skip={skip}, limit={limit})")
    
    query = db.query(EstadoItems)
    # Nota: Si tu modelo EstadoItems no tiene el campo 'activo', quita este filtro
    # if activo is not None:
    #     query = query.filter(EstadoItems.activo == activo)
    
    estados = query.offset(skip).limit(limit).all()
    logger.info(f"✅ Se encontraron {len(estados)} estados")
    return estados


def crear_estado_item(db: Session, estado: EstadoItemsCreate):
    """Crear nuevo estado de item"""
    logger.info("=" * 60)
    logger.info("🆕 INICIANDO CREACIÓN DE ESTADO DE ITEM")
    logger.info(f"📛 Estado: {estado.estado}")
    logger.info(f"📝 Observaciones: {estado.observaciones}")
    logger.info("=" * 60)
    
    # Verificar si ya existe
    estado_existente = get_estado_item_by_nombre(db, estado.estado)
    if estado_existente:
        logger.error(f"❌ ERROR: Ya existe un estado con nombre '{estado.estado}'")
        raise ValueError(f"Ya existe un estado con nombre '{estado.estado}'")
    
    db_estado = EstadoItems(
        estado=estado.estado,
        observaciones=estado.observaciones,  # ← CORREGIDO: coincide con el modelo
    )
    
    try:
        logger.info("💾 Guardando en base de datos...")
        db.add(db_estado)
        db.commit()
        db.refresh(db_estado)
        logger.info(f"✅ ESTADO DE ITEM CREADO EXITOSAMENTE: ID={db_estado.id}")
        return db_estado
    except IntegrityError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE INTEGRIDAD: {str(e)}")
        raise ValueError(f"Error de integridad: {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE BASE DE DATOS: {str(e)}")
        raise ValueError(f"Error de base de datos: {str(e)}")


def actualizar_estado_item(db: Session, estado_id: int, estado: EstadoItemsUpdate):
    """Actualizar estado de item existente"""
    logger.info("=" * 60)
    logger.info(f"🔄 INICIANDO ACTUALIZACIÓN DE ESTADO DE ITEM ID: {estado_id}")
    logger.info("=" * 60)
    
    db_estado = get_estado_item_by_id(db, estado_id)
    if not db_estado:
        logger.error(f"❌ ERROR: Estado con ID {estado_id} NO encontrado")
        return None
    
    logger.info(f"📊 Datos ANTES: Estado={db_estado.estado}")
    
    # ← CORREGIDO: .model_dump() es el estándar en Pydantic V2 (reemplaza a .dict())
    update_data = estado.model_dump(exclude_unset=True)
    logger.info(f"📝 Datos RECIBIDOS: {update_data}")
    
    # Si se cambia el nombre, verificar que no exista otro
    if 'estado' in update_data:
        estado_existente = get_estado_item_by_nombre(db, update_data['estado'])
        if estado_existente and estado_existente.id != estado_id:
            logger.error(f"❌ ERROR: Ya existe otro estado con nombre '{update_data['estado']}'")
            raise ValueError(f"Ya existe otro estado con nombre '{update_data['estado']}'")
    
    for field, value in update_data.items():
        setattr(db_estado, field, value)
        logger.info(f"   ✅ {field} actualizado")
    
    try:
        db.commit()
        db.refresh(db_estado)
        logger.info(f"✅ ESTADO DE ITEM ACTUALIZADO EXITOSAMENTE: ID={db_estado.id}")
        return db_estado
    except IntegrityError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE INTEGRIDAD: {str(e)}")
        raise ValueError(f"Error de integridad: {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE BASE DE DATOS: {str(e)}")
        raise ValueError(f"Error de base de datos: {str(e)}")


# ===========================================================
# ITEMS - SERVICIOS
# ===========================================================

def get_item_by_id(db: Session, item_id: int):
    """Obtener item por ID"""
    logger.info(f"🔍 Buscando item con ID: {item_id}")
    item = db.query(Items).filter(Items.id == item_id).first()
    
    if item:
        logger.info(f"✅ Item encontrado: ID={item.id}, Producto ID={item.producto_id}, Serie={item.serie}")
    else:
        logger.warning(f"❌ Item con ID {item_id} NO encontrado")
    
    return item


def get_items_by_ingreso(db: Session, ingreso_id: int):
    """Obtener todos los items de un ingreso"""
    logger.info(f"🔍 Buscando items del ingreso ID: {ingreso_id}")
    items = db.query(Items).filter(Items.ingreso_id == ingreso_id).all()
    
    logger.info(f"✅ Se encontraron {len(items)} items")
    return items


def get_items(db: Session, skip: int = 0, limit: int = 100, ingreso_id: int = None, producto_id: int = None, bodega_id: int = None):
    """Obtener lista de items con filtros"""
    logger.info(f"🔍 Obteniendo items (skip={skip}, limit={limit})")
    
    query = db.query(Items)
    
    if ingreso_id is not None:
        query = query.filter(Items.ingreso_id == ingreso_id)
        logger.info(f"🔎 Filtro aplicado: ingreso_id={ingreso_id}")
    
    if producto_id is not None:
        query = query.filter(Items.producto_id == producto_id)
        logger.info(f"🔎 Filtro aplicado: producto_id={producto_id}")
    
    if bodega_id is not None:
        query = query.filter(Items.bodega_id == bodega_id)
        logger.info(f"🔎 Filtro aplicado: bodega_id={bodega_id}")
    
    items = query.offset(skip).limit(limit).all()
    logger.info(f"✅ Se encontraron {len(items)} items")
    return items


def crear_item(db: Session, item: ItemsCreate):
    """Crear nuevo item"""
    logger.info("=" * 60)
    logger.info("🆕 INICIANDO CREACIÓN DE ITEM")
    logger.info(f"📦 Ingreso ID: {item.ingreso_id}")
    logger.info(f"📦 Producto ID: {item.producto_id}")
    logger.info(f"🏭 Bodega ID: {item.bodega_id}")
    logger.info(f"🔢 Serie: {item.serie}")
    logger.info(f"📦 Cantidad Inicial: {item.cantidad_inicial}")
    logger.info(f"📦 Cantidad Actual: {item.cantidad_actual}")
    logger.info("=" * 60)
    
    db_item = Items(
        ingreso_id=item.ingreso_id,
        producto_id=item.producto_id,
        bodega_id=item.bodega_id,
        estado_item_id=item.estado_item_id,
        serie=item.serie,
        dte=item.dte,
        dias_stock=item.dias_stock,
        cantidad_inicial=item.cantidad_inicial,  # ← AGREGADO: Control de granel
        cantidad_actual=item.cantidad_actual,    # ← AGREGADO: Control de granel
        activo=True
    )
    
    try:
        logger.info("💾 Guardando item en base de datos...")
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        logger.info(f"✅ ITEM CREADO EXITOSAMENTE: ID={db_item.id}")
        return db_item
    except IntegrityError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE INTEGRIDAD: {str(e)}")
        raise ValueError(f"Error de integridad: {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE BASE DE DATOS: {str(e)}")
        raise ValueError(f"Error de base de datos: {str(e)}")


def actualizar_item(db: Session, item_id: int, item: ItemsUpdate):
    """Actualizar item existente"""
    logger.info("=" * 60)
    logger.info(f"🔄 INICIANDO ACTUALIZACIÓN DE ITEM ID: {item_id}")
    logger.info("=" * 60)
    
    db_item = get_item_by_id(db, item_id)
    if not db_item:
        logger.error(f"❌ ERROR: Item con ID {item_id} NO encontrado")
        return None
    
    logger.info(f"📊 Datos ANTES:")
    logger.info(f"   - Producto ID: {db_item.producto_id}")
    logger.info(f"   - Bodega ID: {db_item.bodega_id}")
    logger.info(f"   - Serie: {db_item.serie}")
    
    # ← CORREGIDO: .model_dump() es el estándar en Pydantic V2
    update_data = item.model_dump(exclude_unset=True)
    logger.info(f"📝 Datos RECIBIDOS: {update_data}")
    
    for field, value in update_data.items():
        setattr(db_item, field, value)
        logger.info(f"   ✅ {field} actualizado")
    
    try:
        db.commit()
        db.refresh(db_item)
        logger.info(f"✅ ITEM ACTUALIZADO EXITOSAMENTE: ID={db_item.id}")
        return db_item
    except IntegrityError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE INTEGRIDAD: {str(e)}")
        raise ValueError(f"Error de integridad: {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE BASE DE DATOS: {str(e)}")
        raise ValueError(f"Error de base de datos: {str(e)}")


# ===========================================================
# ESTADO INGRESO - SERVICIOS
# ===========================================================

def get_estados_ingreso(db: Session):
    """Obtener lista de estados de ingreso"""
    logger.info("🔍 Obteniendo estados de ingreso")
    estados = db.query(Estado_Ingreso).filter(Estado_Ingreso.nombre_estado.isnot(None)).all()
    logger.info(f"✅ Se encontraron {len(estados)} estados de ingreso")
    return estados