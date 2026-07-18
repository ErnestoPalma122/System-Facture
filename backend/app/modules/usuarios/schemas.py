#C:\Users\PC\Desktop\Factu\backend\app\modules\usuarios\schemas.py
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum

#Define los valores permitidos a nivel de API, para segurse que se conviertan en JSON y no envien valores inventados.
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

#Contiene los campos que se comparten al crear y leer.
class DepartamentoBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    descripcion: Optional[str] = None

#Herreda de DepartamentoBase, para crear un departamento.
class DepartamentoCreate(DepartamentoBase):
    pass

class DepartamentoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    descripcion: Optional[str] = None
    activo: Optional[bool] = None  # ← Departamento SÍ tiene activo

#Herreda de DepartamentoBase, para actualizar un departamento.
class DepartamentoResponse(DepartamentoBase):
    id: int
    activo: bool  # ← Departamento SÍ tiene activo
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ===========================================================
# ROL
# ===========================================================

#Contiene los campos que se comparten al crear y leer.
class RolBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=50)
    descripcion: Optional[str] = None
    tipo: TipoRolEnum

#Herreda de RolBase, para crear un rol.
class RolCreate(RolBase):
    pass

#Herreda de RolBase, para actualizar un rol.
class RolUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=50)
    descripcion: Optional[str] = None
    tipo: Optional[TipoRolEnum] = None
    activo: Optional[bool] = None  # ← Rol SÍ tiene activo

#Herreda de RolBase, para leer un rol.
class RolResponse(RolBase):
    id: int
    activo: bool  # ← Rol SÍ tiene activo
    created_at: datetime

    #Esta funcion convierte el enum a mayusculas para coicida con los valores definidos en
    #la base de datos y evitar errores de validacion.
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

#contiene los campos base para un usuario, que se comparten al crear y leer, actualizar, etc.
class UsuarioBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    telefono: Optional[str] = Field(None, max_length=20)
#Herreda de UsuarioBase, para crear un usuario.
class UsuarioCreate(UsuarioBase):
    password: str = Field(..., min_length=8)
    departamento_id: Optional[int] = None
    rol_id: Optional[int] = None
#Esdta clase actualizar un usuario.
class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    telefono: Optional[str] = Field(None, max_length=20)
    departamento_id: Optional[int] = None
    rol_id: Optional[int] = None
#hereda de UsuarioBase, para leer un usuario.
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
    #convierte enum a mayusculas para que coincida con los valores definidos en la base de datos y evitar errores de validacion.
    @field_validator('estado', mode='before')
    @classmethod
    def convert_estado_to_upper(cls, v):
        if isinstance(v, Enum):
            return v.value.upper()
        if isinstance(v, str):
            return v.upper()
        return v
    
    model_config = ConfigDict(from_attributes=True)
#Lee en listado de usuarios, con total y lista de usuarios en respuesta.
class UsuarioListResponse(BaseModel):
    total: int
    #llama a la clase UsuarioResponse para definir el tipo de cada usuario en la lista.
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

#Expone datos para uditoria y control de sesiones.
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
#valida que la contraseña cumpla con los requisitos de seguridad, como longitud mínima y complejidad.
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