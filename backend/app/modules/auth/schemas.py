#C:\Users\PC\Desktop\Factu\backend\app\modules\auth\schemas.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


# ===========================================================
# SCHEMAS DE ENTRADA (REQUEST)
# ===========================================================

class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="Correo electrónico del usuario")
    password: str = Field(..., min_length=8, description="Contraseña del usuario")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "usuario@ejemplo.com",
                "password": "mi_password_seguro"
            }
        }


class RegisterRequest(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100, description="Nombre completo del usuario")
    email: EmailStr = Field(..., description="Correo electrónico del usuario")
    password: str = Field(..., min_length=8, description="Contraseña del usuario")
    telefono: Optional[str] = Field(None, max_length=20, description="Número de teléfono")
    departamento_id: Optional[int] = Field(None, description="ID del departamento del usuario")
    rol_id: Optional[int] = Field(None, description="ID del rol del usuario")

    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "Juan Pérez",
                "email": "juan@ejemplo.com",
                "password": "mi_password_seguro",
                "telefono": "+504 9999-9999",
                "departamento_id": 1,
                "rol_id": 1
            }
        }


class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(..., description="Correo electrónico para recuperación")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "usuario@ejemplo.com"
            }
        }


# ===========================================================
# SCHEMAS DE SALIDA (RESPONSE)
# ===========================================================

class LoginResponse(BaseModel):
    message: str
    access_token: str
    token_type: str

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Inicio de sesión exitoso",
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


class RegisterResponse(BaseModel):
    message: str
    user_id: int

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Usuario registrado exitosamente",
                "user_id": 1
            }
        }


class MessageResponse(BaseModel):
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Operación realizada exitosamente"
            }
        }


class TokenResponse(BaseModel):
    access_token: str
    token_type: str

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }