# app/core/dependencies.py
from fastapi import Depends, HTTPException, status, Cookie, Header # <-- AGREGADO: Cookie y Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session, joinedload
from typing import Optional # <-- AGREGADO: Para los valores opcionales
from app.core.database import get_db
from app.core.jwt import verify_token
from app.modules.usuarios.models import Usuario, Rol
import logging

logger = logging.getLogger(__name__)

# Configura FastAPI para saber que debe esperar un token en el encabezado HTTP
security = HTTPBearer()

# Dependencia que funciona como portero, extrae y decodifica los tokens
# y centraliza las autenticaciones de cada token
async def get_current_user(
    # 🔥 MODIFICADO: En lugar de usar Depends(security) que solo lee el Header,
    # leemos manualmente el Header y la Cookie para soportar ambos métodos de autenticación.
    authorization: Optional[str] = Header(None, alias="Authorization"),
    access_token_cookie: Optional[str] = Cookie(None, alias="access_token"),
    db: Session = Depends(get_db)
) -> Usuario:
    """
    Dependencia que valida el token JWT y retorna el usuario actual.
    Optimizada para cargar también el rol y sus permisos de una sola vez.
    🔥 Ahora soporta tokens enviados por Header (Authorization: Bearer) o por Cookie HttpOnly.
    """
    logger.info("=" * 60)
    logger.info("🔐 VALIDANDO TOKEN JWT")
    logger.info("=" * 60)
    
    # 🔥 LÓGICA DE EXTRACCIÓN DE TOKEN (Busca primero en Header, luego en Cookie)
    token = None
    
    # 1. Intentar obtener del Header (Prioridad alta, usado por Swagger/Postman)
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        logger.info("🔑 Token extraído del Header 'Authorization'")
    
    # 2. Si no hay Header, intentar obtener de la Cookie HttpOnly (Usado por el Frontend)
    elif access_token_cookie:
        token = access_token_cookie
        logger.info("🍪 Token extraído de la Cookie 'access_token'")

    # Si después de buscar en ambos lados no hay token, rechazamos la petición
    if not token:
        logger.error("❌ No se proporcionó token (ni en Header ni en Cookie)")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se proporcionó token de autenticación",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.info(f"🔑 Token recibido: {token[:30]}...")
    
    # Verificar token (A partir de aquí, tu código original sigue intacto)
    payload = verify_token(token)
    
    if not payload:
        logger.error("❌ Token inválido o expirado")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Obtener usuario del payload
    usuario_id = payload.get("sub")
    
    if not usuario_id:
        logger.error("❌ Token no contiene ID de usuario")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no contiene información de usuario",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.info(f"👤 Usuario ID del token: {usuario_id}")
    
    # Buscar usuario en base de datos (CARGA ANSICIADA del rol y sus permisos)
    usuario = db.query(Usuario).options(
        joinedload(Usuario.rol).joinedload(Rol.permisos)
    ).filter(Usuario.id == int(usuario_id)).first()
    
    if not usuario:
        logger.error(f"❌ Usuario ID={usuario_id} NO encontrado en BD")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # VERIFICAR ESTADO usando puede_acceder()
    if not usuario.puede_acceder():
        logger.error(f"❌ Usuario ID={usuario_id} tiene estado {usuario.estado.value}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Usuario con estado {usuario.estado.value}. No puede acceder al sistema."
        )
    
    logger.info(f"✅ USUARIO AUTENTICADO: ID={usuario.id}, Email={usuario.email}, Estado={usuario.estado.value}")
    logger.info("=" * 60)
    
    return usuario


# Dependencia de Usuario activo 
async def get_current_active_user(
    current_user: Usuario = Depends(get_current_user)
) -> Usuario:
    """
    Dependencia que verifica que el usuario tenga estado ACTIVO.
    """
    if not current_user.puede_acceder():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Usuario con estado {current_user.estado.value}"
        )
    return current_user


# Fabrica de roles
def require_role(required_roles: list):
    """
    Dependencia que verifica si el usuario tiene un rol específico.
    """
    async def role_checker(current_user: Usuario = Depends(get_current_user)):
        logger.info(f"🔍 Verificando rol del usuario ID={current_user.id}")
        
        if not current_user.rol:
            logger.error("❌ Usuario no tiene rol asignado")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario no tiene rol asignado"
            )
        
        user_role = current_user.rol.tipo.value.upper()
        logger.info(f"👤 Rol del usuario: {user_role}")
        logger.info(f"🎯 Roles requeridos: {required_roles}")
        
        if user_role not in [r.upper() for r in required_roles]:
            logger.error(f"❌ Rol {user_role} NO está en la lista permitida")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Se requiere uno de estos roles: {', '.join(required_roles)}"
            )
        
        logger.info(f"✅ Rol {user_role} autorizado")
        return current_user
    
    return role_checker


# ✅ NUEVO: Fábrica de permisos asertivos
def require_permission(required_permission: str):
    """
    Dependencia que verifica si el rol del usuario tiene un permiso específico.
    
    Uso en endpoints:
        @router.post("/crear")
        async def crear_bodega(
            current_user: Usuario = Depends(require_permission("bodega:crear"))
        ):
            ...
    """
    async def permission_checker(current_user: Usuario = Depends(get_current_user)):
        logger.info(f"🔍 Verificando permiso '{required_permission}' para usuario ID={current_user.id}")
        
        if not current_user.rol or not current_user.rol.activo:
            logger.error("❌ Usuario no tiene un rol activo asignado")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario no tiene un rol activo asignado"
            )
        
        # Gracias al joinedload en get_current_user, current_user.rol.permisos ya está cargado
        permisos_usuario = [p.codigo.lower() for p in current_user.rol.permisos if p.activo]
        
        if required_permission.lower() not in permisos_usuario:
            logger.error(f"❌ Permiso '{required_permission}' NO encontrado en el rol '{current_user.rol.nombre}'")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permiso denegado. Se requiere el permiso: {required_permission}"
            )
        
        logger.info(f"✅ Permiso '{required_permission}' autorizado para rol '{current_user.rol.nombre}'")
        return current_user
    
    return permission_checker