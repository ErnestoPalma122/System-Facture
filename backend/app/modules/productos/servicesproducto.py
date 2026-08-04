#backend\app\modules\productos\servicesproducto.py

"""
Servicios para módulos de productos: Producto, Precio, Categoria, Stock, Bodega
Con debug detallado en cada operación
"""

from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.modules.productos.modelsproducto import (
    Producto, Categoria, Precio, Stock, Bodega, TipoProducto
)
from app.modules.productos.schemasproducto import (
    ProductoCreate, ProductoUpdate,
    CategoriaCreate, CategoriaUpdate,
    BodegaCreate, BodegaUpdate,
    StockCreate, StockUpdate,
    PrecioCreate, PrecioUpdate
)
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ===========================================================
# CATEGORIA - SERVICIOS
# ===========================================================

def get_categoria_by_id(db: Session, categoria_id: int):
    logger.info(f"🔍 Buscando categoría con ID: {categoria_id}")
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if categoria:
        logger.info(f"✅ Categoría encontrada: ID={categoria.id}, Nombre={categoria.nombre}")
    else:
        logger.warning(f"❌ Categoría con ID {categoria_id} NO encontrada")
    return categoria

def get_categoria_by_nombre(db: Session, nombre: str):
    logger.info(f"🔍 Buscando categoría con nombre: {nombre}")
    categoria = db.query(Categoria).filter(Categoria.nombre == nombre).first()
    if categoria:
        logger.info(f"✅ Categoría encontrada: ID={categoria.id}, Nombre={categoria.nombre}")
    else:
        logger.info(f"ℹ️ No se encontró categoría con nombre: {nombre}")
    return categoria

def get_categorias(db: Session, skip: int = 0, limit: int = 100):
    logger.info(f"🔍 Obteniendo categorías (skip={skip}, limit={limit})")
    categorias = db.query(Categoria).offset(skip).limit(limit).all()
    logger.info(f"✅ Se encontraron {len(categorias)} categorías")
    return categorias

def crear_categoria(db: Session, categoria: CategoriaCreate):
    logger.info("=" * 60)
    logger.info("🆕 INICIANDO CREACIÓN DE CATEGORÍA")
    logger.info(f"📁 Nombre: {categoria.nombre}")
    logger.info("=" * 60)
    
    db_categoria = get_categoria_by_nombre(db, categoria.nombre)
    if db_categoria:
        logger.error(f"❌ ERROR: La categoría '{categoria.nombre}' ya existe")
        raise ValueError(f"La categoría '{categoria.nombre}' ya existe")
    
    db_categoria = Categoria(nombre=categoria.nombre)
    try:
        logger.info("💾 Guardando en base de datos...")
        db.add(db_categoria)
        db.commit()
        db.refresh(db_categoria)
        logger.info(f"✅ CATEGORÍA CREADA EXITOSAMENTE: ID={db_categoria.id}")
        return db_categoria
    except IntegrityError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE INTEGRIDAD: {str(e)}")
        raise ValueError(f"Error de integridad: {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE BASE DE DATOS: {str(e)}")
        raise ValueError(f"Error de base de datos: {str(e)}")

def actualizar_categoria(db: Session, categoria_id: int, categoria: CategoriaUpdate):
    logger.info("=" * 60)
    logger.info(f"🔄 INICIANDO ACTUALIZACIÓN DE CATEGORÍA ID: {categoria_id}")
    logger.info("=" * 60)
    
    db_categoria = get_categoria_by_id(db, categoria_id)
    if not db_categoria:
        logger.error(f"❌ ERROR: Categoría con ID {categoria_id} NO encontrada")
        return None
    
    update_data = categoria.model_dump(exclude_unset=True)
    if 'nombre' in update_data:
        categoria_existente = get_categoria_by_nombre(db, update_data['nombre'])
        if categoria_existente and categoria_existente.id != categoria_id:
            logger.error(f"❌ ERROR: Ya existe otra categoría con nombre '{update_data['nombre']}'")
            raise ValueError(f"Ya existe otra categoría con nombre '{update_data['nombre']}'")
    
    for field, value in update_data.items():
        setattr(db_categoria, field, value)
    
    try:
        db.commit()
        db.refresh(db_categoria)
        logger.info(f"✅ CATEGORÍA ACTUALIZADA EXITOSAMENTE: ID={db_categoria.id}")
        return db_categoria
    except IntegrityError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE INTEGRIDAD: {str(e)}")
        raise ValueError(f"Error de integridad: {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE BASE DE DATOS: {str(e)}")
        raise ValueError(f"Error de base de datos: {str(e)}")


