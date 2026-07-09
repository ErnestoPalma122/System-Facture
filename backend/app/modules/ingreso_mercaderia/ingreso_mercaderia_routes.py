# app/modules/ingreso_mercaderia/ingreso_mercaderia_routes.py
"""
Endpoints para el módulo de ingreso de mercadería.
Rutas limpias sin lógica de negocio (delegada al service).
"""

from fastapi import APIRouter, Depends, Request, status, HTTPException
from sqlalchemy.orm import Session
from app.core.rate_limiter import rate_limit
from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.modules.usuarios.models import Usuario
from app.modules.ingreso_mercaderia.ingreso_mercaderia_shemas import (
    IngresoMercaderiaCreate,
    IngresoMercaderiaResponse,
    MessageResponse
)
from app.modules.ingreso_mercaderia.ingreso_mercaderia_service import IngresoMercaderiaService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ingreso-mercaderia", tags=["Ingreso de Mercadería"])


@router.post(
    "/crear",
    response_model=IngresoMercaderiaResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit(
        limit=5,
        window=60,
        key_prefix="ingreso_mercaderia_crear",
        error_message="Demasiadas solicitudes de ingreso de mercadería. Espera 1 minuto."
    ))],
    summary="Crear ingreso de mercadería",
    description=(
        "Crea un nuevo ingreso de mercadería con transacción atómica.\n\n"
        "**Proceso:**\n"
        "1. Valida todas las referencias (proveedor, productos, bodegas, estados)\n"
        "2. Crea la cabecera del ingreso\n"
        "3. Crea los items con sus series (cada serie = 1 item)\n"
        "4. Actualiza el stock de cada producto en su bodega\n"
        "5. Commit transacción\n\n"
        "**Default:**\n"
        "- estado_ingreso_id = 8 (COMPLETO PROCESADO)\n"
        "- estado_item_id = 1 (DISPONIBLE)\n\n"
        "**Nota:** Cada producto puede tener múltiples series. Cada serie genera un item independiente."
    )
)
def crear_ingreso_mercaderia(
    request: Request,
    data: IngresoMercaderiaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["SUPER_ADMIN", "ADMIN"]))
):
    """
    Endpoint para crear ingreso de mercadería.
    
    **Protección:** Solo SUPER_ADMIN o ADMIN pueden crear ingresos.
    
    **Rate limit:** 5 ingresos por minuto.
    """
    logger.info("=" * 60)
    logger.info(f"📋 ENDPOINT: POST /ingreso-mercaderia/crear")
    logger.info(f"👤 Usuario: ID={current_user.id}, Email={current_user.email}")
    logger.info(f"📦 Proveedor ID: {data.proveedor_id}")
    logger.info(f"📦 Total items: {len(data.items)}")
    logger.info("=" * 60)
    
    try:
        # Delegar lógica al servicio - PASAR current_user.id
        ingreso = IngresoMercaderiaService.crear_ingreso(db, data, current_user.id)
        
        logger.info(f"✅ Ingreso creado exitosamente: ID={ingreso.id}")
        return ingreso
        
    except ValueError as e:
        logger.error(f"❌ Error de validación: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ Error inesperado: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get(
    "/obtener/{ingreso_id}",
    response_model=IngresoMercaderiaResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(rate_limit(
        limit=settings.RATE_LIMIT_DEFAULT,
        window=settings.RATE_LIMIT_WINDOW,
        key_prefix="ingreso_mercaderia_obtener"
    ))],
    summary="Obtener ingreso por ID",
    description="Obtiene los detalles de un ingreso de mercadería con sus items."
)
def obtener_ingreso_mercaderia(
    request: Request,
    ingreso_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Endpoint para obtener un ingreso por ID.
    
    **Protección:** Requiere autenticación JWT.
    """
    logger.info(f"📋 ENDPOINT: GET /ingreso-mercaderia/obtener/{ingreso_id}")
    logger.info(f"👤 Usuario: ID={current_user.id}")
    
    try:
        ingreso = IngresoMercaderiaService.obtener_ingreso_por_id(db, ingreso_id)
        return ingreso
        
    except ValueError as e:
        logger.error(f"❌ Ingreso no encontrado: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ Error inesperado: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )