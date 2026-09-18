#backend\tests\conftest.py
# ============================================================================
# 1. CARGA DE VARIABLES DE ENTORNO DE PRUEBA (DEBE IR PRIMERO)
# ============================================================================
import os
from dotenv import load_dotenv

# Forzar la carga del archivo .env.test que está en la carpeta padre (backend/)
env_path = os.path.join(os.path.dirname(__file__), '..', '.env.test')
load_dotenv(dotenv_path=env_path, override=True)

# ============================================================================
# 2. IMPORTACIONES
# ============================================================================
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import get_db, Base
from app.modules.usuarios.models import Usuario, EstadoUsuario
from app.modules.auth.services import get_password_hash

# ============================================================================
# 3. CONFIGURACIÓN DE BASE DE DATOS DE PRUEBA
# ============================================================================
# Construimos la URL explícitamente desde las variables de .env.test 
# para garantizar que NUNCA se conecte a la BD de producción.
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "formula11")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "negocios_informaticos_pruebas")

TEST_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Motor de base de datos exclusivo para pruebas
test_engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# ============================================================================
# 4. FIXTURES (Preparación del entorno para cada test)
# ============================================================================

@pytest.fixture(scope="function")
def db_session():
    """
    Proporciona una sesión de base de datos limpia para cada prueba.
    Scope 'function' garantiza que se ejecute antes y después de cada test.
    """
    # Aseguramos que las tablas existan (por si acaso no se corrió Alembic)
    Base.metadata.create_all(bind=test_engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Opcional: Limpiar tablas después de cada test para aislamiento total
        # Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    Cliente HTTP de prueba que inyecta la sesión de base de datos de prueba
    en lugar de la sesión de producción.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    # Reemplazamos la dependencia global de FastAPI
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Limpiamos las dependencias al finalizar para no afectar otros tests
    app.dependency_overrides.clear()


@pytest.fixture
def usuario_test(db_session):
    """
    Crea y devuelve un usuario de prueba en la base de datos.
    Si ya existe, lo reutiliza para ahorrar tiempo.
    """
    email_test = "test@example.com"
    
    # Buscar si ya existe
    usuario_existente = db_session.query(Usuario).filter(
        Usuario.email == email_test
    ).first()
    
    if usuario_existente:
        return usuario_existente
    
    # Crear nuevo usuario de prueba
    # NOTA: Ajusta departamento_id=1 y rol_id=1 si tus seeds usan otros IDs
    nuevo_usuario = Usuario(
        nombre="Usuario Test QA",
        email=email_test,
        password_hash=get_password_hash("password123"),
        telefono="2222-2222",
        departamento_id=1,  
        rol_id=1,           
        estado=EstadoUsuario.ACTIVO
    )
    
    db_session.add(nuevo_usuario)
    db_session.commit()
    db_session.refresh(nuevo_usuario)
    
    return nuevo_usuario


@pytest.fixture
def auth_cookies(client, usuario_test):
    """
    Simula un inicio de sesión exitoso y devuelve las cookies resultantes.
    Esto permite que otros tests hagan peticiones autenticadas sin repetir el login.
    """
    response = client.post("/auth/iniciar-sesion", json={
        "email": "test@example.com",
        "password": "password123"
    })
    
    # Verificación de seguridad: si el login falla, el test se detiene aquí con un error claro
    assert response.status_code == 200, f"El login de prueba falló. Respuesta: {response.json()}"
    
    # Devolvemos el objeto de cookies (que contiene 'access_token')
    return response.cookies


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """
    Limpia el rate limiter antes de cada test.
    Funciona sin importar si el backend real es InMemoryRateLimiter
    o RedisRateLimiter (con o sin fallback).
    """
    from app.core.rate_limiter import rate_limiter
    rate_limiter.reset()
    yield