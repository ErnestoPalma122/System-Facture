#C:\Users\PC\Desktop\Factu\backend\app\modules\usuarios\schemas.py
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum


class EstadoUsuarioEnum(str, Enum):
    ACTIVO = "ACTIVO"
    INACTIVO = "INACTIVO"
    BLOQUEADO = "BLOQUEADO"
    PENDIENTE = "PENDIENTE"


class TipoRolEnum(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    GERENTE = "GERENTE"
    SUPERVISOR = "SUPERVISOR"
    VENDEDOR = "VENDEDOR"
    CONTADOR = "CONTADOR"
    USUARIO = "USUARIO"


# ===========================================================
# DEPARTAMENTO
# ===========================================================

class DepartamentoBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    descripcion: Optional[str] = None

class DepartamentoCreate(DepartamentoBase):
    pass

class DepartamentoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    descripcion: Optional[str] = None
    activo: Optional[bool] = None  # ← Departamento SÍ tiene activo

class DepartamentoResponse(DepartamentoBase):
    id: int
    activo: bool  # ← Departamento SÍ tiene activo
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ===========================================================
# ROL
# ===========================================================

class RolBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=50)
    descripcion: Optional[str] = None
    tipo: TipoRolEnum

class RolCreate(RolBase):
    pass

class RolUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=50)
    descripcion: Optional[str] = None
    tipo: Optional[TipoRolEnum] = None
    activo: Optional[bool] = None  # ← Rol SÍ tiene activo

class RolResponse(RolBase):
    id: int
    activo: bool  # ← Rol SÍ tiene activo
    created_at: datetime
    
    @field_validator('tipo', mode='before')
    @classmethod
    def convert_tipo_to_upper(cls, v):
        if isinstance(v, Enum):
            return v.value.upper()
        if isinstance(v, str):
            return v.upper()
        return v
    
    model_config = ConfigDict(from_attributes=True)


# ===========================================================
# USUARIO
# ===========================================================

class UsuarioBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    telefono: Optional[str] = Field(None, max_length=20)

class UsuarioCreate(UsuarioBase):
    password: str = Field(..., min_length=8)
    departamento_id: Optional[int] = None
    rol_id: Optional[int] = None

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    telefono: Optional[str] = Field(None, max_length=20)
    departamento_id: Optional[int] = None
    rol_id: Optional[int] = None

class UsuarioResponse(UsuarioBase):
    id: int
    estado: EstadoUsuarioEnum  # ← Usuario SOLO tiene estado, NO activo
    departamento_id: Optional[int] = None
    rol_id: Optional[int] = None
    departamento: Optional[DepartamentoResponse] = None
    rol: Optional[RolResponse] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    @field_validator('estado', mode='before')
    @classmethod
    def convert_estado_to_upper(cls, v):
        if isinstance(v, Enum):
            return v.value.upper()
        if isinstance(v, str):
            return v.upper()
        return v
    
    model_config = ConfigDict(from_attributes=True)

class UsuarioListResponse(BaseModel):
    total: int
    usuarios: List[UsuarioResponse]

class UsuarioCreateResponse(BaseModel):
    message: str
    id: int
    nombre: str
    email: EmailStr

class UsuarioUpdateResponse(BaseModel):
    message: str
    id: int


# ===========================================================
# SESION
# ===========================================================

class SesionResponse(BaseModel):
    id: int
    usuario_id: int
    token: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    estado: str  # ← Sesion tiene estado
    activo: bool  # ← Sesion tiene activo
    login_at: datetime
    logout_at: Optional[datetime] = None
    expires_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ===========================================================
# CONTRASEÑA
# ===========================================================

class CambiarContrasenaRequest(BaseModel):
    contrasena_actual: str
    contrasena_nueva: str = Field(..., min_length=8)

class MessageResponse(BaseModel):
    message: str


# ===========================================================
# DEPARTAMENTO - SCHEMAS COMPLETOS
# ===========================================================

class DepartamentoListResponse(BaseModel):
    """Respuesta para listar departamentos"""
    total: int
    departamentos: List["DepartamentoResponse"]


# ===========================================================
# ROL - SCHEMAS COMPLETOS
# ===========================================================

class RolListResponse(BaseModel):
    """Respuesta para listar roles"""
    total: int
    roles: List[RolResponse]