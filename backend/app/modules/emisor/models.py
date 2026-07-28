# app/modules/emisor/models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.core.database import Base
import logging

logger = logging.getLogger(__name__)

class Emisor(Base):
    """
    Modelo para la configuración del Emisor (Datos de la empresa).
    TODOS los campos son OBLIGATORIOS para garantizar la validez fiscal.
    """
    __tablename__ = "emisor"
    
    # Identificador
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Datos Fiscales Principales (OBLIGATORIOS)
    nit = Column(String(17), nullable=False, unique=True, index=True)
    nrc = Column(String(8), nullable=False)
    nombre = Column(String(250), nullable=False)
    nombre_comercial = Column(String(150), nullable=False) # Ahora obligatorio
    
    # Actividad Económica (OBLIGATORIOS)
    cod_actividad = Column(String(6), nullable=False)
    desc_actividad = Column(String(150), nullable=False)
    
    # Dirección (OBLIGATORIOS)
    cod_departamento = Column(String(50), nullable=False)
    desc_departamento = Column(String(50), nullable=False)
    cod_municipio = Column(String(50), nullable=False)
    desc_municipio = Column(String(50), nullable=False)
    cod_distrito = Column(String(50), nullable=False)
    desc_distrito = Column(String(50), nullable=False)
    dirr_complemento = Column(String(200), nullable=False)
    
    # Datos de Contacto (OBLIGATORIOS)
    telefono = Column(String(30), nullable=False)
    correo = Column(String(100), nullable=False)
    correo_interno = Column(String(100), nullable=False)

    
    # Códigos internos del contribuyente (OBLIGATORIOS)
    cod_estable = Column(String(4), nullable=False)
    cod_punto_venta = Column(String(15), nullable=False)
    
    # Auditoría
    activo = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

