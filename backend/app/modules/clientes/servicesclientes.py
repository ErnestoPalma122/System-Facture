# app/modules/clientes/servicesclientes.py
"""
Servicios para el módulo de clientes.
Contiene la lógica de negocio, interacción con la base de datos y logging detallado.
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.modules.clientes.modelsclientes import Cliente
from app.modules.clientes.schemasclientes import ClienteCreate, ClienteUpdate
import logging

# Configuración de logging para este módulo
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_cliente_by_id(db: Session, cliente_id: int) -> Cliente | None:
    """Obtiene un cliente por su ID"""
    logger.info(f"🔍 Buscando cliente con ID: {cliente_id}")
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    
    if cliente:
        logger.info(f"✅ Cliente encontrado: ID={cliente.id}, Nombre='{cliente.nombre}', Correo={cliente.correo}")
    else:
        logger.warning(f"❌ Cliente con ID {cliente_id} NO encontrado")
    return cliente


def get_cliente_by_correo(db: Session, correo: str) -> Cliente | None:
    """Obtiene un cliente por su correo electrónico (para validación de unicidad)"""
    logger.info(f"🔍 Buscando cliente con correo: {correo}")
    cliente = db.query(Cliente).filter(Cliente.correo == correo).first()
    
    if cliente:
        logger.info(f"⚠️ Cliente encontrado con ese correo: ID={cliente.id}")
    else:
        logger.info(f"ℹ️ No existe cliente con el correo: {correo}")
    return cliente


def get_clientes(db: Session, skip: int = 0, limit: int = 100, activo: bool | None = None, nombre: str | None = None) -> list[Cliente]:
    """Obtiene una lista de clientes con filtros opcionales de paginación, estado y nombre"""
    logger.info(f"📋 Obteniendo lista de clientes (skip={skip}, limit={limit}, activo={activo}, nombre='{nombre}')")
    
    query = db.query(Cliente)
    
    if activo is not None:
        query = query.filter(Cliente.activo == activo)
        logger.info(f"🔎 Filtro aplicado: activo={activo}")
        
    if nombre:
        # Búsqueda insensible a mayúsculas/minúsculas
        query = query.filter(Cliente.nombre.ilike(f"%{nombre}%") | Cliente.nombre_comercial.ilike(f"%{nombre}%"))
        logger.info(f"🔎 Filtro aplicado: nombre contiene '{nombre}'")
        
    clientes = query.offset(skip).limit(limit).all()
    logger.info(f"✅ Se encontraron {len(clientes)} clientes")
    return clientes


def crear_cliente(db: Session, cliente_data: ClienteCreate) -> Cliente:
    """Crea un nuevo cliente en la base de datos con validación de unicidad de correo"""
    logger.info("=" * 60)
    logger.info("🆕 INICIANDO CREACIÓN DE CLIENTE")
    logger.info(f"📧 Correo: {cliente_data.correo}")
    logger.info(f"👤 Nombre: {cliente_data.nombre or cliente_data.nombre_comercial}")
    logger.info("=" * 60)
    
    # 1. Validar que el correo no exista ya
    cliente_existente = get_cliente_by_correo(db, cliente_data.correo)
    if cliente_existente:
        logger.error(f"❌ ERROR: Ya existe un cliente registrado con el correo '{cliente_data.correo}'")
        raise ValueError(f"Ya existe un cliente registrado con el correo '{cliente_data.correo}'")
    
    # 2. Crear la instancia del modelo
    nuevo_cliente = Cliente(**cliente_data.model_dump(), activo=True)
    
    try:
        logger.info("💾 Guardando cliente en la base de datos...")
        db.add(nuevo_cliente)
        db.commit()
        db.refresh(nuevo_cliente)
        logger.info(f"✅ CLIENTE CREADO EXITOSAMENTE: ID={nuevo_cliente.id}")
        return nuevo_cliente
        
    except IntegrityError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE INTEGRIDAD (posible conflicto de datos únicos): {str(e)}")
        raise ValueError("Error de integridad: Los datos proporcionados violan una restricción de la base de datos.")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE BASE DE DATOS: {str(e)}")
        raise ValueError("Error interno de la base de datos al crear el cliente.")


def actualizar_cliente(db: Session, cliente_id: int, cliente_data: ClienteUpdate) -> Cliente | None:
    """Actualiza los datos de un cliente existente de forma dinámica"""
    logger.info("=" * 60)
    logger.info(f"🔄 INICIANDO ACTUALIZACIÓN DE CLIENTE ID: {cliente_id}")
    logger.info("=" * 60)
    
    cliente = get_cliente_by_id(db, cliente_id)
    if not cliente:
        return None
    
    # Extraer solo los campos que se enviaron en la petición (exclude_unset=True)
    update_data = cliente_data.model_dump(exclude_unset=True)
    logger.info(f"📝 Campos a actualizar: {list(update_data.keys())}")
    
    # Validación: Si se intenta cambiar el correo, verificar que no exista en otro cliente
    if 'correo' in update_data and update_data['correo'] != cliente.correo:
        cliente_con_nuevo_correo = get_cliente_by_correo(db, update_data['correo'])
        if cliente_con_nuevo_correo:
            logger.error(f"❌ ERROR: El correo '{update_data['correo']}' ya está en uso por otro cliente (ID={cliente_con_nuevo_correo.id})")
            raise ValueError(f"El correo '{update_data['correo']}' ya está en uso por otro cliente.")
    
    # Aplicar cambios dinámicamente
    for campo, valor in update_data.items():
        setattr(cliente, campo, valor)
        logger.info(f"   ✅ {campo} actualizado a: {valor}")
    
    try:
        logger.info("💾 Guardando cambios en la base de datos...")
        db.commit()
        db.refresh(cliente)
        logger.info(f"✅ CLIENTE ACTUALIZADO EXITOSAMENTE: ID={cliente.id}")
        return cliente
        
    except IntegrityError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE INTEGRIDAD al actualizar: {str(e)}")
        raise ValueError("Error de integridad al actualizar el cliente.")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE BASE DE DATOS al actualizar: {str(e)}")
        raise ValueError("Error interno de la base de datos al actualizar el cliente.")


def eliminar_cliente(db: Session, cliente_id: int) -> dict:
    """Realiza un 'Soft Delete' (desactivación lógica) del cliente"""
    logger.info("=" * 60)
    logger.info(f"🗑️ INICIANDO DESACTIVACIÓN (SOFT DELETE) DE CLIENTE ID: {cliente_id}")
    logger.info("=" * 60)
    
    cliente = get_cliente_by_id(db, cliente_id)
    if not cliente:
        raise ValueError(f"El cliente con ID {cliente_id} no existe.")
    
    if not cliente.activo:
        logger.warning(f"⚠️ El cliente ID={cliente_id} YA está desactivado")
        return {"cliente": cliente, "cambio_realizado": False, "mensaje": "El cliente ya está desactivado"}
    
    try:
        logger.info(f"🔄 Cambiando estado de ACTIVO a INACTIVO para el cliente ID={cliente_id}")
        cliente.activo = False
        db.commit()
        db.refresh(cliente)
        logger.info(f"✅ CLIENTE DESACTIVADO EXITOSAMENTE: ID={cliente.id}")
        return {
            "cliente": cliente,
            "cambio_realizado": True,
            "mensaje": f"Cliente '{cliente.nombre or cliente.nombre_comercial}' desactivado exitosamente"
        }
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE BASE DE DATOS al desactivar cliente: {str(e)}")
        raise ValueError("Error interno al intentar desactivar el cliente.")