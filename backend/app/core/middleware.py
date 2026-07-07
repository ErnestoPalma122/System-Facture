#C:\Users\PC\Desktop\Factu\backend\app\core\middleware.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware


def configure_middlewares(app: FastAPI):

    # CORS Middleware
    #Muestra a que puerto se conectara la backend con la frontend
    #con los metodos "GET","POST","PUT","PATCH","DELETE","OPTIONS
    #con cualquier encabezado ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ],
        allow_credentials=True,
        allow_methods=[
            "GET",
            "POST",
            "PUT",
            "PATCH",
            "DELETE",
            "OPTIONS"
        ],
        allow_headers=["*"],
    )
    
    # Rate Limit Headers Middleware
    #Intercepata dosa las peticiones HTTP y antes de enviar la respuesta 
    #le inyecta el limite de datos en los encabezados. 
    @app.middleware("http")
    async def add_rate_limit_headers(request: Request, call_next):
        response = await call_next(request)
        
        # Agregar headers de rate limit si están disponibles
        if hasattr(request.state, "rate_limit_info"):
            info = request.state.rate_limit_info
            response.headers["X-RateLimit-Limit"] = str(info["limit"])
            response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
            response.headers["X-RateLimit-Reset"] = str(info["reset"])
        
        return response