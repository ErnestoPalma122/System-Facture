# app/modules/inventario/schemas_inventario.py
"""
Schemas para módulo de inventario: Ingreso, Items, EstadoItems, Movimiento, etc.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


# ===========================================================
# ESTADO ITEMS - SCHEMAS
# ===========================================================

class EstadoItemsBase(BaseModel):
    estado: str = Field(..., min_length=2, max_length=50, description="Nombre del estado")
    observaciones: str = Field(..., max_length=100, description="Explicación adicional del estado")

class EstadoItemsCreate(EstadoItemsBase):
    pass

class EstadoItemsUpdate(BaseModel):
    estado: Optional[str] = Field(None, min_length=2, max_length=50)
    observaciones: Optional[str] = Field(None, max_length=100)

class EstadoItemsResponse(EstadoItemsBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class EstadoItemsListResponse(BaseModel):
    total: int
    estados: List[EstadoItemsResponse]


# ===========================================================
# ITEMS - SCHEMAS
# ===========================================================

class ItemsBase(BaseModel):
    ingreso_id: int = Field(..., description="ID del ingreso")
    producto_id: int = Field(..., description="ID del producto")
    bodega_id: int = Field(..., description="ID de la bodega")
    estado_item_id: int = Field(..., description="ID del estado del item")
    serie: str = Field(..., max_length=100, description="Serie del producto")
    dte: Optional[str] = Field(None, max_length=50, description="DTE del item")
    dias_stock: int = Field(0, ge=0, description="Días de stock")
    
    # Campos de control de granel
    cantidad_inicial: int = Field(1, ge=1, description="Cantidad inicial (ej. 100 si es caja de 100)")
    cantidad_actual: int = Field(1, ge=0, description="Cantidad actual disponible")

class ItemsCreate(ItemsBase):
    pass

class ItemsUpdate(BaseModel):
    producto_id: Optional[int] = None
    bodega_id: Optional[int] = None
    estado_item_id: Optional[int] = None
    serie: Optional[str] = Field(None, max_length=100)
    dte: Optional[str] = Field(None, max_length=50)
    dias_stock: Optional[int] = Field(None, ge=0)
    cantidad_inicial: Optional[int] = Field(None, ge=1)
    cantidad_actual: Optional[int] = Field(None, ge=0)
    activo: Optional[bool] = None

class ItemsResponse(ItemsBase):
    id: int
    activo: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class ItemsListResponse(BaseModel):
    total: int
    items: List[ItemsResponse]


# ===========================================================
# INGRESO - SCHEMAS
# ===========================================================

class IngresoBase(BaseModel):
    proveedor_id: int = Field(..., description="ID del proveedor")
    usuario_id: int = Field(..., description="ID del usuario que registra")
    dte: str = Field(..., max_length=50, description="Número de DTE")
    sello: str = Field(..., max_length=100, description="Sello del DTE")
    codigo_generacion: str = Field(..., max_length=100, description="Código de generación")
    cotizacion: str = Field(..., max_length=50, description="Número de cotización")
    observaciones: str = Field(..., description="Observaciones del ingreso")
    estado_ingreso_id: int = Field(..., description="ID del estado del ingreso")

class IngresoCreate(IngresoBase):
    items: List[ItemsCreate] = Field(..., description="Lista de items a ingresar")

class IngresoUpdate(BaseModel):
    observaciones: Optional[str] = None
    estado_ingreso_id: Optional[int] = None
    activo: Optional[bool] = None

class IngresoResponse(IngresoBase):
    id: int
    fecha: datetime
    activo: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[ItemsResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

class IngresoListResponse(BaseModel):
    total: int
    ingresos: List[IngresoResponse]


# ===========================================================
# MOVIMIENTO - SCHEMAS
# ===========================================================

class MovimientoBase(BaseModel):
    item_id: int = Field(..., description="ID del item")
    tipo_movimiento_id: int = Field(..., description="ID del tipo de movimiento")
    usuario_id: int = Field(..., description="ID del usuario que realiza el movimiento")
    cantidad: int = Field(..., description="Cantidad movida")
    bodega_origen_id: Optional[int] = Field(None, description="Bodega de origen")
    bodega_destino_id: Optional[int] = Field(None, description="Bodega de destino")
    saldo_anterior: int = Field(..., description="Saldo antes del movimiento")
    saldo_nuevo: int = Field(..., description="Saldo después del movimiento")
    observaciones: Optional[str] = Field(None, description="Observaciones del movimiento")

class MovimientoCreate(MovimientoBase):
    pass

class MovimientoResponse(MovimientoBase):
    id: int
    fecha: datetime
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class MovimientoListResponse(BaseModel):
    total: int
    movimientos: List[MovimientoResponse]


# ===========================================================
# MENSAJE GENÉRICO
# ===========================================================

class MessageResponse(BaseModel):
    message: str