# ===========================================================
# BODEGA - SERVICIOS
# ===========================================================

def get_bodega_by_id(db: Session, bodega_id: int):
    logger.info(f"🔍 Buscando bodega con ID: {bodega_id}")
    bodega = db.query(Bodega).filter(Bodega.id == bodega_id).first()
    if bodega:
        logger.info(f"✅ Bodega encontrada: ID={bodega.id}, Nombre={bodega.nombre}")
    else:
        logger.warning(f"❌ Bodega con ID {bodega_id} NO encontrada")
    return bodega

def get_bodega_by_nombre(db: Session, nombre: str):
    logger.info(f"🔍 Buscando bodega con nombre: {nombre}")
    bodega = db.query(Bodega).filter(Bodega.nombre == nombre).first()
    if bodega:
        logger.info(f"✅ Bodega encontrada: ID={bodega.id}, Nombre={bodega.nombre}")
    else:
        logger.info(f"ℹ️ No se encontró bodega con nombre: {nombre}")
    return bodega

def get_bodegas(db: Session, skip: int = 0, limit: int = 100, activo: bool = None):
    logger.info(f"🔍 Obteniendo bodegas (skip={skip}, limit={limit}, activo={activo})")
    query = db.query(Bodega)
    if activo is not None:
        query = query.filter(Bodega.activo == activo)
    bodegas = query.offset(skip).limit(limit).all()
    logger.info(f"✅ Se encontraron {len(bodegas)} bodegas")
    return bodegas

def crear_bodega(db: Session, bodega: BodegaCreate):
    logger.info("=" * 60)
    logger.info("🆕 INICIANDO CREACIÓN DE BODEGA")
    logger.info(f"🏭 Nombre: {bodega.nombre}")
    logger.info("=" * 60)
    
    db_bodega = get_bodega_by_nombre(db, bodega.nombre)
    if db_bodega:
        logger.error(f"❌ ERROR: La bodega '{bodega.nombre}' ya existe")
        raise ValueError(f"La bodega '{bodega.nombre}' ya existe")
    
    db_bodega = Bodega(
        nombre=bodega.nombre,
        direccion=bodega.direccion,
        ubicacion=bodega.ubicacion,
        telefono=bodega.telefono,
        encargado_id=bodega.encargado_id,
        activo=True
    )
    try:
        logger.info("💾 Guardando en base de datos...")
        db.add(db_bodega)
        db.commit()
        db.refresh(db_bodega)
        logger.info(f"✅ BODEGA CREADA EXITOSAMENTE: ID={db_bodega.id}")
        return db_bodega
    except IntegrityError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE INTEGRIDAD: {str(e)}")
        raise ValueError(f"Error de integridad: {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE BASE DE DATOS: {str(e)}")
        raise ValueError(f"Error de base de datos: {str(e)}")

def actualizar_bodega(db: Session, bodega_id: int, bodega: BodegaUpdate):
    logger.info("=" * 60)
    logger.info(f"🔄 INICIANDO ACTUALIZACIÓN DE BODEGA ID: {bodega_id}")
    logger.info("=" * 60)
    
    db_bodega = get_bodega_by_id(db, bodega_id)
    if not db_bodega:
        logger.error(f"❌ ERROR: Bodega con ID {bodega_id} NO encontrada")
        return None
    
    update_data = bodega.model_dump(exclude_unset=True)
    if 'nombre' in update_data:
        bodega_existente = get_bodega_by_nombre(db, update_data['nombre'])
        if bodega_existente and bodega_existente.id != bodega_id:
            logger.error(f"❌ ERROR: Ya existe otra bodega con nombre '{update_data['nombre']}'")
            raise ValueError(f"Ya existe otra bodega con nombre '{update_data['nombre']}'")
    
    for field, value in update_data.items():
        setattr(db_bodega, field, value)
    
    try:
        db.commit()
        db.refresh(db_bodega)
        logger.info(f"✅ BODEGA ACTUALIZADA EXITOSAMENTE: ID={db_bodega.id}")
        return db_bodega
    except IntegrityError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE INTEGRIDAD: {str(e)}")
        raise ValueError(f"Error de integridad: {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE BASE DE DATOS: {str(e)}")
        raise ValueError(f"Error de base de datos: {str(e)}")


# ===========================================================
# PRECIO - SERVICIOS
# ===========================================================

def get_precio_by_producto_id(db: Session, producto_id: int):
    logger.info(f"🔍 Buscando precio para producto ID: {producto_id}")
    precio = db.query(Precio).filter(Precio.producto_id == producto_id).first()
    if precio:
        logger.info(f"✅ Precio encontrado: ID={precio.id}, Producto ID={precio.producto_id}")
    else:
        logger.info(f"ℹ️ No se encontró precio para producto ID: {producto_id}")
    return precio

def crear_precio(db: Session, precio: PrecioCreate, producto_id: int):
    logger.info("=" * 60)
    logger.info(f"💰 INICIANDO CREACIÓN DE PRECIO para producto ID: {producto_id}")
    logger.info("=" * 60)
    
    precio_existente = get_precio_by_producto_id(db, producto_id)
    if precio_existente:
        logger.error(f"❌ ERROR: Ya existe precio para producto ID {producto_id}")
        raise ValueError(f"Ya existe precio para producto ID {producto_id}")
    
    db_precio = Precio(
        producto_id=producto_id,
        precio_base=precio.precio_base,
        precio_costo=precio.precio_costo,
        precio_publico=precio.precio_publico,
        precio_iva=precio.precio_iva,
        precio_promo=precio.precio_promo or 0,
        precio_descuento=precio.precio_descuento or 0,
        activo=True
    )
    try:
        logger.info("💾 Guardando precio en base de datos...")
        db.add(db_precio)
        db.commit()
        db.refresh(db_precio)
        logger.info(f"✅ PRECIO CREADO EXITOSAMENTE: ID={db_precio.id}")
        return db_precio
    except IntegrityError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE INTEGRIDAD: {str(e)}")
        raise ValueError(f"Error de integridad: {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE BASE DE DATOS: {str(e)}")
        raise ValueError(f"Error de base de datos: {str(e)}")

def actualizar_precio(db: Session, producto_id: int, precio: PrecioUpdate):
    logger.info("=" * 60)
    logger.info(f"💰 INICIANDO ACTUALIZACIÓN DE PRECIO para producto ID: {producto_id}")
    logger.info("=" * 60)
    
    db_precio = get_precio_by_producto_id(db, producto_id)
    if not db_precio:
        logger.error(f"❌ ERROR: No existe precio para producto ID {producto_id}")
        return None
    
    update_data = precio.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_precio, field, value)
    
    try:
        db.commit()
        db.refresh(db_precio)
        logger.info(f"✅ PRECIO ACTUALIZADO EXITOSAMENTE: ID={db_precio.id}")
        return db_precio
    except IntegrityError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE INTEGRIDAD: {str(e)}")
        raise ValueError(f"Error de integridad: {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE BASE DE DATOS: {str(e)}")
        raise ValueError(f"Error de base de datos: {str(e)}")


# ===========================================================
# STOCK - SERVICIOS
# ===========================================================

def get_stock_by_id(db: Session, stock_id: int):
    logger.info(f"🔍 Buscando stock con ID: {stock_id}")
    stock = db.query(Stock).filter(Stock.id == stock_id).first()
    if stock:
        logger.info(f"✅ Stock encontrado: ID={stock.id}, Producto ID={stock.producto_id}, Cantidad={stock.cantidad}")
    else:
        logger.warning(f"❌ Stock con ID {stock_id} NO encontrado")
    return stock

def get_stock_by_producto_bodega(db: Session, producto_id: int, bodega_id: int):
    logger.info(f"🔍 Buscando stock para producto ID={producto_id} en bodega ID={bodega_id}")
    stock = db.query(Stock).filter(
        Stock.producto_id == producto_id,
        Stock.bodega_id == bodega_id
    ).first()
    if stock:
        logger.info(f"✅ Stock encontrado: ID={stock.id}, Cantidad={stock.cantidad}")
    else:
        logger.info(f"ℹ️ No se encontró stock para producto ID={producto_id} en bodega ID={bodega_id}")
    return stock

