# app/modules/proveedores/schemas_proveedor.py
"""
Schemas para módulo de proveedores
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


# ===========================================================
# PROVEEDOR - SCHEMAS
# ===========================================================

class ProveedorBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=150, description="Nombre del proveedor")
    direccion: Optional[str] = Field(None, max_length=255, description="Dirección física")
    contacto: Optional[str] = Field(None, max_length=100, description="Persona de contacto")
    email: Optional[EmailStr] = Field(None, max_length=150, description="Correo electrónico")
    telefono1: Optional[str] = Field(None, max_length=20, description="Teléfono principal")
    telefono2: Optional[str] = Field(None, max_length=20, description="Teléfono secundario")
    observaciones: Optional[str] = Field(None, description="Observaciones adicionales")

class ProveedorCreate(ProveedorBase):
    pass

class ProveedorUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=150)
    direccion: Optional[str] = Field(None, max_length=255)
    contacto: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = Field(None, max_length=150)
    telefono1: Optional[str] = Field(None, max_length=20)
    telefono2: Optional[str] = Field(None, max_length=20)
    observaciones: Optional[str] = None
    activo: Optional[bool] = None

class ProveedorResponse(ProveedorBase):
    id: int
    activo: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class ProveedorListResponse(BaseModel):
    total: int
    proveedores: List[ProveedorResponse]


# ===========================================================
# MENSAJE GENÉRICO
# ===========================================================

class MessageResponse(BaseModel):
    message: str