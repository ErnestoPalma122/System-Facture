# app/modules/clientes/schemasclientes.py
"""
Schemas para el módulo de clientes.
Define la estructura de validación de datos de entrada y salida usando Pydantic.
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


# ===========================================================
# CLIENTE - SCHEMAS
# ===========================================================

class ClienteBase(BaseModel):
    """Campos base compartidos para creación y actualización de clientes"""
    
    nombre_comercial: Optional[str] = Field(
        None, 
        max_length=150, 
        description="Nombre comercial de la empresa",
        examples=["Distribuidora El Sol S.A. de C.V."]
    )
    nombre: Optional[str] = Field(
        None, 
        max_length=150, 
        description="Nombre de la persona o razón social",
        examples=["Juan Alberto Pérez García"]
    )
    dui: Optional[str] = Field(
        None, 
        max_length=20, 
        description="Documento Único de Identidad",
        examples=["000000000"]
    )
    nit: Optional[str] = Field(
        None, 
        max_length=30, 
        description="Número de Identificación Tributaria",
        examples=["00000000000000"]
    )
    nrc: Optional[str] = Field(
        None, 
        max_length=20, 
        description="Número de Registro de Contribuyente",
        examples=["0000000"]
    )
    pasaporte: Optional[str] = Field(
        None, 
        max_length=50, 
        description="Número de pasaporte",
        examples=["A12345678"]
    )
    
    # Datos de actividad (AHORA OPCIONALES)
    cod_actividad: Optional[str] = Field(
        None, 
        max_length=50, 
        description="Código de actividad económica",
        examples=["01111"]
    )
    desc_actividad: Optional[str] = Field(
        None, 
        max_length=255, 
        description="Descripción de la actividad económica",
        examples=["Cultivo de cereales excepto arroz y para forrajes"]
    )
    
    # Datos de ubicación (Obligatorios)
    cod_departamento: str = Field(
        ..., 
        max_length=50, 
        description="Código del departamento",
        examples=["06"]
    )
    desc_departamento: str = Field(
        ..., 
        max_length=100, 
        description="Descripción del departamento",
        examples=["San Salvador"]
    )
    cod_municipio: str = Field(
        ..., 
        max_length=50, 
        description="Código del municipio",
        examples=["21"]
    )
    desc_municipio: str = Field(
        ..., 
        max_length=100, 
        description="Descripción del municipio",
        examples=["SAN SALVADOR OESTE"]
    )
    cod_distrito: str = Field(
        ..., 
        max_length=50, 
        description="Código del distrito",
        examples=["02"]
    )
    desc_distrito: str = Field(
        ..., 
        max_length=100, 
        description="Descripción del distrito",
        examples=["APOPA"]
    )
    
    # Tipo de persona (Obligatorio)
    cod_tipopersona: str = Field(
        ..., 
        max_length=50, 
        description="Código del tipo de persona",
        examples=["1"]
    )
    desc_tipopersona: str = Field(
        ..., 
        max_length=100, 
        description="Descripción del tipo de persona",
        examples=["Persona Jurídica"]
    )
    
    # Configuración fiscal (Obligatorios)
    percep_iva: bool = Field(
        False, 
        description="¿Sujeto a percepción de IVA?",
        examples=[False]
    )
    iva: bool = Field(
        False, 
        description="¿Sujeto a IVA?",
        examples=[True]
    )
    
    # Contacto
    telefono: Optional[str] = Field(
        None, 
        max_length=20, 
        description="Número de teléfono",
        examples=["+504 2222-3333"]
    )
    correo: EmailStr = Field(
        ..., 
        max_length=150, 
        description="Correo electrónico (único)",
        examples=["facturacion@empresa.com.sv"]
    )
    observaciones: Optional[str] = Field(
        None, 
        description="Observaciones adicionales",
        examples=["Cliente preferente, pago a 30 días"]
    )


class ClienteCreate(ClienteBase):
    """Schema para crear un nuevo cliente (hereda la opcionalidad de ClienteBase)"""
    pass


class ClienteUpdate(BaseModel):
    """Schema para actualizar un cliente (todos los campos son opcionales)"""
    nombre_comercial: Optional[str] = Field(None, max_length=150, examples=["Nuevo Nombre Comercial S.A."])
    nombre: Optional[str] = Field(None, max_length=150, examples=["Nuevo Nombre S.A."])
    dui: Optional[str] = Field(None, max_length=20, examples=["11111111-1"])
    nit: Optional[str] = Field(None, max_length=30, examples=["1111-111111-111-1"])
    nrc: Optional[str] = Field(None, max_length=20, examples=["111111-1"])
    pasaporte: Optional[str] = Field(None, max_length=50, examples=["B98765432"])
    
    # Ahora también opcionales en la actualización
    cod_actividad: Optional[str] = Field(None, max_length=50, examples=["0112"])
    desc_actividad: Optional[str] = Field(None, max_length=255, examples=["Cultivo de hortalizas"])
    
    cod_departamento: Optional[str] = Field(None, max_length=50, examples=["12"])
    desc_departamento: Optional[str] = Field(None, max_length=100, examples=["La Libertad"])
    cod_municipio: Optional[str] = Field(None, max_length=50, examples=["1201"])
    desc_municipio: Optional[str] = Field(None, max_length=100, examples=["Antiguo Cuscatlán"])
    cod_distrito: Optional[str] = Field(None, max_length=50, examples=["120101"])
    desc_distrito: Optional[str] = Field(None, max_length=100, examples=["Distrito 1"])
    cod_tipopersona: Optional[str] = Field(None, max_length=50, examples=["2"])
    desc_tipopersona: Optional[str] = Field(None, max_length=100, examples=["Persona Natural"])
    percep_iva: Optional[bool] = Field(None, examples=[True])
    iva: Optional[bool] = Field(None, examples=[False])
    telefono: Optional[str] = Field(None, max_length=20, examples=["+504 9999-8888"])
    correo: Optional[EmailStr] = Field(None, max_length=150, examples=["nuevo@empresa.com.sv"])
    observaciones: Optional[str] = Field(None, examples=["Actualización de datos fiscales"])
    activo: Optional[bool] = Field(None, examples=[True])


class ClienteResponse(ClienteBase):
    """Schema de respuesta que incluye campos generados por la base de datos"""
    id: int = Field(..., examples=[1])
    activo: bool = Field(..., examples=[True])
    created_at: datetime = Field(..., examples=["2026-07-10T15:30:00-06:00"])
    updated_at: Optional[datetime] = Field(None, examples=["2026-07-10T15:30:00-06:00"])
    
    model_config = ConfigDict(from_attributes=True)


class ClienteListResponse(BaseModel):
    """Schema para respuestas paginadas de lista de clientes"""
    total: int = Field(..., examples=[150])
    clientes: List[ClienteResponse]


class MessageResponse(BaseModel):
    """Schema para mensajes genéricos de éxito o error"""
    message: str = Field(..., examples=["Operación realizada exitosamente"])
    data: Optional[dict] = None