def get_stocks(db: Session, skip: int = 0, limit: int = 100, producto_id: int = None, bodega_id: int = None):
    logger.info(f"📦 Obteniendo stocks (skip={skip}, limit={limit})")
    query = db.query(Stock)
    if producto_id is not None:
        query = query.filter(Stock.producto_id == producto_id)
    if bodega_id is not None:
        query = query.filter(Stock.bodega_id == bodega_id)
    stocks = query.offset(skip).limit(limit).all()
    logger.info(f"✅ Se encontraron {len(stocks)} stocks")
    return stocks

def crear_stock(db: Session, stock: StockCreate):
    logger.info("=" * 60)
    logger.info("📦 INICIANDO CREACIÓN DE STOCK")
    logger.info(f"📦 Producto ID: {stock.producto_id}")
    logger.info(f"🏭 Bodega ID: {stock.bodega_id}")
    logger.info(f"🔢 Cantidad: {stock.cantidad}")
    logger.info("=" * 60)
    
    stock_existente = get_stock_by_producto_bodega(db, stock.producto_id, stock.bodega_id)
    if stock_existente:
        logger.error(f"❌ ERROR: Ya existe stock para producto ID {stock.producto_id} en bodega ID {stock.bodega_id}")
        raise ValueError(f"Ya existe stock para producto ID {stock.producto_id} en bodega ID {stock.bodega_id}")
    
    db_stock = Stock(
        producto_id=stock.producto_id,
        bodega_id=stock.bodega_id,
        cantidad=stock.cantidad,
        cantidad_minima=stock.cantidad_minima,
        activo=True
    )
    try:
        logger.info("💾 Guardando stock en base de datos...")
        db.add(db_stock)
        db.commit()
        db.refresh(db_stock)
        logger.info(f"✅ STOCK CREADO EXITOSAMENTE: ID={db_stock.id}")
        return db_stock
    except IntegrityError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE INTEGRIDAD: {str(e)}")
        raise ValueError(f"Error de integridad: {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE BASE DE DATOS: {str(e)}")
        raise ValueError(f"Error de base de datos: {str(e)}")

def actualizar_stock(db: Session, stock_id: int, stock: StockUpdate):
    logger.info("=" * 60)
    logger.info(f"📦 INICIANDO ACTUALIZACIÓN DE STOCK ID: {stock_id}")
    logger.info("=" * 60)
    
    db_stock = get_stock_by_id(db, stock_id)
    if not db_stock:
        logger.error(f"❌ ERROR: Stock con ID {stock_id} NO encontrado")
        return None
    
    update_data = stock.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_stock, field, value)
    
    try:
        db.commit()
        db.refresh(db_stock)
        logger.info(f"✅ STOCK ACTUALIZADO EXITOSAMENTE: ID={db_stock.id}")
        return db_stock
    except IntegrityError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE INTEGRIDAD: {str(e)}")
        raise ValueError(f"Error de integridad: {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE BASE DE DATOS: {str(e)}")
        raise ValueError(f"Error de base de datos: {str(e)}")


# ===========================================================
# PRODUCTO - SERVICIOS (CON CÓDIGO Y BÚSQUEDAS)
# ===========================================================

def get_producto_by_id(db: Session, producto_id: int):
    logger.info(f"🔍 Buscando producto con ID: {producto_id}")
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if producto:
        logger.info(f"✅ Producto encontrado: ID={producto.id}, Código={producto.codigo}, Nombre={producto.nombre}")
    else:
        logger.warning(f"❌ Producto con ID {producto_id} NO encontrado")
    return producto

def get_producto_by_codigo(db: Session, codigo: str):
    logger.info(f"🔍 Buscando producto con código: {codigo}")
    producto = db.query(Producto).filter(Producto.codigo == codigo).first()
    if producto:
        logger.info(f"✅ Producto encontrado: ID={producto.id}, Código={producto.codigo}, Nombre={producto.nombre}")
    else:
        logger.info(f"ℹ️ No se encontró producto con código: {codigo}")
    return producto

def get_producto_by_nombre(db: Session, nombre: str):
    logger.info(f"🔍 Buscando producto con nombre exacto: {nombre}")
    producto = db.query(Producto).filter(Producto.nombre == nombre).first()
    if producto:
        logger.info(f"✅ Producto encontrado: ID={producto.id}, Código={producto.codigo}, Nombre={producto.nombre}")
    else:
        logger.info(f"ℹ️ No se encontró producto con nombre: {nombre}")
    return producto

