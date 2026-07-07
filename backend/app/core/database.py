#C:\Users\PC\Desktop\Factu\backend\app\core\database.py
#Este archivo tiene una única responsabilidad:
#Crear y administrar la conexión entre la aplicación
# y la base de datos PostgreSQL utilizando SQLAlchemy.
#-----------------------------------------------------------------------
#Importa una libreria de SQLAlchemy
#Basicamente (create_engine) esta encargado de comunicarse con la base de datos 
#y administra las conexiones dentro del proyecto
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
#En database.py hara uso de la configuracion de (config.py)
#para construir el motor de conexión, crear sesiones y 
# proporcionar una forma segura de acceder a la base de datos 
# desde FastAPI.
from app.core.config import settings

# ===========================================================
# CONFIGURACIÓN DE LA BASE DE DATOS
# ===========================================================

# Se crea el motor que conecta con PostgreSQL
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=False  # Cambiar a True para ver queries SQL en desarrollo
)

# es una fábrica que crea "sesiones" (transacciones) para interactuar con la BD.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base es el lienzo base donde SQLAlchemy registrará la estructura de tus tablas.
Base = declarative_base()


# ===========================================================
# DEPENDENCIA PARA OBTENER SESIÓN DE BD
# ===========================================================

def get_db():
    """
    Dependencia de FastAPI para obtener sesión de base de datos.
    Uso: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        #(yield). Crea una sesión de base de datos, se la "presta" a tu ruta de FastAPI
        yield db
    #garantiza que se cierre (db.close()) en el bloque finally cuando la petición termina.
    finally:
        db.close()