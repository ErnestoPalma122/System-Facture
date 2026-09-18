# alembic/env.py
#
# Este archivo decide a que base de datos se conecta Alembic cuando
# corres cualquier comando de migracion (upgrade, downgrade, revision).
#
# CAMBIO CRITICO respecto a la version original: antes, este archivo
# importaba "settings" directamente, y "settings" carga su configuracion
# leyendo el archivo .env de PRODUCCION por defecto (ver app/core/config.py,
# linea "load_dotenv()" sin argumentos). Eso significa que si corrias
# "alembic upgrade head" sin ningun paso adicional, terminabas conectado
# a la base de datos de produccion sin ningun aviso.
#
# La solucion: antes de importar "settings", este archivo obliga a definir
# explicitamente la variable de entorno APP_ENV (test o prod). Si no esta
# definida, el script se detiene con un error en vez de adivinar.

from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys
from dotenv import load_dotenv

# Agregar el directorio raiz del backend al path, igual que en la version original
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

# ============================================================
# PASO 1: Determinar el entorno ANTES de importar settings
# ============================================================
# APP_ENV debe venir definida en la terminal antes de correr alembic.
# Ejemplo en cmd (Windows):
#   set APP_ENV=test && alembic upgrade head
#   set APP_ENV=prod && alembic upgrade head
#
# Si no se define, se detiene aqui. No hay valor por defecto porque
# un valor por defecto es exactamente el riesgo que queremos eliminar.
APP_ENV = os.getenv("APP_ENV", "").strip().lower()

if APP_ENV == "test":
    # Carga .env.test y sobreescribe cualquier variable de entorno
    # que ya exista en el sistema, para garantizar que se use esta
    dotenv_path = os.path.join(backend_dir, ".env.test")
    load_dotenv(dotenv_path, override=True)
elif APP_ENV == "prod":
    # Carga el .env de produccion explicitamente
    dotenv_path = os.path.join(backend_dir, ".env")
    load_dotenv(dotenv_path, override=True)
else:
    raise RuntimeError(
        "No se definio la variable de entorno APP_ENV. "
        "Debes especificar 'test' o 'prod' antes de correr alembic. "
        "Ejemplo en cmd: set APP_ENV=test && alembic upgrade head"
    )

# ============================================================
# PASO 2: Importar configuracion y modelos DESPUES de fijar el entorno
# ============================================================
# Este orden importa: si "settings" se importara antes del bloque de
# arriba, ya habria leido las variables de entorno equivocadas.
from app.core.config import settings
from app.core.database import Base
from app.modules.usuarios.models import Usuario, Departamento, Rol, Sesion
from app.modules.productos.modelsproducto import Producto, Categoria, Precio, Stock, Bodega
from app.modules.proveedores.models_proveedor import Proveedor
from app.modules.inventario.models_inventario import Ingreso, EstadoItems, Items, Estado_Ingreso
from app.modules.clientes.modelsclientes import Cliente
from app.modules.emisor.models import Emisor

# Configuracion estandar de Alembic (igual que la version original)
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ============================================================
# PASO 3: Construir la URL de conexion a partir de settings
# ============================================================
DATABASE_URL = (
    f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}"
    f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)

# ============================================================
# PASO 4: Verificacion visible en pantalla antes de conectar
# ============================================================
# Esta linea se imprime siempre, para que en cualquier momento puedas
# ver a que base de datos y en que entorno estas a punto de conectarte,
# antes de que la migracion realmente ocurra.
print("------------------------------------------------------------")
print("Entorno seleccionado (APP_ENV): " + APP_ENV)
print("Base de datos destino (DB_NAME): " + settings.DB_NAME)
print("------------------------------------------------------------")

# ============================================================
# PASO 5: Verificacion de seguridad (assert de coherencia)
# ============================================================
# Si APP_ENV=test pero el nombre de la base no contiene "pruebas",
# algo esta mal configurado en .env.test y se detiene la ejecucion
# antes de tocar cualquier base de datos.
if APP_ENV == "test" and "pruebas" not in settings.DB_NAME:
    raise RuntimeError(
        "APP_ENV=test pero DB_NAME='" + settings.DB_NAME + "' "
        "no contiene la palabra 'pruebas'. Se detiene la ejecucion "
        "para evitar conectar por error a una base incorrecta."
    )

# Si APP_ENV=prod, se verifica lo contrario: que el nombre de la base
# NO sea el de pruebas, para evitar el error inverso.
if APP_ENV == "prod" and "pruebas" in settings.DB_NAME:
    raise RuntimeError(
        "APP_ENV=prod pero DB_NAME='" + settings.DB_NAME + "' "
        "contiene la palabra 'pruebas'. Se detiene la ejecucion "
        "porque esto parece un error de configuracion."
    )

config.set_main_option("sqlalchemy.url", DATABASE_URL)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Corre las migraciones en modo 'offline': genera el SQL sin
    necesidad de una conexion activa a la base de datos.
    Esta funcion no fue modificada respecto a la version original.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Corre las migraciones en modo 'online': abre una conexion real
    a la base de datos definida en sqlalchemy.url y aplica los cambios.
    Esta funcion no fue modificada respecto a la version original.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()