# app/modules/inventario/models_inventario.py
"""
Módulo de modelos de inventario.
Contiene: Ingreso, Items, EstadoItems
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class Ingreso(Base):
    """Modelo para ingresos de inventario"""
    __tablename__ = "ingresos"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    proveedor_id = Column(Integer, ForeignKey("proveedores.id"), nullable=False, index=True)
    dte = Column(String(50), nullable=True, index=True)
    sello = Column(String(100), nullable=True)
    codigo_origen = Column(String(100), nullable=True, index=True)
    cotizacion = Column(String(50), nullable=True)
    observaciones = Column(Text, nullable=True)
    
    # Fecha automática de creación
    fecha = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    activo = Column(Boolean, default=True, index=True)

    estado_ingreso_id = Column(Integer, ForeignKey("estado_ingreso.id"), nullable=False, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    proveedor = relationship("Proveedor")
    items = relationship("Items", back_populates="ingreso", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Ingreso(id={self.id}, proveedor_id={self.proveedor_id}, dte={self.dte})>"


class EstadoItems(Base):
    """Modelo para estados de items de inventario"""
    __tablename__ = "estado_items"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    estado = Column(String(50), nullable=False, unique=True, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    items = relationship("Items", back_populates="estado_item")
    
    def __repr__(self):
        return f"<EstadoItems(id={self.id}, estado={self.estado})>"


class Items(Base):
    """Modelo para items de ingreso de inventario"""
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ingreso_id = Column(Integer, ForeignKey("ingresos.id"), nullable=False, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False, index=True)
    bodega_id = Column(Integer, ForeignKey("bodegas.id"), nullable=False, index=True)
    estado_item_id = Column(Integer, ForeignKey("estado_items.id"), nullable=True, index=True)
    
    serie = Column(String(100), nullable=True, index=True)
    dte = Column(String(50), nullable=True)
    dias_stock = Column(Integer, nullable=True, default=0)
    
    activo = Column(Boolean, default=True, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    ingreso = relationship("Ingreso", back_populates="items")
    producto = relationship("Producto")
    bodega = relationship("Bodega")
    estado_item = relationship("EstadoItems", back_populates="items")
    
    def __repr__(self):
        return f"<Items(id={self.id}, ingreso_id={self.ingreso_id}, producto_id={self.producto_id})>"
    
class Estado_Ingreso(Base):
    """Modelo para estados de ingreso"""
    __tablename__ = "estado_ingreso"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre_estado = Column(String(100), nullable=True, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