def get_productos(db: Session, skip: int = 0, limit: int = 100, 
                  categoria_id: int = None, tipo: str = None, 
                  activo: bool = None, codigo: str = None, nombre: str = None):
    logger.info(f"🔍 Obteniendo productos (skip={skip}, limit={limit})")
    logger.info(f"🔎 Filtros recibidos: categoria_id={categoria_id}, tipo={tipo}, activo={activo}, codigo={codigo}, nombre={nombre}")
    
    query = db.query(Producto)
    
    if categoria_id is not None:
        query = query.filter(Producto.categoria_id == categoria_id)
    if tipo is not None:
        query = query.filter(Producto.tipo == tipo)
    if activo is not None:
        query = query.filter(Producto.activo == activo)
    if codigo is not None:
        query = query.filter(Producto.codigo.ilike(f'%{codigo}%'))
    if nombre is not None:
        query = query.filter(Producto.nombre.ilike(f'%{nombre}%'))
    
    productos = query.offset(skip).limit(limit).all()
    logger.info(f"✅ Se encontraron {len(productos)} productos")
    return productos

def crear_producto(db: Session, producto: ProductoCreate):
    logger.info("=" * 60)
    logger.info("🆕 INICIANDO CREACIÓN DE PRODUCTO")
    logger.info(f"🏷️ Código: {producto.codigo}")
    logger.info(f"📦 Nombre: {producto.nombre}")
    logger.info(f"📝 Descripción: {producto.descripcion}")
    logger.info(f"🏭 Marca: {producto.marca}")
    logger.info(f"📦 Tipo: {producto.tipo}")
    logger.info(f"📁 Categoría ID: {producto.categoria_id}")
    logger.info("=" * 60)
    
    # VALIDACIÓN 1: Verificar si el código ya existe
    producto_existente_codigo = get_producto_by_codigo(db, producto.codigo)
    if producto_existente_codigo:
        logger.error(f"❌ ERROR: Ya existe un producto con código '{producto.codigo}'")
        raise ValueError(f"Ya existe un producto con código '{producto.codigo}'")
    
    # VALIDACIÓN 2: Verificar si el nombre ya existe
    producto_existente_nombre = get_producto_by_nombre(db, producto.nombre)
    if producto_existente_nombre:
        logger.error(f"❌ ERROR: Ya existe un producto con nombre '{producto.nombre}'")
        raise ValueError(f"Ya existe un producto con nombre '{producto.nombre}'")
    
    # Crear producto
    db_producto = Producto(
        codigo=producto.codigo,
        nombre=producto.nombre,
        descripcion=producto.descripcion,
        marca=producto.marca,
        tipo=producto.tipo.value if hasattr(producto.tipo, 'value') else producto.tipo,
        categoria_id=producto.categoria_id,
        activo=True
    )
    
    try:
        logger.info("💾 Guardando producto en base de datos...")
        db.add(db_producto)
        db.commit()
        db.refresh(db_producto)
        logger.info(f"✅ PRODUCTO CREADO EXITOSAMENTE: ID={db_producto.id}, Código={db_producto.codigo}, Nombre={db_producto.nombre}")
        
        # Crear precio asociado
        logger.info("💰 Creando precio asociado al producto...")
        db_precio = crear_precio(db, producto.precio, db_producto.id)
        
        logger.info(f"✅ PRODUCTO Y PRECIO CREADOS EXITOSAMENTE")
        logger.info(f"   - Producto ID: {db_producto.id}")
        logger.info(f"   - Código: {db_producto.codigo}")
        logger.info(f"   - Nombre: {db_producto.nombre}")
        logger.info(f"   - Precio ID: {db_precio.id}")
        
        db.refresh(db_producto)
        return db_producto
        
    except IntegrityError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE INTEGRIDAD: {str(e)}")
        raise ValueError(f"Error de integridad: {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE BASE DE DATOS: {str(e)}")
        raise ValueError(f"Error de base de datos: {str(e)}")

# ... (funciones anteriores se mantienen igual)

