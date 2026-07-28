# app/modules/emisor/schemas.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# ===========================================================
# SCHEMAS ANIDADOS (Para que el frontend envíe la dirección agrupada)
# ===========================================================

class DireccionEmisor(BaseModel):
    cod_departamento: str = Field(..., description="Código del Departamento (Catálogo Hacienda)")
    desc_departamento: str = Field(..., description="Descripción del Departamento")
    cod_municipio: str = Field(..., description="Código del Municipio (Catálogo Hacienda)")
    desc_municipio: str = Field(..., description="Descripción del Municipio")
    cod_distrito: str = Field(..., description="Código del Distrito (Catálogo Hacienda)")
    desc_distrito: str = Field(..., description="Descripción del Distrito")
    complemento: str = Field(..., min_length=1, max_length=200, description="Detalle de la dirección (calle, casa, etc.)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "cod_departamento": "01",
                "desc_departamento": "Ahuachapán",
                "cod_municipio": "0101",
                "desc_municipio": "Ahuachapán",
                "cod_distrito": "010101",
                "desc_distrito": "Ahuachapán",
                "complemento": "Barrio El Calvario, Casa #123"
            }
        }
    }


class EmisorBase(BaseModel):
    """Campos base con validaciones estrictas. TODOS son obligatorios."""
    nit: str = Field(..., description="NIT del Emisor (ej: 0000-000000-000-0)")
    nrc: str = Field(..., min_length=2, max_length=8, description="NRC del Emisor")
    nombre: str = Field(..., min_length=1, max_length=250, description="Nombre o Razón Social")
    nombre_comercial: str = Field(..., min_length=1, max_length=150, description="Nombre Comercial")
    cod_actividad: str = Field(..., min_length=5, max_length=6, description="Código de Actividad Económica")
    desc_actividad: str = Field(..., min_length=5, max_length=150, description="Descripción de Actividad")
    direccion: DireccionEmisor
    telefono: str = Field(..., min_length=8, max_length=30, description="Teléfono")
    correo: EmailStr = Field(..., min_length=6, max_length=100, description="Correo electrónico fiscal (para DTE)")
    correo_interno: EmailStr = Field(..., min_length=6, max_length=100, description="Correo electrónico interno (para notificaciones del sistema)")
    cod_estable: str = Field(..., min_length=2, max_length=4, description="Código de Establecimiento")
    cod_punto_venta: str = Field(..., min_length=1, max_length=15, description="Código de Punto de Venta")

    model_config = {
        "json_schema_extra": {
            "example": {
                "nit": "0614-120589-101-1",
                "nrc": "123456",
                "nombre": "Negocios Informáticos S.A. de C.V.",
                "nombre_comercial": "FactuSV",
                "cod_actividad": "620100",
                "desc_actividad": "Programación informática",
                "direccion": {
                    "cod_departamento": "11",
                    "desc_departamento": "San Salvador",
                    "cod_municipio": "1101",
                    "desc_municipio": "San Salvador",
                    "cod_distrito": "110101",
                    "desc_distrito": "San Salvador",
                    "complemento": "Col. Escalón, Calle El Progreso #456"
                },
                "telefono": "2222-3333",
                "correo": "facturacion@negociosinformaticos.com",
                "correo_interno": "admin@negociosinformaticos.com",
                "cod_estable": "0001",
                "cod_punto_venta": "PV-001"
            }
        }
    }


class EmisorCreate(EmisorBase):
    """Schema para crear la configuración del emisor (hereda obligatoriedad y ejemplo)"""
    pass


class EmisorUpdate(EmisorBase):
    """
    Schema para actualización. 
    Al ser todos obligatorios, esto actúa como un reemplazo completo (PUT) 
    para garantizar que no queden campos vacíos.
    """
    pass


class EmisorResponse(BaseModel):
    """
    Schema de respuesta que refleja EXACTAMENTE la estructura plana de la base de datos.
    Esto evita errores de validación al serializar el modelo SQLAlchemy.
    """
    id: int
    nit: str
    nrc: str
    nombre: str
    nombre_comercial: str
    cod_actividad: str
    desc_actividad: str
    
    # Dirección (plana, igual que en la BD)
    cod_departamento: str
    desc_departamento: str
    cod_municipio: str
    desc_municipio: str
    cod_distrito: str
    desc_distrito: str
    dirr_complemento: str  # Mantenemos el nombre exacto de la columna de la BD
    
    telefono: str
    correo: EmailStr
    correo_interno: EmailStr
    cod_estable: str
    cod_punto_venta: str
    
    activo: bool
    created_at: datetime          # ✅ Pydantic serializará esto automáticamente a string ISO
    updated_at: Optional[datetime] = None # ✅ Permite None si aún no se ha actualizado

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "nit": "0614-120589-101-1",
                "nrc": "123456",
                "nombre": "Negocios Informáticos S.A. de C.V.",
                "nombre_comercial": "FactuSV",
                "cod_actividad": "620100",
                "desc_actividad": "Programación informática",
                "cod_departamento": "11",
                "desc_departamento": "San Salvador",
                "cod_municipio": "1101",
                "desc_municipio": "San Salvador",
                "cod_distrito": "110101",
                "desc_distrito": "San Salvador",
                "dirr_complemento": "Col. Escalón, Calle El Progreso #456",
                "telefono": "2222-3333",
                "correo": "facturacion@negociosinformaticos.com",
                "correo_interno": "admin@negociosinformaticos.com",
                "cod_estable": "0001",
                "cod_punto_venta": "PV-001",
                "activo": True,
                "created_at": "2026-07-22T10:00:00Z",
                "updated_at": "2026-07-22T10:00:00Z"
            }
        }
    }