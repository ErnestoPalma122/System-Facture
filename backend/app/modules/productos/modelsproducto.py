# app/modules/productos/modelsproducto.py
"""
Módulo de modelos de productos.
Contiene: Producto, Categoria, Precio, Stock, Bodega
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Text, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum
import logging
from datetime import datetime
from decimal import Decimal

logger = logging.getLogger(__name__)


# ===========================================================
# ENUMS
# ===========================================================

class TipoProducto(enum.Enum):
    """Tipo de producto: Bien físico o Servicio"""
    BIEN = "BIEN"
    SERVICIO = "SERVICIO"


# ===========================================================
# MODELOS
# ===========================================================

class Categoria(Base):
    """Modelo para categorías de productos"""
    __tablename__ = "categorias"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False, unique=True, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    productos = relationship("Producto", back_populates="categoria")
    
    def __repr__(self):
        return f"<Categoria(id={self.id}, nombre={self.nombre})>"


class Bodega(Base):
    """Modelo para bodegas/almacenes"""
    __tablename__ = "bodegas"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False, unique=True, index=True)
    direccion = Column(String(255), nullable=True)
    ubicacion = Column(String(150), nullable=True)
    telefono = Column(String(20), nullable=True)
    
    # Encargado de la bodega (relación con usuarios)
    encargado_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True, index=True)
    
    activo = Column(Boolean, default=True, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    encargado = relationship("Usuario", foreign_keys=[encargado_id])
    productos = relationship("Producto", back_populates="bodega")
    stocks = relationship("Stock", back_populates="bodega")
    
    def __repr__(self):
        return f"<Bodega(id={self.id}, nombre={self.nombre}, activo={self.activo})>"


class Precio(Base):
    """Modelo para precios de productos (múltiples tipos de precios)"""
    __tablename__ = "precios"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False, unique=True, index=True)
    
    # Tipos de precios (usando Numeric para precisión monetaria)
    precio_base = Column(Numeric(10, 2), nullable=False, default=0)
    precio_costo = Column(Numeric(10, 2), nullable=False, default=0)
    precio_publico = Column(Numeric(10, 2), nullable=False, default=0)
    precio_iva = Column(Numeric(10, 2), nullable=False, default=0)
    precio_promo = Column(Numeric(10, 2), nullable=True, default=0)
    precio_descuento = Column(Numeric(10, 2), nullable=True, default=0)
    
    activo = Column(Boolean, default=True, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    producto = relationship("Producto", back_populates="precio")
    
    def __repr__(self):
        return f"<Precio(id={self.id}, producto_id={self.producto_id}, precio_publico={self.precio_publico})>"


class Stock(Base):
    """Modelo para stock de productos (cantidad por bodega)"""
    __tablename__ = "stocks"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False, index=True)
    bodega_id = Column(Integer, ForeignKey("bodegas.id"), nullable=False, index=True)
    
    cantidad = Column(Integer, nullable=False, default=0)
    cantidad_minima = Column(Integer, nullable=False, default=0)  # Para alertas de stock bajo
    
    activo = Column(Boolean, default=True, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    producto = relationship("Producto", back_populates="stocks")
    bodega = relationship("Bodega", back_populates="stocks")
    
    def __repr__(self):
        return f"<Stock(id={self.id}, producto_id={self.producto_id}, bodega_id={self.bodega_id}, cantidad={self.cantidad})>"


class Producto(Base):
    """Modelo principal de productos"""
    __tablename__ = "productos"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo = Column(String(50), nullable=False, unique=True, index=True)  # ← AGREGAR
    nombre = Column(String(150), nullable=False, index=True)
    descripcion = Column(Text, nullable=True)
    marca = Column(String(100), nullable=True)
    
    # Tipo: BIEN o SERVICIO
    tipo = Column(
        Enum(TipoProducto),
        nullable=False,
        default=TipoProducto.BIEN,
        index=True
    )
    
    # Relaciones con otras tablas
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=True, index=True)
    bodega_id = Column(Integer, ForeignKey("bodegas.id"), nullable=True, index=True)
    
    activo = Column(Boolean, default=True, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    categoria = relationship("Categoria", back_populates="productos")
    bodega = relationship("Bodega", back_populates="productos")
    precio = relationship("Precio", back_populates="producto", uselist=False, cascade="all, delete-orphan")
    stocks = relationship("Stock", back_populates="producto", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Producto(id={self.id}, codigo={self.codigo}, nombre={self.nombre}, tipo={self.tipo})>"
    
    def stock_total(self) -> int:
        """Calcula el stock total del producto en todas las bodegas"""
        if not self.stocks:
            return 0
        return sum(stock.cantidad for stock in self.stocks if stock.activo)
    
    def tiene_stock_suficiente(self, cantidad_solicitada: int) -> bool:
        """Verifica si hay stock suficiente para una venta"""
        return self.stock_total() >= cantidad_solicitada