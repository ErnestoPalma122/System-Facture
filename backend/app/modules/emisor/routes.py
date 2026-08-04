# app/modules/emisor/routes.py
from fastapi import APIRouter, Depends, Request, status, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
# ✅ ACTUALIZADO: Importar require_permission en lugar de require_role
from app.core.dependencies import require_permission, get_current_user
from app.modules.usuarios.models import Usuario
from app.modules.emisor.schemas import EmisorCreate, EmisorUpdate, EmisorResponse
from app.modules.emisor.services import get_emisor_activo, guardar_emisor
import logging

logger = logging.getLogger(__name__)

# El prefijo es /emisor, y las rutas internas tendrán nombres de acción
router = APIRouter(prefix="/emisor", tags=["Configuración del Emisor"])


@router.get(
    "/obtener",
    response_model=EmisorResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener configuración del emisor",
    description="Obtiene los datos fiscales configurados de la empresa emisora activa. Requiere permiso 'emisor:leer'."
)
def obtener_emisor(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtiene la configuración actual del emisor."""
    logger.info("📋 ENDPOINT: GET /emisor/obtener")
    emisor = get_emisor_activo(db)
    
    if not emisor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se ha configurado ningún emisor en el sistema."
        )
    return emisor


@router.post(
    "/crear",
    response_model=EmisorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear configuración del emisor",
    description="Crea la configuración fiscal inicial de la empresa emisora. TODOS los campos son obligatorios. Requiere permiso 'emisor:actualizar'."
)
def crear_emisor(
    request: Request,
    emisor_data: EmisorCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Crea una nueva configuración de emisor. Falla si ya existe uno activo."""
    logger.info("=" * 60)
    logger.info(f"📋 ENDPOINT: POST /emisor/crear | Usuario: {current_user.email}")
    logger.info("=" * 60)
    
    if get_emisor_activo(db):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una configuración de emisor activa. Usa el endpoint /actualizar para modificarla."
        )
    
    try:
        emisor_guardado = guardar_emisor(db, emisor_data)
        logger.info(f"✅ Configuración de emisor creada exitosamente por {current_user.email}")
        return emisor_guardado
    except ValueError as e:
        logger.error(f"❌ Error de validación al crear emisor: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put(
    "/actualizar",
    response_model=EmisorResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar configuración del emisor",
    description="Reemplaza por completo la configuración fiscal de la empresa. TODOS los campos son obligatorios. Requiere permiso 'emisor:actualizar'."
)
def actualizar_emisor(
    request: Request,
    emisor_data: EmisorUpdate,
    db: Session = Depends(get_db),
    
    current_user: Usuario = Depends(get_current_user)
):
    """Actualiza la configuración existente del emisor."""
    logger.info("=" * 60)
    logger.info(f"📋 ENDPOINT: PUT /emisor/actualizar | Usuario: {current_user.email}")
    logger.info("=" * 60)
    
    if not get_emisor_activo(db):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No existe un emisor configurado. Usa el endpoint /crear para configurarlo primero."
        )
    
    try:
        emisor_actualizado = guardar_emisor(db, emisor_data)
        logger.info(f"✅ Configuración de emisor actualizada exitosamente por {current_user.email}")
        return emisor_actualizado
    except ValueError as e:
        logger.error(f"❌ Error de validación al actualizar emisor: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))