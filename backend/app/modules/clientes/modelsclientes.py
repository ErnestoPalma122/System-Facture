# app/modules/clientes/modelsclientes.py
"""
Módulo de modelos de clientes.
Contiene la estructura de datos para la gestión de clientes (facturación electrónica).
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import logging

logger = logging.getLogger(__name__)


class Cliente(Base):
    """Modelo principal para la gestión de clientes"""
    __tablename__ = "clientes"
    
    # Identificador único
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Datos generales (Opcionales según requerimiento)
    nombre_comercial = Column(String(150), nullable=True)
    nombre = Column(String(150), nullable=True)
    
    # Datos de identificación fiscal (Opcionales)
    dui = Column(String(20), nullable=True, index=True)
    nit = Column(String(30), nullable=True, index=True)
    nrc = Column(String(20), nullable=True, index=True)
    pasaporte = Column(String(50), nullable=True)
    
    # Datos de actividad económica (AHORA OPCIONALES)
    cod_actividad = Column(String(50), nullable=True)
    desc_actividad = Column(String(255), nullable=True)
    
    # Datos de ubicación geográfica (Obligatorios)
    cod_departamento = Column(String(50), nullable=False)
    desc_departamento = Column(String(100), nullable=False)
    
    cod_municipio = Column(String(50), nullable=False)
    desc_municipio = Column(String(100), nullable=False)
    
    cod_distrito = Column(String(50), nullable=False)
    desc_distrito = Column(String(100), nullable=False)
    
    # Tipo de persona (Obligatorio)
    cod_tipopersona = Column(String(50), nullable=False)
    desc_tipopersona = Column(String(100), nullable=False)
    
    # Configuración fiscal (Obligatorios)
    percep_iva = Column(Boolean, default=False, nullable=False)  # Corregido de 'persep' a 'percep'
    iva = Column(Boolean, default=False, nullable=False)
    
    # Datos de contacto
    telefono = Column(String(20), nullable=True)
    correo = Column(String(150), nullable=False, unique=True, index=True)
    
    # Datos adicionales
    observaciones = Column(Text, nullable=True)
    
    # Campos de auditoría y estado
    activo = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())