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
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)  # ← NUEVO
    dte = Column(String(50), nullable=False, index=True)
    sello = Column(String(100), nullable=False)
    codigo_generacion = Column(String(100), nullable=False, index=True)
    cotizacion = Column(String(50), nullable=False)
    observaciones = Column(Text, nullable=False)
    
    # Fecha automática de creación
    fecha = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    activo = Column(Boolean, default=True, index=True)
    estado_ingreso_id = Column(Integer, ForeignKey("estado_ingreso.id"), nullable=False, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    proveedor = relationship("Proveedor")
    usuario = relationship("Usuario")  # ← NUEVO
    items = relationship("Items", back_populates="ingreso", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Ingreso(id={self.id}, proveedor_id={self.proveedor_id}, usuario_id={self.usuario_id}, dte={self.dte})>"


class EstadoItems(Base):
    """Modelo para estados de items de inventario"""
    __tablename__ = "estado_items"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    #DEFAULT: 1 = Ejemplo: Disponible
    estado = Column(String(50), nullable=False, unique=True, index=True)
    #Explicaciones adicionales sobre el estado del item, por ejemplo: 
    observaciones = Column(String(100), nullable=False, unique=True, index=True)


    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    items = relationship("Items", back_populates="estado_item")
    
    def __repr__(self):
        return f"<EstadoItems(id={self.id}, estado={self.estado})>"


class Items(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ingreso_id = Column(Integer, ForeignKey("ingresos.id"), nullable=False, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False, index=True)
    bodega_id = Column(Integer, ForeignKey("bodegas.id"), nullable=False, index=True)
    estado_item_id = Column(Integer, ForeignKey("estado_items.id"), nullable=False, index=True)
    
    serie = Column(String(100), nullable=False, index=True)
    dte = Column(String(50), nullable=True)
    dias_stock = Column(Integer, nullable=False, default=0)

    # ← NUEVO: control de granel
    cantidad_inicial = Column(Integer, nullable=False, default=1)  # qty_contenido del producto, o 1 si no es granel
    cantidad_actual = Column(Integer, nullable=False, default=1)   # se descuenta con cada salida
    
    activo = Column(Boolean, default=True, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    ingreso = relationship("Ingreso", back_populates="items")
    producto = relationship("Producto")
    bodega = relationship("Bodega")
    estado_item = relationship("EstadoItems", back_populates="items")
    movimientos = relationship("Movimiento", back_populates="item", cascade="all, delete-orphan")  # ← NUEVO
    
    def __repr__(self):
        return f"<Items(id={self.id}, ingreso_id={self.ingreso_id}, producto_id={self.producto_id})>"
    
class Estado_Ingreso(Base):
    """Modelo para estados de ingreso"""
    __tablename__ = "estado_ingreso"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre_estado = Column(String(100), nullable=True, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class TiposMovimiento(Base):
    """Catálogo de tipos de movimiento de inventario"""
    __tablename__ = "tipos_movimiento"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Ejemplos: INGRESO, TRASLADO, SALIDA_VENTA, AJUSTE
    nombre = Column(String(50), nullable=False, unique=True, index=True)
    observaciones = Column(String(150), nullable=True)

    # Indica si este tipo SUMA o RESTA cantidad_actual/stock al aplicarse
    afecta_suma = Column(Boolean, nullable=False, default=False)

    activo = Column(Boolean, default=True, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    movimientos = relationship("Movimiento", back_populates="tipo_movimiento")

    def __repr__(self):
        return f"<TiposMovimiento(id={self.id}, nombre={self.nombre})>"
    
    
class Movimiento(Base):
    """Auditoría de todos los movimientos de inventario (ingresos, traslados, salidas)"""
    __tablename__ = "movimientos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    item_id = Column(Integer, ForeignKey("items.id"), nullable=False, index=True)
    tipo_movimiento_id = Column(Integer, ForeignKey("tipos_movimiento.id"), nullable=False, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)

    cantidad = Column(Integer, nullable=False)  # cuánto se movió (1 = unidad completa, 7 = granel)

    # Trazabilidad de bodega (traslados usan ambos, ingreso/salida solo uno)
    bodega_origen_id = Column(Integer, ForeignKey("bodegas.id"), nullable=True, index=True)
    bodega_destino_id = Column(Integer, ForeignKey("bodegas.id"), nullable=True, index=True)

    # Referencia a venta, si aplica (nullable porque no todo movimiento es una venta)
    #venta_id = Column(Integer, ForeignKey("ventas.id"), nullable=True, index=True)

    # Snapshot del saldo del item antes/después, para auditoría sin necesidad de recalcular
    saldo_anterior = Column(Integer, nullable=False)
    saldo_nuevo = Column(Integer, nullable=False)

    observaciones = Column(Text, nullable=True)

    fecha = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    item = relationship("Items", back_populates="movimientos")
    tipo_movimiento = relationship("TiposMovimiento", back_populates="movimientos")
    usuario = relationship("Usuario")
    bodega_origen = relationship("Bodega", foreign_keys=[bodega_origen_id])
    bodega_destino = relationship("Bodega", foreign_keys=[bodega_destino_id])

    def __repr__(self):
        return f"<Movimiento(id={self.id}, item_id={self.item_id}, tipo={self.tipo_movimiento_id}, cantidad={self.cantidad})>"
