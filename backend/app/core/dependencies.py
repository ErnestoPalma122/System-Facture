#C:\Users\PC\Desktop\Factu\backend\app\core\dependencies.py
from fastapi import Depends, HTTPException, status
# Estandariza la extracción del token. En lugar de que tú leas los 
#headers manualmente y busques la palabra "Bearer" FastAPI lo hace por ti 
#y te da el token limpio.
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.jwt import verify_token
from app.modules.usuarios.models import Usuario
import logging

logger = logging.getLogger(__name__)


#Configura FastAPI para saber que debe esperar un token en el encabezado HTTP
security = HTTPBearer()

#Dependecia que funciona como portero, extrae y decodifica los tokens
#y centraliza las autenticaciones de cada token
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Usuario:
    """
    Dependencia que valida el token JWT y retorna el usuario actual.
    
    Uso en endpoints:
        current_user: Usuario = Depends(get_current_user)
    """
    logger.info("=" * 60)
    logger.info("🔐 VALIDANDO TOKEN JWT")
    logger.info("=" * 60)
    
    token = credentials.credentials
    logger.info(f"🔑 Token recibido: {token[:30]}...")
    
    # Verificar token
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
    
    # Buscar usuario en base de datos
    usuario = db.query(Usuario).filter(Usuario.id == int(usuario_id)).first()
    
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

#Dependecia de Usuario activo 
#lo que hace es la compracion de si el usuario esta activo o desctivado
async def get_current_active_user(
    current_user: Usuario = Depends(get_current_user)
) -> Usuario:
    """
    Dependencia que verifica que el usuario tenga estado ACTIVO.
    Útil para endpoints que requieren usuario activo específicamente.
    """
    if not current_user.puede_acceder():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Usuario con estado {current_user.estado.value}"
        )
    return current_user

#Fabrica de roles
#bascamente hace que no tengas que escribir una dependencia distinta 
# cada vez que se de un rol
def require_role(required_roles: list):
    """
    Dependencia que verifica si el usuario tiene un rol específico.
    
    Uso:
        @router.get("/admin")
        async def admin_endpoint(
            current_user: Usuario = Depends(require_role(["SUPER_ADMIN", "ADMIN"]))
        ):
            ...
    """
    #funcion interna que recuerda la lista de roles de (required_roles)
    async def role_checker(current_user: Usuario = Depends(get_current_user)):
        logger.info(f"🔍 Verificando rol del usuario ID={current_user.id}")
        
        if not current_user.rol:
            logger.error("❌ Usuario no tiene rol asignado")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario no tiene rol asignado"
            )
        
        # Convertir el tipo de rol a string para comparación
        user_role = current_user.rol.tipo.value.upper()
        
        logger.info(f"👤 Rol del usuario: {user_role}")
        #Solo escribes Depends(require_role y le das el rol que
        #necesita para acceder en las rutas
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