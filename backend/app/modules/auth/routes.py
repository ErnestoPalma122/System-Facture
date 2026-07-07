#C:\Users\PC\Desktop\Factu\backend\app\modules\auth\routes.py
from fastapi import APIRouter, Depends, Request, status, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional
from app.core.rate_limiter import rate_limit
from app.core.database import get_db
from app.modules.auth.schemas import (
    LoginRequest,
    RegisterRequest,
    ForgotPasswordRequest,
    LoginResponse,
    RegisterResponse,
    MessageResponse,
    TokenResponse
)
from app.modules.auth.services import (
    login,
    register_user,
    logout,
    refresh_access_token
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Autenticación"])


# ===========================================================
# ENDPOINTS DE AUTENTICACIÓN
# ===========================================================

@router.post(
    "/iniciar-sesion",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(rate_limit(
        limit=5,
        window=60,
        key_prefix="auth_login",
        error_message="Demasiados intentos de inicio de sesión. Espera 1 minuto."
    ))],
    summary="Iniciar sesión",
    description="Autentica un usuario y retorna un token JWT"
)
async def iniciar_sesion(
    request: Request,
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Endpoint para iniciar sesión.
    
    Rate limit: 5 intentos por minuto para prevenir fuerza bruta.
    """
    logger.info("=" * 60)
    logger.info("📋 ENDPOINT: POST /auth/iniciar-sesion")
    logger.info(f"📧 Email: {credentials.email}")
    logger.info("=" * 60)
    
    # Obtener información del cliente
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    logger.info(f"🌐 IP: {ip_address}")
    logger.info(f"🖥️ User-Agent: {user_agent}")
    
    try:
        result = login(db, credentials, ip_address, user_agent)
        
        logger.info("✅ LOGIN EXITOSO - Retornando respuesta")
        
        return LoginResponse(
            message="Inicio de sesión exitoso",
            access_token=result["access_token"],
            token_type=result["token_type"]
        )
    
    except ValueError as e:
        logger.error(f"❌ ERROR EN LOGIN: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post(
    "/olvide-mi-contrasena",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(rate_limit(
        limit=3,
        window=300,
        key_prefix="auth_forgot_password",
        error_message="Demasiadas solicitudes de recuperación. Espera 5 minutos."
    ))],
    summary="Recuperar contraseña",
    description="Envía un email con instrucciones para recuperar la contraseña"
)
async def olvide_mi_contrasena(
    request: Request,
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Endpoint para solicitar recuperación de contraseña.
    
    Rate limit: 3 solicitudes cada 5 minutos para prevenir abuso.
    """
    logger.info("=" * 60)
    logger.info("📋 ENDPOINT: POST /auth/olvide-mi-contrasena")
    logger.info(f"📧 Email: {data.email}")
    logger.info("=" * 60)
    
    # TODO: Implementar lógica de recuperación
    # - Verificar si email existe
    # - Generar token de recuperación
    # - Enviar email con link de recuperación
    
    logger.info("⚠️ Funcionalidad de recuperación NO IMPLEMENTADA aún")
    
    return MessageResponse(
        message="Si el email existe, se han enviado las instrucciones de recuperación"
    )


@router.post(
    "/cerrar-sesion",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(rate_limit(
        limit=10,
        window=60,
        key_prefix="auth_logout",
        error_message="Demasiados intentos de cierre de sesión."
    ))],
    summary="Cerrar sesión",
    description="Invalida el token JWT actual"
)
async def cerrar_sesion(
    request: Request,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Endpoint para cerrar sesión.
    
    Rate limit: 10 solicitudes por minuto.
    """
    logger.info("=" * 60)
    logger.info("📋 ENDPOINT: POST /auth/cerrar-sesion")
    logger.info("=" * 60)
    
    if not authorization:
        logger.error("❌ ERROR: No se proporcionó token de autorización")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autorización requerido"
        )
    
    # Extraer token del header Authorization
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Scheme inválido")
    except Exception as e:
        logger.error(f"❌ ERROR: Formato de autorización inválido: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato de autorización inválido. Use: Bearer <token>"
        )
    
    logger.info(f"🔑 Token recibido: {token[:30]}...")
    
    try:
        success = logout(db, token)
        
        if success:
            logger.info("✅ LOGOUT EXITOSO")
            return MessageResponse(message="Sesión cerrada exitosamente")
        else:
            logger.warning("⚠️ No se encontró sesión activa")
            return MessageResponse(message="No se encontró sesión activa")
    
    except ValueError as e:
        logger.error(f"❌ ERROR EN LOGOUT: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/refrescar-token",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(rate_limit(
        limit=10,
        window=60,
        key_prefix="auth_refresh",
        error_message="Demasiadas solicitudes de refresco de token."
    ))],
    summary="Refrescar token",
    description="Genera un nuevo token JWT usando el refresh token"
)
async def refrescar_token(
    request: Request,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Endpoint para refrescar el token JWT.
    
    Rate limit: 10 solicitudes por minuto.
    """
    logger.info("=" * 60)
    logger.info("📋 ENDPOINT: POST /auth/refrescar-token")
    logger.info("=" * 60)
    
    if not authorization:
        logger.error("❌ ERROR: No se proporcionó refresh token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token requerido"
        )
    
    # Extraer token del header Authorization
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Scheme inválido")
    except Exception as e:
        logger.error(f"❌ ERROR: Formato de autorización inválido: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato de autorización inválido. Use: Bearer <refresh_token>"
        )
    
    logger.info(f"🔄 Refresh Token recibido: {token[:30]}...")
    
    try:
        result = refresh_access_token(db, token)
        
        logger.info("✅ REFRESH EXITOSO - Retornando nuevo token")
        
        return TokenResponse(
            access_token=result["access_token"],
            token_type=result["token_type"]
        )
    
    except ValueError as e:
        logger.error(f"❌ ERROR EN REFRESH: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )