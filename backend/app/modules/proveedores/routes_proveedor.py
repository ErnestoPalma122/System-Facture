# app/modules/proveedores/routes_proveedor.py
"""
Endpoints para módulo de proveedores
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
from app.modules.proveedores.schemas_proveedor import (
    ProveedorCreate, ProveedorUpdate, ProveedorResponse, ProveedorListResponse, MessageResponse
)
from app.modules.proveedores.services_proveedor import (
    get_proveedores, get_proveedor_by_id, crear_proveedor, actualizar_proveedor, eliminar_proveedor
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/proveedores", tags=["Proveedores"])


# ===========================================================
# ENDPOINTS DE PROVEEDORES (PROTEGIDOS CON JWT)
# ===========================================================
#el enpont se espesializa en listar los probeedores
@router.get(
    "/listar",
    #Llama a ProveedorListResponse de Shemas lo que hace que responda de una maera explicita.
    response_model=ProveedorListResponse,
    #Responde con un codigo HTTP de ok que es 200
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(rate_limit(
        limit=settings.RATE_LIMIT_DEFAULT,
        window=settings.RATE_LIMIT_WINDOW,
        key_prefix="proveedores_listar"
    ))],
    summary="Listar proveedores",
    description="Obtiene una lista de todos los proveedores. Requiere autenticación."
)
def listar_proveedores(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    activo: Optional[bool] = None,
    nombre: Optional[str] = None
):
    """
    Listar proveedores con filtros opcionales.
    
    Parámetros de filtro:
    - activo: true/false (opcional)
    - nombre: búsqueda parcial por nombre (opcional)
    """
    logger.info("=" * 60)
    logger.info(f"📋 ENDPOINT: GET /proveedores/listar")
    logger.info(f"👤 Usuario autenticado: ID={current_user.id}, Email={current_user.email}")
    logger.info(f"🔎 Filtros: activo={activo}, nombre={nombre}")
    logger.info("=" * 60)
    
    proveedores = get_proveedores(db, skip=skip, limit=limit, activo=activo, nombre=nombre)
    logger.info(f"✅ Retornando {len(proveedores)} proveedores")
    
    return ProveedorListResponse(
        total=len(proveedores),
        proveedores=proveedores
    )


@router.get(
    "/obtener/{proveedor_id}",
    response_model=ProveedorResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(rate_limit(
        limit=settings.RATE_LIMIT_DEFAULT,
        window=settings.RATE_LIMIT_WINDOW,
        key_prefix="proveedores_obtener"
    ))],
    summary="Obtener proveedor por ID",
    description="Obtiene los detalles de un proveedor específico por su ID."
)
def obtener_proveedor(
    request: Request,
    proveedor_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtener proveedor por ID"""
    logger.info(f"📋 ENDPOINT: GET /proveedores/obtener/{proveedor_id}")
    logger.info(f"👤 Usuario autenticado: ID={current_user.id}")
    
    proveedor = get_proveedor_by_id(db, proveedor_id)
    
    if not proveedor:
        logger.error(f"❌ Proveedor ID={proveedor_id} NO encontrado")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proveedor con ID {proveedor_id} no encontrado"
        )
    
    logger.info(f"✅ Retornando proveedor ID={proveedor.id}, Nombre={proveedor.nombre}")
    return proveedor


@router.post(
    "/crear",
    response_model=ProveedorResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit(
        limit=10,
        window=60,
        key_prefix="proveedores_crear",
        error_message="Demasiadas solicitudes de creación de proveedores. Espera 1 minuto."
    ))],
    summary="Crear proveedor",
    description="Crea un nuevo proveedor en el sistema. Solo administradores."
)
def crear_proveedor_endpoint(
    request: Request,
    proveedor: ProveedorCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["SUPER_ADMIN", "ADMIN"]))
):
    """
    Crear nuevo proveedor.
    
    Rate limit: 10 creaciones por minuto.
    Protección: Solo SUPER_ADMIN o ADMIN.
    """
    logger.info(f"📋 ENDPOINT: POST /proveedores/crear")
    logger.info(f"👤 Creado por: ID={current_user.id}, Email={current_user.email}")
    logger.info(f"📛 Nombre del proveedor: {proveedor.nombre}")
    
    try:
        db_proveedor = crear_proveedor(db, proveedor)
        logger.info(f"✅ Proveedor creado: ID={db_proveedor.id}")
        return db_proveedor
    except ValueError as e:
        logger.error(f"❌ Error al crear proveedor: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put(
    "/actualizar/{proveedor_id}",
    response_model=ProveedorResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(rate_limit(
        limit=20,
        window=60,
        key_prefix="proveedores_actualizar",
        error_message="Demasiadas solicitudes de actualización. Espera 1 minuto."
    ))],
    summary="Actualizar proveedor",
    description="Actualiza los datos de un proveedor existente. Solo administradores."
)
def actualizar_proveedor_endpoint(
    request: Request,
    proveedor_id: int,
    proveedor: ProveedorUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["SUPER_ADMIN", "ADMIN"]))
):
    """
    Actualizar proveedor existente.
    
    Rate limit: 20 actualizaciones por minuto.
    Protección: Solo SUPER_ADMIN o ADMIN.
    """
    logger.info(f"📋 ENDPOINT: PUT /proveedores/actualizar/{proveedor_id}")
    logger.info(f"👤 Actualizado por: ID={current_user.id}, Email={current_user.email}")
    
    try:
        db_proveedor = actualizar_proveedor(db, proveedor_id, proveedor)
        
        if not db_proveedor:
            logger.error(f"❌ Proveedor ID={proveedor_id} NO encontrado")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Proveedor con ID {proveedor_id} no encontrado"
            )
        
        logger.info(f"✅ Proveedor ID={proveedor_id} actualizado exitosamente")
        return db_proveedor
    except ValueError as e:
        logger.error(f"❌ Error al actualizar proveedor: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/eliminar/{proveedor_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(rate_limit(
        limit=10,
        window=60,
        key_prefix="proveedores_eliminar",
        error_message="Demasiadas solicitudes de eliminación. Espera 1 minuto."
    ))],
    summary="Eliminar proveedor (soft delete)",
    description="Desactiva un proveedor del sistema. Solo administradores."
)
def eliminar_proveedor_endpoint(
    request: Request,
    proveedor_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["SUPER_ADMIN", "ADMIN"]))
):
    """
    Eliminar proveedor (soft delete).
    
    Rate limit: 10 eliminaciones por minuto.
    Protección: Solo SUPER_ADMIN o ADMIN.
    """
    logger.info(f"📋 ENDPOINT: DELETE /proveedores/eliminar/{proveedor_id}")
    logger.info(f"👤 Eliminado por: ID={current_user.id}, Email={current_user.email}")
    
    try:
        resultado = eliminar_proveedor(db, proveedor_id)
        
        if not resultado:
            logger.error(f"❌ Proveedor ID={proveedor_id} NO encontrado")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Proveedor con ID {proveedor_id} no encontrado"
            )
        
        logger.info(f"✅ {resultado['mensaje']}")
        return MessageResponse(message=resultado["mensaje"])
    except ValueError as e:
        logger.error(f"❌ ERROR al eliminar proveedor: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )