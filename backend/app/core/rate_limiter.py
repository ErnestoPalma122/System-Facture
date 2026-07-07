#C:\Users\PC\Desktop\Factu\backend\app\core\rate_limiter.py
import time
import hashlib
from typing import Optional, Dict, Tuple
from fastapi import Request, HTTPException, status
from functools import wraps
from app.core.config import settings

#guarda las marcas de tiempo de las peticiones en cada peticion
#y borra las que ya caducaron lo que hace que cunete las
#peticiones ip utilizando la RAM
class InMemoryRateLimiter:
    """Rate limiter en memoria para desarrollo"""
    
    def __init__(self):
        self.requests: Dict[str, list] = {}
    
    def is_allowed(self, key: str, limit: int, window: int) -> Tuple[bool, int, int]:
        """
        Verifica si la solicitud está permitida.
        Retorna: (permitido, restantes, tiempo_reset)
        """
        current_time = int(time.time())
        
        # Limpiar solicitudes antiguas
        if key in self.requests:
            self.requests[key] = [
                t for t in self.requests[key] 
                if t > current_time - window
            ]
        else:
            self.requests[key] = []
        
        # Verificar límite
        if len(self.requests[key]) >= limit:
            reset_time = self.requests[key][0] + window
            return False, 0, reset_time
        
        # Agregar solicitud actual
        self.requests[key].append(current_time)
        remaining = limit - len(self.requests[key])
        reset_time = current_time + window
        
        return True, remaining, reset_time

#Redis es una base de datos de memoria ultra rapida que
# si 2 o mas servidores estan corriendo los centraliza para 
#que compartan el mismo limite
class RedisRateLimiter:
    """Rate limiter con Redis para producción"""
    
    def __init__(self, redis_url: str):
        try:
            import redis
            self.redis = redis.from_url(redis_url)
            self.redis.ping()
            self.available = True
        except Exception as e:
            print(f"⚠️ Redis no disponible, usando rate limiter en memoria: {e}")
            self.available = False
            self.fallback = InMemoryRateLimiter()
    
    def is_allowed(self, key: str, limit: int, window: int) -> Tuple[bool, int, int]:
        """
        Verifica si la solicitud está permitida usando Redis.
        """
        if not self.available:
            return self.fallback.is_allowed(key, limit, window)
        
        current_time = int(time.time())
        redis_key = f"rate_limit:{key}"
        
        # Obtener solicitudes actuales
        pipe = self.redis.pipeline()
        pipe.zremrangebyscore(redis_key, 0, current_time - window)
        pipe.zcard(redis_key)
        pipe.zadd(redis_key, {str(current_time): current_time})
        pipe.expire(redis_key, window)
        results = pipe.execute()
        
        current_count = results[1]
        
        if current_count >= limit:
            # Obtener el timestamp más antiguo para calcular reset
            oldest = self.redis.zrange(redis_key, 0, 0, withscores=True)
            reset_time = int(oldest[0][1]) + window if oldest else current_time + window
            return False, 0, reset_time
        
        remaining = limit - current_count - 1
        reset_time = current_time + window
        
        return True, remaining, reset_time


# Instancia global del rate limiter
#
def get_rate_limiter():
    """Obtiene la instancia del rate limiter"""
    if settings.REDIS_URL:
        return RedisRateLimiter(settings.REDIS_URL)
    return InMemoryRateLimiter()


rate_limiter = get_rate_limiter()


def rate_limit(
    limit: Optional[int] = None,
    window: Optional[int] = None,
    key_prefix: str = "default",
    error_message: Optional[str] = None
):
    """
    Dependencia de FastAPI para aplicar rate limiting.
    
    Args:
        limit: Número máximo de solicitudes permitidas
        window: Ventana de tiempo en segundos
        key_prefix: Prefijo para la clave de rate limiting
        error_message: Mensaje de error personalizado
    """
    limit = limit or settings.RATE_LIMIT_DEFAULT
    window = window or settings.RATE_LIMIT_WINDOW
    error_message = error_message or "Demasiadas solicitudes. Por favor, intenta más tarde."
    
    async def dependency(request: Request):
        # Obtener IP del cliente
        client_ip = request.client.host
        
        # Considerar X-Forwarded-For si existe (para proxies)
        if "X-Forwarded-For" in request.headers:
            client_ip = request.headers["X-Forwarded-For"].split(",")[0].strip()
        
        # Crear clave única
        key = f"{key_prefix}:{client_ip}"
        
        # Verificar rate limit
        allowed, remaining, reset_time = rate_limiter.is_allowed(key, limit, window)
        
        # Guardar información en el estado de la request para los headers
        request.state.rate_limit_info = {
            "limit": limit,
            "remaining": remaining,
            "reset": reset_time
        }
        
        if not allowed:
            retry_after = reset_time - int(time.time())
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=error_message,
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_time)
                }
            )
    
    return dependency