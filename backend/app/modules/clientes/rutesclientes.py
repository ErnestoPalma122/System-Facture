# app/modules/clientes/routesclientes.py
"""
Endpoints (Rutas) para el módulo de clientes.
Incluye protección JWT, validación de roles, rate limiting y delegación de lógica al servicio.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Request, status, HTTPException
from sqlalchemy.orm import Session

from app.core.rate_limiter import rate_limit
from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.modules.usuarios.models import Usuario

from app.modules.clientes.schemasclientes import (
    ClienteCreate, ClienteUpdate, ClienteResponse, ClienteListResponse, MessageResponse
)
from app.modules.clientes.servicesclientes import (
    get_clientes, get_cliente_by_id, crear_cliente, actualizar_cliente, eliminar_cliente
)
import logging

logger = logging.getLogger(__name__)

# Prefijo de la ruta y etiqueta para Swagger
router = APIRouter(prefix="/clientes", tags=["Clientes"])


# ===========================================================
# ENDPOINTS DE CLIENTES
# ===========================================================

@router.get(
    "/listar",
    response_model=ClienteListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(rate_limit(
        limit=settings.RATE_LIMIT_DEFAULT,
        window=settings.RATE_LIMIT_WINDOW,
        key_prefix="clientes_listar"
    ))],
    summary="Listar clientes",
    description="Obtiene una lista paginada de clientes. Requiere autenticación y rol de Vendedor, Admin o Super Admin."
)
def listar_clientes(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["SUPER_ADMIN", "ADMIN", "VENDEDOR"])), # ← Seguridad por rol
    skip: int = 0,
    limit: int = 100,
    activo: Optional[bool] = None,
    nombre: Optional[str] = None
):
    """Lista clientes con filtros opcionales de nombre y estado."""
    logger.info("=" * 60)
    logger.info(f"📋 ENDPOINT: GET /clientes/listar")
    logger.info(f"👤 Solicitado por: ID={current_user.id}, Rol={current_user.rol.tipo.value if current_user.rol else 'N/A'}")
    logger.info(f"🔎 Filtros: activo={activo}, nombre='{nombre}'")
    logger.info("=" * 60)
    
    clientes = get_clientes(db, skip=skip, limit=limit, activo=activo, nombre=nombre)
    
    logger.info(f"✅ Retornando {len(clientes)} clientes al usuario {current_user.id}")
    return ClienteListResponse(total=len(clientes), clientes=clientes)


@router.get(
    "/obtener/{cliente_id}",
    response_model=ClienteResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(rate_limit(
        limit=settings.RATE_LIMIT_DEFAULT,
        window=settings.RATE_LIMIT_WINDOW,
        key_prefix="clientes_obtener"
    ))],
    summary="Obtener cliente por ID",
    description="Obtiene los detalles completos de un cliente específico. Requiere autenticación."
)
def obtener_cliente(
    request: Request,
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["SUPER_ADMIN", "ADMIN", "VENDEDOR"])) # ← Seguridad por rol
):
    """Obtiene un cliente por su ID."""
    logger.info(f"📋 ENDPOINT: GET /clientes/obtener/{cliente_id} | Usuario: {current_user.id}")
    
    cliente = get_cliente_by_id(db, cliente_id)
    if not cliente:
        logger.error(f"❌ Cliente ID={cliente_id} NO encontrado")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Cliente con ID {cliente_id} no encontrado")
    
    return cliente


@router.post(
    "/crear",
    response_model=ClienteResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit(
        limit=10,
        window=60,
        key_prefix="clientes_crear",
        error_message="Demasiadas solicitudes de creación de clientes. Espera 1 minuto."
    ))],
    summary="Crear nuevo cliente",
    description="Registra un nuevo cliente en el sistema. Solo administradores pueden crear clientes."
)
def crear_cliente_endpoint(
    request: Request,
    cliente_data: ClienteCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["SUPER_ADMIN", "ADMIN"])) # ← Seguridad restrictiva
):
    """Crea un nuevo cliente validando la unicidad del correo."""
    logger.info("=" * 60)
    logger.info(f"📋 ENDPOINT: POST /clientes/crear")
    logger.info(f"👤 Creado por: ID={current_user.id}, Email={current_user.email}")
    logger.info(f"📧 Correo del nuevo cliente: {cliente_data.correo}")
    logger.info("=" * 60)
    
    try:
        nuevo_cliente = crear_cliente(db, cliente_data)
        logger.info(f"✅ Cliente creado exitosamente: ID={nuevo_cliente.id}")
        return nuevo_cliente
    except ValueError as e:
        logger.error(f"❌ Error de validación al crear cliente: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put(
    "/actualizar/{cliente_id}",
    response_model=ClienteResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(rate_limit(
        limit=20,
        window=60,
        key_prefix="clientes_actualizar",
        error_message="Demasiadas solicitudes de actualización. Espera 1 minuto."
    ))],
    summary="Actualizar cliente",
    description="Actualiza los datos de un cliente existente. Solo administradores."
)
def actualizar_cliente_endpoint(
    request: Request,
    cliente_id: int,
    cliente_data: ClienteUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["SUPER_ADMIN", "ADMIN"])) # ← Seguridad restrictiva
):
    """Actualiza parcialmente o totalmente un cliente."""
    logger.info(f"📋 ENDPOINT: PUT /clientes/actualizar/{cliente_id} | Usuario: {current_user.id}")
    
    try:
        cliente_actualizado = actualizar_cliente(db, cliente_id, cliente_data)
        if not cliente_actualizado:
            logger.error(f"❌ Cliente ID={cliente_id} NO encontrado para actualizar")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Cliente con ID {cliente_id} no encontrado")
        
        logger.info(f"✅ Cliente ID={cliente_id} actualizado exitosamente")
        return cliente_actualizado
    except ValueError as e:
        logger.error(f"❌ Error de validación al actualizar cliente: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    "/eliminar/{cliente_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(rate_limit(
        limit=10,
        window=60,
        key_prefix="clientes_eliminar",
        error_message="Demasiadas solicitudes de eliminación. Espera 1 minuto."
    ))],
    summary="Desactivar cliente (Soft Delete)",
    description="Desactiva un cliente del sistema (no lo borra físicamente). Solo administradores."
)
def eliminar_cliente_endpoint(
    request: Request,
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["SUPER_ADMIN", "ADMIN"])) # ← Seguridad restrictiva
):
    """Realiza un soft delete (cambia estado a inactivo)."""
    logger.info(f"📋 ENDPOINT: DELETE /clientes/eliminar/{cliente_id} | Usuario: {current_user.id}")
    
    try:
        resultado = eliminar_cliente(db, cliente_id)
        
        if not resultado["cambio_realizado"]:
            logger.warning(f"⚠️ {resultado['mensaje']}")
            return MessageResponse(message=resultado["mensaje"])
        
        logger.info(f"✅ {resultado['mensaje']}")
        return MessageResponse(message=resultado["mensaje"])
        
    except ValueError as e:
        logger.error(f"❌ Error al eliminar cliente: {str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))