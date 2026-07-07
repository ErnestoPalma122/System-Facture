from fastapi import FastAPI

# Configuración
from app.core.middleware import configure_middlewares

# Routers
from app.modules.auth.routes import router as auth_router
from app.modules.usuarios.routes import router as users_router
from app.modules.productos.routesproducto import router as productos_router
from app.modules.proveedores.routes_proveedor import router as proveedores_router
from app.modules.inventario.routes_inventario import router as inventario_router



app = FastAPI(
    title="Sistema de Facturación Electrónica",
    description="API para la gestión de facturación electrónica conforme a los requerimientos del Ministerio de Hacienda.",
    version="1.0.0",
    docs_url="/docs",          # Swagger
    redoc_url="/redoc",        # ReDoc
    openapi_url="/openapi.json"
)


# ===========================================================
# CONFIGURACIÓN DE MIDDLEWARES
# ===========================================================

configure_middlewares(app)


# ===========================================================
# REGISTRO DE MÓDULOS
# ===========================================================

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(productos_router)
app.include_router(proveedores_router)
app.include_router(inventario_router)



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