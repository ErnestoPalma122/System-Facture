# app/modules/inventario/routes_inventario.py
"""
Endpoints para módulo de inventario: Ingreso, Items, EstadoItems
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
from app.modules.inventario.schemas_inventario import (
    IngresoCreate, IngresoUpdate, IngresoResponse, IngresoListResponse,
    ItemsCreate, ItemsUpdate, ItemsResponse, ItemsListResponse,
    EstadoItemsCreate, EstadoItemsUpdate, EstadoItemsResponse, EstadoItemsListResponse,
    MessageResponse
)
from app.modules.inventario.services_inventario import (
    # Ingreso
    get_ingresos, get_ingreso_by_id, crear_ingreso, actualizar_ingreso, eliminar_ingreso,
    # Items
    get_items, get_item_by_id, get_items_by_ingreso, crear_item, actualizar_item,
    # EstadoItems
    get_estados_items, get_estado_item_by_id, crear_estado_item, actualizar_estado_item
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/inventario", tags=["Inventario"])


# ===========================================================
# ENDPOINTS DE ESTADO ITEMS
# ===========================================================

@router.get(
    "/estados/listar",
    response_model=EstadoItemsListResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar estados de items",
    description="Obtiene lista de estados de items de inventario."
)
def listar_estados_items(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    activo: Optional[bool] = None
):
    """Listar estados de items"""
    logger.info(f"📋 ENDPOINT: GET /inventario/estados/listar")
    
    estados = get_estados_items(db, skip=skip, limit=limit, activo=activo)
    return EstadoItemsListResponse(total=len(estados), estados=estados)


@router.get(
    "/estados/obtener/{estado_id}",
    response_model=EstadoItemsResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener estado de item por ID"
)
def obtener_estado_item(
    request: Request,
    estado_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtener estado de item por ID"""
    estado = get_estado_item_by_id(db, estado_id)
    if not estado:
        raise HTTPException(status_code=404, detail=f"Estado con ID {estado_id} no encontrado")
    return estado


@router.post(
    "/estados/crear",
    response_model=EstadoItemsResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear estado de item",
    description="Crea un nuevo estado de item. Solo administradores."
)
def crear_estado_item_endpoint(
    request: Request,
    estado: EstadoItemsCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["SUPER_ADMIN", "ADMIN"]))
):
    """Crear estado de item"""
    try:
        db_estado = crear_estado_item(db, estado)
        return db_estado
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put(
    "/estados/actualizar/{estado_id}",
    response_model=EstadoItemsResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar estado de item"
)
def actualizar_estado_item_endpoint(
    request: Request,
    estado_id: int,
    estado: EstadoItemsUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["SUPER_ADMIN", "ADMIN"]))
):
    """Actualizar estado de item"""
    try:
        db_estado = actualizar_estado_item(db, estado_id, estado)
        if not db_estado:
            raise HTTPException(status_code=404, detail=f"Estado con ID {estado_id} no encontrado")
        return db_estado
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ===========================================================
# ENDPOINTS DE ITEMS
# ===========================================================

@router.get(
    "/items/listar",
    response_model=ItemsListResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar items",
    description="Obtiene lista de items con filtros opcionales."
)
def listar_items(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    ingreso_id: Optional[int] = None,
    producto_id: Optional[int] = None,
    bodega_id: Optional[int] = None
):
    """Listar items con filtros"""
    items = get_items(db, skip=skip, limit=limit, ingreso_id=ingreso_id, producto_id=producto_id, bodega_id=bodega_id)
    return ItemsListResponse(total=len(items), items=items)


