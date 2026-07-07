# app/modules/productos/routesproducto.py
"""
Endpoints para módulos de productos: Producto, Precio, Categoria, Stock, Bodega
Con protección JWT y debug detallado
"""

from typing import Optional
from fastapi import APIRouter, Depends, Request, status, HTTPException
from sqlalchemy.orm import Session
from app.core.rate_limiter import rate_limit
from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.modules.usuarios.models import Usuario
from app.modules.productos.schemasproducto import (
    ProductoCreate, ProductoUpdate, ProductoResponse, ProductoListResponse,
    CategoriaCreate, CategoriaUpdate, CategoriaResponse, CategoriaListResponse,
    BodegaCreate, BodegaUpdate, BodegaResponse, BodegaListResponse,
    StockCreate, StockUpdate, StockResponse, StockListResponse,
    PrecioUpdate, PrecioResponse,
    MessageResponse
)
from app.modules.productos.servicesproducto import (
    # Categoria
    get_categorias, get_categoria_by_id, crear_categoria, actualizar_categoria,
    # Bodega
    get_bodegas, get_bodega_by_id, crear_bodega, actualizar_bodega,
    # Stock
    get_stocks, get_stock_by_id, crear_stock, actualizar_stock,
    # Producto
    get_productos, get_producto_by_id, crear_producto, actualizar_producto, eliminar_producto,
    # Precio
    actualizar_precio
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/productos", tags=["Productos"])


# ===========================================================
# ENDPOINTS DE CATEGORÍAS
# ===========================================================

@router.get(
    "/categorias/listar",
    response_model=CategoriaListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(rate_limit(
        limit=settings.RATE_LIMIT_DEFAULT,
        window=settings.RATE_LIMIT_WINDOW,
        key_prefix="categorias_listar"
    ))],
    summary="Listar categorías",
    description="Obtiene una lista de todas las categorías. Requiere autenticación."
)
def listar_categorias(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    """Listar categorías con paginación"""
    logger.info("=" * 60)
    logger.info(f"📋 ENDPOINT: GET /productos/categorias/listar")
    logger.info(f"👤 Usuario autenticado: ID={current_user.id}")
    logger.info("=" * 60)
    
    categorias = get_categorias(db, skip=skip, limit=limit)
    logger.info(f"✅ Retornando {len(categorias)} categorías")
    
    return CategoriaListResponse(
        total=len(categorias),
        categorias=categorias
    )


@router.get(
    "/categorias/obtener/{categoria_id}",
    response_model=CategoriaResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(rate_limit(
        limit=settings.RATE_LIMIT_DEFAULT,
        window=settings.RATE_LIMIT_WINDOW,
        key_prefix="categorias_obtener"
    ))],
    summary="Obtener categoría por ID",
    description="Obtiene los detalles de una categoría específica."
)
def obtener_categoria(
    request: Request,
    categoria_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtener categoría por ID"""
    logger.info(f"📋 ENDPOINT: GET /productos/categorias/obtener/{categoria_id}")
    
    categoria = get_categoria_by_id(db, categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail=f"Categoría con ID {categoria_id} no encontrada")
    
    return categoria


@router.post(
    "/categorias/crear",
    response_model=CategoriaResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit(
        limit=10,
        window=60,
        key_prefix="categorias_crear"
    ))],
    summary="Crear categoría",
    description="Crea una nueva categoría. Solo administradores."
)
def crear_categoria_endpoint(
    request: Request,
    categoria: CategoriaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["SUPER_ADMIN", "ADMIN"]))
):
    """Crear nueva categoría"""
    logger.info(f"📋 ENDPOINT: POST /productos/categorias/crear")
    logger.info(f"👤 Creado por: ID={current_user.id}")
    
    try:
        db_categoria = crear_categoria(db, categoria)
        logger.info(f"✅ Categoría creada: ID={db_categoria.id}")
        return db_categoria
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put(
    "/categorias/actualizar/{categoria_id}",
    response_model=CategoriaResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(rate_limit(
        limit=20,
        window=60,
        key_prefix="categorias_actualizar"
    ))],
    summary="Actualizar categoría",
    description="Actualiza una categoría existente. Solo administradores."
)
def actualizar_categoria_endpoint(
    request: Request,
    categoria_id: int,
    categoria: CategoriaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["SUPER_ADMIN", "ADMIN"]))
):
    """Actualizar categoría"""
    logger.info(f"📋 ENDPOINT: PUT /productos/categorias/actualizar/{categoria_id}")
    
    try:
        db_categoria = actualizar_categoria(db, categoria_id, categoria)
        if not db_categoria:
            raise HTTPException(status_code=404, detail=f"Categoría con ID {categoria_id} no encontrada")
        return db_categoria
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ===========================================================
# ENDPOINTS DE BODEGAS
# ===========================================================

@router.get(
    "/bodegas/listar",
    response_model=BodegaListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(rate_limit(
        limit=settings.RATE_LIMIT_DEFAULT,
        window=settings.RATE_LIMIT_WINDOW,
        key_prefix="bodegas_listar"
    ))],
    summary="Listar bodegas",
    description="Obtiene una lista de todas las bodegas. Requiere autenticación."
)
def listar_bodegas(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    activo: Optional[bool] = None
):
    """Listar bodegas con filtros"""
    logger.info(f"📋 ENDPOINT: GET /productos/bodegas/listar")
    
    bodegas = get_bodegas(db, skip=skip, limit=limit, activo=activo)
    return BodegaListResponse(total=len(bodegas), bodegas=bodegas)


@router.get(
    "/bodegas/obtener/{bodega_id}",
    response_model=BodegaResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener bodega por ID"
)
def obtener_bodega(
    request: Request,
    bodega_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtener bodega por ID"""
    bodega = get_bodega_by_id(db, bodega_id)
    if not bodega:
        raise HTTPException(status_code=404, detail=f"Bodega con ID {bodega_id} no encontrada")
    return bodega


@router.post(
    "/bodegas/crear",
    response_model=BodegaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear bodega",
    description="Crea una nueva bodega. Solo administradores."
)
def crear_bodega_endpoint(
    request: Request,
    bodega: BodegaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["SUPER_ADMIN", "ADMIN"]))
):
    """Crear nueva bodega"""
    try:
        db_bodega = crear_bodega(db, bodega)
        return db_bodega
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put(
    "/bodegas/actualizar/{bodega_id}",
    response_model=BodegaResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar bodega"
)
def actualizar_bodega_endpoint(
    request: Request,
    bodega_id: int,
    bodega: BodegaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["SUPER_ADMIN", "ADMIN"]))
):
    """Actualizar bodega"""
    try:
        db_bodega = actualizar_bodega(db, bodega_id, bodega)
        if not db_bodega:
            raise HTTPException(status_code=404, detail=f"Bodega con ID {bodega_id} no encontrada")
        return db_bodega
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ===========================================================
# ENDPOINTS DE STOCKS
# ===========================================================

@router.get(
    "/stocks/listar",
    response_model=StockListResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar stocks",
    description="Obtiene lista de stocks con filtros opcionales por producto o bodega."
)
def listar_stocks(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    producto_id: Optional[int] = None,
    bodega_id: Optional[int] = None
):
    """Listar stocks con filtros"""
    stocks = get_stocks(db, skip=skip, limit=limit, producto_id=producto_id, bodega_id=bodega_id)
    return StockListResponse(total=len(stocks), stocks=stocks)


@router.get(
    "/stocks/obtener/{stock_id}",
    response_model=StockResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener stock por ID"
)
def obtener_stock(
    request: Request,
    stock_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtener stock por ID"""
    stock = get_stock_by_id(db, stock_id)
    if not stock:
        raise HTTPException(status_code=404, detail=f"Stock con ID {stock_id} no encontrado")
    return stock


@router.post(
    "/stocks/crear",
    response_model=StockResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear stock",
    description="Crea un nuevo registro de stock. Solo administradores."
)
def crear_stock_endpoint(
    request: Request,
    stock: StockCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["SUPER_ADMIN", "ADMIN"]))
):
    """Crear nuevo stock"""
    try:
        db_stock = crear_stock(db, stock)
        return db_stock
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put(
    "/stocks/actualizar/{stock_id}",
    response_model=StockResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar stock"
)
def actualizar_stock_endpoint(
    request: Request,
    stock_id: int,
    stock: StockUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["SUPER_ADMIN", "ADMIN"]))
):
    """Actualizar stock"""
    try:
        db_stock = actualizar_stock(db, stock_id, stock)
        if not db_stock:
            raise HTTPException(status_code=404, detail=f"Stock con ID {stock_id} no encontrado")
        return db_stock
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ===========================================================
# ENDPOINTS DE PRODUCTOS (con precio integrado)
# ===========================================================

@router.get(
    "/listar",
    response_model=ProductoListResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar productos",
    description="Obtiene lista de productos con filtros opcionales por categoría, tipo, código y nombre."
)
def listar_productos(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    categoria_id: Optional[int] = None,
    tipo: Optional[str] = None,
    activo: Optional[bool] = None,
    codigo: Optional[str] = None,      # ← NUEVO: Buscar por código
    nombre: Optional[str] = None       # ← NUEVO: Buscar por nombre
):
    """Listar productos con filtros múltiples (incluye búsqueda por código y nombre)"""
    logger.info("=" * 60)
    logger.info(f"📋 ENDPOINT: GET /productos/listar")
    logger.info(f"🔎 Filtros: categoria_id={categoria_id}, tipo={tipo}, activo={activo}, codigo={codigo}, nombre={nombre}")
    logger.info("=" * 60)
    
    productos = get_productos(
        db, 
        skip=skip, 
        limit=limit, 
        categoria_id=categoria_id, 
        tipo=tipo, 
        activo=activo,
        codigo=codigo,
        nombre=nombre
    )
    
    return ProductoListResponse(total=len(productos), productos=productos)


@router.get(
    "/obtener/{producto_id}",
    response_model=ProductoResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener producto por ID"
)
def obtener_producto(
    request: Request,
    producto_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtener producto por ID con precio y stocks"""
    producto = get_producto_by_id(db, producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail=f"Producto con ID {producto_id} no encontrado")
    return producto


@router.post(
    "/crear",
    response_model=ProductoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear producto con precio",
    description="Crea un nuevo producto junto con sus precios. Solo administradores."
)
def crear_producto_endpoint(
    request: Request,
    producto: ProductoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["SUPER_ADMIN", "ADMIN"]))
):
    """Crear producto con precio integrado"""
    logger.info(f" ENDPOINT: POST /productos/crear")
    logger.info(f"👤 Creado por: ID={current_user.id}")
    
    try:
        db_producto = crear_producto(db, producto)
        logger.info(f"✅ Producto creado: ID={db_producto.id}")
        return db_producto
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put(
    "/actualizar/{producto_id}",
    response_model=ProductoResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar producto"
)
def actualizar_producto_endpoint(
    request: Request,
    producto_id: int,
    producto: ProductoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["SUPER_ADMIN", "ADMIN"]))
):
    """Actualizar producto"""
    try:
        db_producto = actualizar_producto(db, producto_id, producto)
        if not db_producto:
            raise HTTPException(status_code=404, detail=f"Producto con ID {producto_id} no encontrado")
        return db_producto
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/eliminar/{producto_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Eliminar producto (soft delete)"
)
def eliminar_producto_endpoint(
    request: Request,
    producto_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["SUPER_ADMIN", "ADMIN"]))
):
    """Eliminar producto (soft delete)"""
    try:
        resultado = eliminar_producto(db, producto_id)
        if not resultado:
            raise HTTPException(status_code=404, detail=f"Producto con ID {producto_id} no encontrado")
        return MessageResponse(message=resultado["mensaje"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put(
    "/precio/actualizar/{producto_id}",
    response_model=PrecioResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar precio de producto"
)
def actualizar_precio_endpoint(
    request: Request,
    producto_id: int,
    precio: PrecioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["SUPER_ADMIN", "ADMIN"]))
):
    """Actualizar precio de un producto existente"""
    try:
        db_precio = actualizar_precio(db, producto_id, precio)
        if not db_precio:
            raise HTTPException(status_code=404, detail=f"No existe precio para producto ID {producto_id}")
        return db_precio
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))