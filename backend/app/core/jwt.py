#app\core\jwt.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

#Toma los datos los copia, luego le da un tiempo de expiracion y 
# luego lo firma con SECRET_KEY para dar el token.
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un token JWT de acceso.
    
    Args:
        data: Datos a incluir en el token (ej: {"sub": "user@email.com"})
        expires_delta: Tiempo de expiración personalizado
    
    Returns:
        Token JWT codificado
    """
    logger.info("🔐 Creando access token...")
    
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)  # 30 minutos por defecto
    
    to_encode.update({"exp": expire})
    
    logger.info(f"📝 Datos del token: {data}")
    logger.info(f"⏰ Expira en: {expire}")
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    logger.info(f"✅ Token creado exitosamente: {encoded_jwt[:20]}...")
    
    return encoded_jwt


#Esta funcion es un atajo para refrescar el token de 30 minutos a 7 dias
#cunado se configure la fontend estara en funcion
def create_refresh_token(data: dict) -> str:
    """
    Crea un refresh token JWT (mayor duración).
    
    Args:
        data: Datos a incluir en el token
    
    Returns:
        Refresh token codificado
    """
    logger.info("🔄 Creando refresh token...")
    
    expires_delta = timedelta(days=7)  # 7 días
    return create_access_token(data, expires_delta)

#Decodifica el token creado anteriormente y 
#confirma si este tiene SECRET_KEY y que no esta caducado
#utilizando la libreria Jose
def verify_token(token: str) -> Optional[dict]:
    """
    Verifica y decodifica un token JWT.
    
    Args:
        token: Token JWT a verificar
    
    Returns:
        Datos decodificados del token o None si es inválido
    """
    logger.info(f"🔍 Verificando token: {token[:20]}...")
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        logger.info(f"✅ Token válido")
        logger.info(f"📝 Payload: {payload}")
        
        return payload
    
    except JWTError as e:
        logger.error(f"❌ Token inválido: {str(e)}")
        return None