# app/modules/proveedores/models_proveedor.py
"""
Módulo de modelos de proveedores.
Contiene: Proveedor
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class Proveedor(Base):
    """Modelo para proveedores de la empresa"""
    __tablename__ = "proveedores"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(150), nullable=False, index=True)
    direccion = Column(String(255), nullable=True)
    contacto = Column(String(100), nullable=True)
    email = Column(String(150), nullable=True, index=True)
    telefono1 = Column(String(20), nullable=True)
    telefono2 = Column(String(20), nullable=True)
    observaciones = Column(Text, nullable=True)
    
    activo = Column(Boolean, default=True, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Proveedor(id={self.id}, nombre={self.nombre}, email={self.email})>"
    
