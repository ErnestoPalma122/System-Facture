# C:\Users\PC\Desktop\Factu\backend\app\main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Routers
from app.modules.auth.routes import router as auth_router
from app.modules.usuarios.routes import router as users_router
from app.modules.productos.routesproducto import router as productos_router
from app.modules.proveedores.routes_proveedor import router as proveedores_router
from app.modules.inventario.routes_inventario import router as inventario_router
from app.modules.ingreso_mercaderia.ingreso_mercaderia_routes import router as ingreso_mercaderia_router
from app.modules.clientes.rutesclientes import router as rutesclientes_router
from app.modules.emisor.routes import router as emisor_router
from app.modules.hacienda.catalogos_routes import router as catalogos_router


# ===========================================================
# INICIALIZACIÓN DE LA APP
# ===========================================================

app = FastAPI(
    title="Sistema de Facturación Electrónica",
    description="API para la gestión de facturación electrónica conforme a los requerimientos del Ministerio de Hacienda.",
    version="1.0.0",
    docs_url="/docs",          # Swagger (No se verá afectado, seguirá funcionando perfecto)
    redoc_url="/redoc",        # ReDoc
    openapi_url="/openapi.json"
)

# ===========================================================
# CONFIGURACIÓN DE MIDDLEWARES
# ===========================================================

def configure_middlewares(application: FastAPI):
    """
    Configura todos los middlewares de la aplicación.
    """
    print("🔥 [MAIN] Registrando middleware de CORS para http://localhost:5173...")
    
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",      
            "http://127.0.0.1:5173",      
            "http://localhost:3000",      
            "http://127.0.0.1:3000",
        ],
        allow_credentials=True,            
        allow_methods=["*"],               
        allow_headers=["*"],               
    )
    
    print("✅ [MAIN] Middleware de CORS registrado exitosamente.")

# ⚠️ ESTA ERA LA LÍNEA QUE FALTABA: LLAMAR A LA FUNCIÓN ⚠️
configure_middlewares(app)

# ===========================================================
# REGISTRO DE MÓDULOS
# ===========================================================

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(productos_router)
app.include_router(proveedores_router)
app.include_router(inventario_router)
app.include_router(ingreso_mercaderia_router)
app.include_router(rutesclientes_router)
app.include_router(emisor_router)
app.include_router(catalogos_router)


# ===========================================================
# ENDPOINT RAÍZ
# ===========================================================

@app.get("/", tags=["Sistema"])
def root():
    return {
        "application": "Sistema de Facturación Electrónica",
        "company": "Negocios Informáticos",
        "version": "1.0.0",
        "status": "API funcionando correctamente"
    }

# ===========================================================
# HEALTH CHECK
# ===========================================================

@app.get("/health", tags=["Sistema"])
def health():
    return {
        "status": "UP"
    }