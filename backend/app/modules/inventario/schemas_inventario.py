# app/modules/inventario/schemas_inventario.py
"""
Schemas para módulo de inventario: Ingreso, Items, EstadoItems
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


# ===========================================================
# ESTADO ITEMS - SCHEMAS
# ===========================================================

class EstadoItemsBase(BaseModel):
    estado: str = Field(..., min_length=2, max_length=50, description="Nombre del estado")
    descripcion: Optional[str] = Field(None, max_length=200, description="Descripción del estado")

class EstadoItemsCreate(EstadoItemsBase):
    pass

class EstadoItemsUpdate(BaseModel):
    estado: Optional[str] = Field(None, min_length=2, max_length=50)
    descripcion: Optional[str] = Field(None, max_length=200)
    activo: Optional[bool] = None

class EstadoItemsResponse(EstadoItemsBase):
    id: int
    activo: bool
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
    estado_item_id: Optional[int] = Field(None, description="ID del estado del item")
    serie: Optional[str] = Field(None, max_length=100, description="Serie del producto")
    dte: Optional[str] = Field(None, max_length=50, description="DTE del item")
    dias_stock: Optional[int] = Field(0, ge=0, description="Días de stock")

class ItemsCreate(ItemsBase):
    pass

class ItemsUpdate(BaseModel):
    producto_id: Optional[int] = None
    bodega_id: Optional[int] = None
    estado_item_id: Optional[int] = None
    serie: Optional[str] = Field(None, max_length=100)
    dte: Optional[str] = Field(None, max_length=50)
    dias_stock: Optional[int] = Field(None, ge=0)
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
    dte: Optional[str] = Field(None, max_length=50, description="DTE del ingreso")
    sello: Optional[str] = Field(None, max_length=100, description="Sello del documento")
    codigo_origen: Optional[str] = Field(None, max_length=100, description="Código de origen")
    cotizacion: Optional[str] = Field(None, max_length=50, description="Número de cotización")
    observaciones: Optional[str] = Field(None, description="Observaciones del ingreso")

class IngresoCreate(IngresoBase):
    items: List[ItemsCreate] = Field(..., description="Lista de items del ingreso")

class IngresoUpdate(BaseModel):
    proveedor_id: Optional[int] = None
    dte: Optional[str] = Field(None, max_length=50)
    sello: Optional[str] = Field(None, max_length=100)
    codigo_origen: Optional[str] = Field(None, max_length=100)
    cotizacion: Optional[str] = Field(None, max_length=50)
    observaciones: Optional[str] = None
    activo: Optional[bool] = None

class IngresoResponse(IngresoBase):
    id: int
    fecha: datetime
    activo: bool
    items: List[ItemsResponse] = []
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class IngresoListResponse(BaseModel):
    total: int
    ingresos: List[IngresoResponse]


# ===========================================================
# MENSAJE GENÉRICO
# ===========================================================

class MessageResponse(BaseModel):
    message: str