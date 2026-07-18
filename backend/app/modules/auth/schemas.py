#C:\Users\PC\Desktop\Factu\backend\app\modules\auth\schemas.py
#Este archivo es el guardian de datos de la api, ya que define los esquemas de entrada y 
# salida para las rutas de autenticación.

#importa las erramientas de Pydantic, que es la libreria que usa FastApi para validar datos.
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


# ===========================================================
# SCHEMAS DE ENTRADA (REQUEST)
# ===========================================================
#Este request verifica que el email sea un correo válido y que la contraseña tenga al menos 8 
# caracteres, y es utilizado en la ruta de inicio de sesión.
class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="Correo electrónico del usuario")
    password: str = Field(..., min_length=8, description="Contraseña del usuario")
    #Esta es solo para la documentacion de la API Swagger, no tiene efecto en la validación de datos.
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


#Solo valida el email, y es utilizado en la ruta de recuperación de contraseña.
class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(..., description="Correo electrónico para recuperación")
    #Esta es solo para la documentacion de la API Swagger, no tiene efecto en la validación de datos.
    class Config:
        json_schema_extra = {
            "example": {
                "email": "usuario@ejemplo.com"
            }
        }


# ===========================================================
# SCHEMAS DE SALIDA (RESPONSE)
# ===========================================================

#La funcion debuelve un mensaje de éxito, el token de acceso y el tipo de token,
# y es utilizado en la ruta de inicio de sesión.
class LoginResponse(BaseModel):
    message: str
    access_token: str
    token_type: str
    #Esta es solo para la documentacion de la API Swagger, no tiene efecto en la validación de datos.
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Inicio de sesión exitoso",
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }

#Es un mensaje de éxito, y es utilizado en la ruta de recuperación de contraseña y cierre de sesión.
class MessageResponse(BaseModel):
    message: str
    #Esta es solo para la documentacion de la API Swagger, no tiene efecto en la validación de datos.
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Operación realizada exitosamente"
            }
        }

#Es igual que LoginResponse, pero solo devuelve el token de acceso y el tipo de token.
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    #Esta es solo para la documentacion de la API Swagger, no tiene efecto en la validación de datos.
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }