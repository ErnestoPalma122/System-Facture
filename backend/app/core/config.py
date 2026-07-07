#C:\Users\PC\Desktop\Factu\backend\app\core\config.py
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

class Settings:
    # ===========================================================
    # BASE DE DATOS (con valores por defecto)
    # ===========================================================
    #manda a llamar la inormacion de .env, luego si no encuentra informacion 
    #con la variable que esta llamando, utiliza la siguiente informacion luego de la coma. 
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_NAME: str = os.getenv("DB_NAME", "negocios_informaticos")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))  # ← Valor por defecto

    # ===========================================================
    # SEGURIDAD
    # ===========================================================
    SECRET_KEY: str = os.getenv("SECRET_KEY", "cambia_esta_clave_en_produccion")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    
    # ===========================================================
    # REDIS (OPCIONAL)
    # ===========================================================
    REDIS_URL: str = os.getenv("REDIS_URL", "")
    
    # ===========================================================
    # RATE LIMITING
    # ===========================================================
    RATE_LIMIT_DEFAULT: int = int(os.getenv("RATE_LIMIT_DEFAULT", "100"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
    RATE_LIMIT_AUTH: int = int(os.getenv("RATE_LIMIT_AUTH", "5"))
    RATE_LIMIT_AUTH_WINDOW: int = int(os.getenv("RATE_LIMIT_AUTH_WINDOW", "60"))
    
    # ===========================================================
    # URL DE BASE DE DATOS (propiedad calculada)
    # ===========================================================
    #al pareces esto: (@property), convierte un metodo a propiedad
    #entonces (DATABASE_URL) se leeria como un atributo de solo lectura. 
    @property
    #Al ejecutarse (settings.DATABASE_URL) debuelve un string 
    #con los valores(Self)
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
#Creacion de instancia, en otras palabras es una variable que guarda
# la clase  Settings.
settings = Settings()

#Este archivo existe para mayor control ya que es el unico 
# lugar que centraliza las configuraciones, hace facil de 
# mantener y de cambiar de entorno(desarrollo, pruebas o producción)
#sin modificar el codigo fuente