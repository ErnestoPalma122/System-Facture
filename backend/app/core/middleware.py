# C:\Users\PC\Desktop\Factu\backend\app\core\middleware.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

def configure_middlewares(app: FastAPI):
    print("✅ [MIDDLEWARE] Configurando CORS para http://localhost:5173...")
    
    # 1. CORS DEBE SER EL PRIMER MIDDLEWARE REGISTRADO
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            
            "http://localhost:5173",
            
            "http://127.0.0.1:5173",
            
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 2. Middleware para inyectar headers de rate limit (DESPUÉS de CORS)
    @app.middleware("http")
    async def add_rate_limit_headers(request: Request, call_next):
        # Si es una petición OPTIONS (preflight), la dejamos pasar sin tocar nada
        # para que el middleware de CORS superior haga su trabajo limpio.
        if request.method == "OPTIONS":
            return await call_next(request)
            
        response = await call_next(request)
        
        if hasattr(request.state, "rate_limit_info"):
            info = request.state.rate_limit_info
            response.headers["X-RateLimit-Limit"] = str(info["limit"])
            response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
            response.headers["X-RateLimit-Reset"] = str(info["reset"])
        
        return response
        
    print("✅ [MIDDLEWARE] Configuración completada exitosamente.")