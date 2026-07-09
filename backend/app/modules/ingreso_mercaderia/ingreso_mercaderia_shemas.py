# app/modules/ingreso_mercaderia/ingreso_mercaderia_shemas.py
"""
Schemas para el módulo de ingreso de mercadería.
Define la estructura de datos para crear ingresos de inventario.
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime


# ===========================================================
# ITEMS - SCHEMAS
# ===========================================================

class ItemCreate(BaseModel):
    """Schema para crear un item de ingreso"""
    producto_id: int = Field(..., description="ID del producto", examples=[1])
    bodega_id: int = Field(..., description="ID de la bodega destino", examples=[2])
    series: List[str] = Field(
        ..., 
        min_length=1, 
        description="Lista de series del producto (cada serie genera un item)",
        examples=[["SER001", "SER002", "SER003"]]
    )
    dias_stock: Optional[int] = Field(
        0, 
        ge=0, 
        description="Días de stock del producto",
        examples=[30]
    )
    
    @field_validator('series')
    @classmethod
    def validar_series_no_vacias(cls, v):
        """Validar que las series no estén vacías"""
        if not v or len(v) == 0:
            raise ValueError('La lista de series no puede estar vacía')
        
        # Validar que cada serie sea un string no vacío
        series_limpias = []
        for serie in v:
            serie_limpia = serie.strip()
            if not serie_limpia:
                raise ValueError('Las series no pueden estar vacías')
            series_limpias.append(serie_limpia)
        
        # Validar que no haya series duplicadas
        if len(series_limpias) != len(set(series_limpias)):
            raise ValueError('No puede haber series duplicadas en el mismo producto')
        
        return series_limpias
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "producto_id": 1,
                "bodega_id": 2,
                "series": ["SER001", "SER002", "SER003"],
                "dias_stock": 30
            }
        }
    )


class ItemResponse(BaseModel):
    """Schema de respuesta para items"""
    id: int
    ingreso_id: int
    producto_id: int
    bodega_id: int
    estado_item_id: int  # ← Sin Optional
    serie: str  # ← Sin Optional
    dte: Optional[str] = None  # ← Este SÍ puede ser NULL (no lo asignas en el servicio)
    dias_stock: int  # ← Sin Optional
    activo: bool  # ← Sin Optional
    created_at: datetime  # ← Sin Optional
    updated_at: Optional[datetime] = None  # ← Este SÍ puede ser NULL
    
    model_config = ConfigDict(from_attributes=True)


# ===========================================================
# INGRESO - SCHEMAS
# ===========================================================

class IngresoMercaderiaCreate(BaseModel):
    """Schema principal para crear ingreso de mercadería"""
    proveedor_id: int = Field(..., description="ID del proveedor", examples=[1])
    dte: str = Field(..., max_length=50, description="DTE del documento", examples=["DTE-001"])
    sello: str = Field(..., max_length=100, description="Sello del documento", examples=["SELLO123"])
    cotizacion: str = Field(..., max_length=50, description="Número de cotización", examples=["COT-2026-001"])
    codigo_generacion: str = Field(..., max_length=100, description="Código de generación", examples=["GEN-001"])
    observaciones: str = Field(..., description="Observaciones del ingreso", examples=["Ingreso de productos electrónicos"])
    estado_ingreso_id: int = Field(
        8, 
        description="ID del estado de ingreso (default: 8 = COMPLETO PROCESADO)",
        examples=[8]
    )
    items: List[ItemCreate] = Field(
        ..., 
        min_length=1, 
        description="Lista de items del ingreso (mínimo 1 item)",
        examples=[[
            {
                "producto_id": 1,
                "bodega_id": 2,
                "series": ["SER001", "SER002"],
                "dias_stock": 0
            }
        ]]
    )
    
    @field_validator('items')
    @classmethod
    def validar_items_no_vacios(cls, v):
        """Validar que la lista de items no esté vacía"""
        if not v or len(v) == 0:
            raise ValueError('Debe incluir al menos un item en el ingreso')
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "proveedor_id": 1,
                "dte": "DTE-001",
                "sello": "SELLO123",
                "cotizacion": "COT-2026-001",
                "codigo_generacion": "GEN-001",
                "observaciones": "Ingreso de productos electrónicos",
                "estado_ingreso_id": 8,
                "items": [
                    {
                        "producto_id": 1,
                        "bodega_id": 2,
                        "series": ["SER001", "SER002", "SER003"],
                        "dias_stock": 30
                    },
                    {
                        "producto_id": 2,
                        "bodega_id": 2,
                        "series": ["SER004", "SER005"],
                        "dias_stock": 45
                    }
                ]
            }
        }
    )


class IngresoMercaderiaResponse(BaseModel):
    """Schema de respuesta para ingreso de mercadería"""
    id: int
    proveedor_id: int
    usuario_id: int  # ← NUEVO
    dte: str
    sello: str
    codigo_generacion: str
    cotizacion: str
    observaciones: str
    fecha: datetime
    estado_ingreso_id: int
    activo: bool
    items: List[ItemResponse] = []
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# ===========================================================
# MENSAJE GENÉRICO
# ===========================================================

class MessageResponse(BaseModel):
    """Schema para mensajes genéricos"""
    message: str
    data: Optional[dict] = None