def actualizar_producto(db: Session, producto_id: int, producto: ProductoUpdate):
    # DOCUMENTACIÓN: Actualiza un producto existente, incluyendo su cabecera y sus precios asociados en una sola transacción.
    logger.info("=" * 60)
    logger.info(f"🔄 INICIANDO ACTUALIZACIÓN DE PRODUCTO ID: {producto_id}")
    logger.info("=" * 60)
    
    db_producto = get_producto_by_id(db, producto_id)
    if not db_producto:
        logger.error(f"❌ ERROR: Producto con ID {producto_id} NO encontrado")
        return None
    
    update_data = producto.model_dump(exclude_unset=True)
    
    # VALIDACIÓN: Si se cambia el código, verificar que no exista otro con ese código
    if 'codigo' in update_data:
        producto_existente = get_producto_by_codigo(db, update_data['codigo'])
        if producto_existente and producto_existente.id != producto_id:
            logger.error(f"❌ ERROR: Ya existe otro producto con código '{update_data['codigo']}'")
            raise ValueError(f"Ya existe otro producto con código '{update_data['codigo']}'")
    
    # VALIDACIÓN: Si se cambia el nombre, verificar que no exista otro con ese nombre
    if 'nombre' in update_data:
        producto_existente = get_producto_by_nombre(db, update_data['nombre'])
        if producto_existente and producto_existente.id != producto_id:
            logger.error(f"❌ ERROR: Ya existe otro producto con nombre '{update_data['nombre']}'")
            raise ValueError(f"Ya existe otro producto con nombre '{update_data['nombre']}'")
    
    # ✅ CORRECCIÓN: Extraer los datos de precio del payload para manejarlos por separado
    precio_data = update_data.pop('precio', None)
    
    # Actualizar campos de la cabecera del producto
    for field, value in update_data.items():
        if field == 'tipo' and hasattr(value, 'value'):
            value = value.value
        setattr(db_producto, field, value)
    
    # ✅ CORRECCIÓN: Actualizar precios asociados si se proporcionaron en la petición
    if precio_data:
        logger.info("💰 Actualizando precios asociados...")
        db_precio = get_precio_by_producto_id(db, producto_id)
        if db_precio:
            for field, value in precio_data.items():
                if value is not None: # Solo actualizamos los campos que vienen explícitamente
                    setattr(db_precio, field, value)
            logger.info("✅ Precios actualizados en memoria")
        else:
            logger.warning("⚠️ No se encontró precio existente, creando uno nuevo...")
            db_precio = Precio(producto_id=producto_id, **precio_data, activo=True)
            db.add(db_precio)

    try:
        db.commit()
        db.refresh(db_producto)
        logger.info(f"✅ PRODUCTO ACTUALIZADO EXITOSAMENTE: ID={db_producto.id}")
        logger.info(f"   - Código: {db_producto.codigo}")
        logger.info(f"   - Nombre: {db_producto.nombre}")
        return db_producto
    except IntegrityError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE INTEGRIDAD: {str(e)}")
        raise ValueError(f"Error de integridad: {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE BASE DE DATOS: {str(e)}")
        raise ValueError(f"Error de base de datos: {str(e)}")

# ... (el resto del archivo se mantiene igual)

def eliminar_producto(db: Session, producto_id: int):
    logger.info("=" * 60)
    logger.info(f"🗑️ INICIANDO ELIMINACIÓN DE PRODUCTO ID: {producto_id}")
    logger.info("=" * 60)
    
    db_producto = get_producto_by_id(db, producto_id)
    if not db_producto:
        logger.error(f"❌ ERROR: Producto con ID {producto_id} NO encontrado")
        return None
    
    if not db_producto.activo:
        logger.warning(f"⚠️ Producto ID={producto_id} YA está desactivado")
        return {
            "producto": db_producto,
            "cambio_realizado": False,
            "mensaje": "El producto ya está desactivado"
        }
    
    try:
        db_producto.activo = False
        db.commit()
        db.refresh(db_producto)
        logger.info(f"✅ PRODUCTO ELIMINADO EXITOSAMENTE: ID={db_producto.id}")
        return {
            "producto": db_producto,
            "cambio_realizado": True,
            "mensaje": f"Producto '{db_producto.nombre}' (Código: {db_producto.codigo}) eliminado exitosamente"
        }
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"❌ ERROR al eliminar producto: {str(e)}")
        raise ValueError(f"Error al eliminar producto: {str(e)}")