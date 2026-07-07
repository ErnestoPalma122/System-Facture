# app/modules/productos/schemasproducto.py
"""
Schemas para módulos de productos: Producto, Precio, Categoria, Stock, Bodega
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
from decimal import Decimal


# ===========================================================
# ENUMS
# ===========================================================

class TipoProductoEnum(str, Enum):
    BIEN = "BIEN"
    SERVICIO = "SERVICIO"


# ===========================================================
# CATEGORIA - SCHEMAS
# ===========================================================

class CategoriaBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100, description="Nombre de la categoría")

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)

class CategoriaResponse(CategoriaBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class CategoriaListResponse(BaseModel):
    total: int
    categorias: List[CategoriaResponse]


# ===========================================================
# BODEGA - SCHEMAS
# ===========================================================

class BodegaBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100, description="Nombre de la bodega")
    direccion: Optional[str] = Field(None, max_length=255, description="Dirección física")
    ubicacion: Optional[str] = Field(None, max_length=150, description="Ubicación/coordenadas")
    telefono: Optional[str] = Field(None, max_length=20, description="Teléfono de contacto")
    encargado_id: Optional[int] = Field(None, description="ID del usuario encargado")

class BodegaCreate(BodegaBase):
    pass

class BodegaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    direccion: Optional[str] = Field(None, max_length=255)
    ubicacion: Optional[str] = Field(None, max_length=150)
    telefono: Optional[str] = Field(None, max_length=20)
    encargado_id: Optional[int] = None
    activo: Optional[bool] = None

class BodegaResponse(BodegaBase):
    id: int
    activo: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class BodegaListResponse(BaseModel):
    total: int
    bodegas: List[BodegaResponse]


# ===========================================================
# PRECIO - SCHEMAS
# ===========================================================

class PrecioBase(BaseModel):
    precio_base: Decimal = Field(..., ge=0, description="Precio base del producto")
    precio_costo: Decimal = Field(..., ge=0, description="Precio de costo")
    precio_publico: Decimal = Field(..., ge=0, description="Precio público de venta")
    precio_iva: Decimal = Field(..., ge=0, description="Precio con IVA incluido")
    precio_promo: Optional[Decimal] = Field(0, ge=0, description="Precio en promoción")
    precio_descuento: Optional[Decimal] = Field(0, ge=0, description="Precio con descuento")

class PrecioCreate(PrecioBase):
    pass

class PrecioUpdate(BaseModel):
    precio_base: Optional[Decimal] = Field(None, ge=0)
    precio_costo: Optional[Decimal] = Field(None, ge=0)
    precio_publico: Optional[Decimal] = Field(None, ge=0)
    precio_iva: Optional[Decimal] = Field(None, ge=0)
    precio_promo: Optional[Decimal] = Field(None, ge=0)
    precio_descuento: Optional[Decimal] = Field(None, ge=0)
    activo: Optional[bool] = None

class PrecioResponse(PrecioBase):
    id: int
    producto_id: int
    activo: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# ===========================================================
# STOCK - SCHEMAS
# ===========================================================

class StockBase(BaseModel):
    producto_id: int = Field(..., description="ID del producto")
    bodega_id: int = Field(..., description="ID de la bodega")
    cantidad: int = Field(..., ge=0, description="Cantidad en stock")
    cantidad_minima: int = Field(0, ge=0, description="Stock mínimo para alertas")

class StockCreate(StockBase):
    pass

class StockUpdate(BaseModel):
    cantidad: Optional[int] = Field(None, ge=0)
    cantidad_minima: Optional[int] = Field(None, ge=0)
    activo: Optional[bool] = None

class StockResponse(StockBase):
    id: int
    activo: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class StockListResponse(BaseModel):
    total: int
    stocks: List[StockResponse]


# ===========================================================
# PRODUCTO - SCHEMAS (CON CÓDIGO)
# ===========================================================

class ProductoBase(BaseModel):
    codigo: str = Field(..., min_length=2, max_length=50, description="Código único del producto")
    nombre: str = Field(..., min_length=2, max_length=150, description="Nombre del producto")
    descripcion: Optional[str] = Field(None, description="Descripción detallada")
    marca: Optional[str] = Field(None, max_length=100, description="Marca del producto")
    tipo: TipoProductoEnum = Field(TipoProductoEnum.BIEN, description="Tipo: BIEN o SERVICIO")
    categoria_id: Optional[int] = Field(None, description="ID de la categoría")
    bodega_id: Optional[int] = Field(None, description="ID de la bodega principal")

class ProductoCreate(ProductoBase):
    precio: PrecioCreate = Field(..., description="Precios del producto")

class ProductoUpdate(BaseModel):
    codigo: Optional[str] = Field(None, min_length=2, max_length=50)
    nombre: Optional[str] = Field(None, min_length=2, max_length=150)
    descripcion: Optional[str] = None
    marca: Optional[str] = Field(None, max_length=100)
    tipo: Optional[TipoProductoEnum] = None
    categoria_id: Optional[int] = None
    bodega_id: Optional[int] = None
    activo: Optional[bool] = None

class ProductoResponse(ProductoBase):
    id: int
    activo: bool
    precio: Optional[PrecioResponse] = None
    stocks: List[StockResponse] = []
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @field_validator('tipo', mode='before')
    @classmethod
    def convert_tipo_to_upper(cls, v):
        if isinstance(v, Enum):
            return v.value.upper()
        if isinstance(v, str):
            return v.upper()
        return v
    
    model_config = ConfigDict(from_attributes=True)

class ProductoListResponse(BaseModel):
    total: int
    productos: List[ProductoResponse]


# ===========================================================
# MENSAJE GENÉRICO
# ===========================================================

class MessageResponse(BaseModel):
    message: str