@router.get(
    "/items/obtener/{item_id}",
    response_model=ItemsResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener item por ID"
)
def obtener_item(
    request: Request,
    item_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtener item por ID"""
    item = get_item_by_id(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Item con ID {item_id} no encontrado")
    return item


@router.get(
    "/items/por-ingreso/{ingreso_id}",
    response_model=ItemsListResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener items por ingreso"
)
def obtener_items_por_ingreso(
    request: Request,
    ingreso_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtener todos los items de un ingreso específico"""
    items = get_items_by_ingreso(db, ingreso_id)
    return ItemsListResponse(total=len(items), items=items)


@router.post(
    "/items/crear",
    response_model=ItemsResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear item",
    description="Crea un nuevo item. Solo administradores."
)
def crear_item_endpoint(
    request: Request,
    item: ItemsCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["SUPER_ADMIN", "ADMIN"]))
):
    """Crear item"""
    try:
        db_item = crear_item(db, item)
        return db_item
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put(
    "/items/actualizar/{item_id}",
    response_model=ItemsResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar item"
)
def actualizar_item_endpoint(
    request: Request,
    item_id: int,
    item: ItemsUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["SUPER_ADMIN", "ADMIN"]))
):
    """Actualizar item"""
    try:
        db_item = actualizar_item(db, item_id, item)
        if not db_item:
            raise HTTPException(status_code=404, detail=f"Item con ID {item_id} no encontrado")
        return db_item
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ===========================================================
# ENDPOINTS DE INGRESOS
# ===========================================================

@router.get(
    "/ingresos/listar",
    response_model=IngresoListResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar ingresos",
    description="Obtiene lista de ingresos con filtros opcionales."
)
def listar_ingresos(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    proveedor_id: Optional[int] = None,
    activo: Optional[bool] = None
):
    """Listar ingresos con filtros"""
    ingresos = get_ingresos(db, skip=skip, limit=limit, proveedor_id=proveedor_id, activo=activo)
    return IngresoListResponse(total=len(ingresos), ingresos=ingresos)


@router.get(
    "/ingresos/obtener/{ingreso_id}",
    response_model=IngresoResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener ingreso por ID"
)
def obtener_ingreso(
    request: Request,
    ingreso_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtener ingreso por ID con sus items"""
    ingreso = get_ingreso_by_id(db, ingreso_id)
    if not ingreso:
        raise HTTPException(status_code=404, detail=f"Ingreso con ID {ingreso_id} no encontrado")
    return ingreso


@router.post(
    "/ingresos/crear",
    response_model=IngresoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear ingreso con items",
    description="Crea un nuevo ingreso de inventario con sus items. Solo administradores."
)
def crear_ingreso_endpoint(
    request: Request,
    ingreso: IngresoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["SUPER_ADMIN", "ADMIN"]))
):
    """Crear ingreso con items"""
    logger.info(f"📋 ENDPOINT: POST /inventario/ingresos/crear")
    logger.info(f"👤 Creado por: ID={current_user.id}")
    
    try:
        db_ingreso = crear_ingreso(db, ingreso)
        logger.info(f"✅ Ingreso creado: ID={db_ingreso.id}")
        return db_ingreso
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put(
    "/ingresos/actualizar/{ingreso_id}",
    response_model=IngresoResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar ingreso"
)
def actualizar_ingreso_endpoint(
    request: Request,
    ingreso_id: int,
    ingreso: IngresoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["SUPER_ADMIN", "ADMIN"]))
):
    """Actualizar ingreso"""
    try:
        db_ingreso = actualizar_ingreso(db, ingreso_id, ingreso)
        if not db_ingreso:
            raise HTTPException(status_code=404, detail=f"Ingreso con ID {ingreso_id} no encontrado")
        return db_ingreso
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/ingresos/eliminar/{ingreso_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Eliminar ingreso (soft delete)"
)
def eliminar_ingreso_endpoint(
    request: Request,
    ingreso_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["SUPER_ADMIN", "ADMIN"]))
):
    """Eliminar ingreso (soft delete)"""
    try:
        resultado = eliminar_ingreso(db, ingreso_id)
        if not resultado:
            raise HTTPException(status_code=404, detail=f"Ingreso con ID {ingreso_id} no encontrado")
        return MessageResponse(message=resultado["mensaje"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))