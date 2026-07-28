# app/modules/usuarios/models.py
"""
Módulo consolidado de modelos de usuarios.
Contiene: Usuario, Rol, Departamento, Sesion
"""


# Prueba de colaboración - Luis - 07/07/
# Prueba de Git - Luis - 07/07/2026

# app/modules/usuarios/models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Text, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# ===========================================================
# ENUMS
# ===========================================================
class EstadoUsuario(enum.Enum):
    ACTIVO = "ACTIVO"
    INACTIVO = "INACTIVO"
    BLOQUEADO = "BLOQUEADO"
    PENDIENTE = "PENDIENTE"

class TipoRol(enum.Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    GERENTE = "GERENTE"
    SUPERVISOR = "SUPERVISOR"
    VENDEDOR = "VENDEDOR"
    CONTADOR = "CONTADOR"
    USUARIO = "USUARIO"

class EstadoSesion(enum.Enum):
    ACTIVA = "ACTIVA"
    CERRADA = "CERRADA"
    EXPIRADA = "EXPIRADA"

# ===========================================================
# MODELOS
# ===========================================================

class Departamento(Base):
    __tablename__ = "departamentos"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False, unique=True, index=True)
    descripcion = Column(Text, nullable=True)
    activo = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    usuarios = relationship("Usuario", back_populates="departamento")

# ✅ ACTUALIZADO: Se agrega la relación con permisos
class Rol(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(50), nullable=False, unique=True, index=True)
    descripcion = Column(Text, nullable=True)
    tipo = Column(Enum(TipoRol), nullable=False, index=True)
    activo = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    usuarios = relationship("Usuario", back_populates="rol")
    # Relación M:N con Permisos a través de la tabla intermedia
    permisos = relationship("Permiso", secondary="rol_permisos", back_populates="roles")

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False, index=True)
    email = Column(String(150), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    telefono = Column(String(20), nullable=True)
    estado = Column(Enum(EstadoUsuario, name="estadousuario", create_constraint=True, values_callable=lambda x: [e.value for e in x]), default=EstadoUsuario.ACTIVO, nullable=False, index=True)
    departamento_id = Column(Integer, ForeignKey("departamentos.id"), nullable=True, index=True)
    rol_id = Column(Integer, ForeignKey("roles.id"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, server_default=func.now(), server_onupdate=func.now(), nullable=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    
    departamento = relationship("Departamento", back_populates="usuarios")
    rol = relationship("Rol", back_populates="usuarios")
    sesiones = relationship("Sesion", back_populates="usuario", cascade="all, delete-orphan")
    
    def puede_acceder(self) -> bool:
        return self.estado == EstadoUsuario.ACTIVO

class Sesion(Base):
    __tablename__ = "sesiones"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    token = Column(String(500), nullable=False, unique=True, index=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    estado = Column(Enum(EstadoSesion), default=EstadoSesion.ACTIVA, nullable=False, index=True)
    activo = Column(Boolean, default=True, index=True)
    login_at = Column(DateTime(timezone=True), server_default=func.now())
    logout_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    usuario = relationship("Usuario", back_populates="sesiones")

# ✅ NUEVO: Modelo de Permisos Asertivos
class Permiso(Base):
    """Modelo para permisos específicos del sistema (ej: 'bodega:crear')"""
    __tablename__ = "permisos"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo = Column(String(50), nullable=False, unique=True, index=True) # ej: "bodega:crear"
    nombre = Column(String(100), nullable=False) # ej: "Crear Bodega"
    descripcion = Column(Text, nullable=True)
    modulo = Column(String(50), nullable=False, index=True) # ej: "bodega", "usuarios"
    activo = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relación M:N con Roles
    roles = relationship("Rol", secondary="rol_permisos", back_populates="permisos")

# ✅ NUEVO: Tabla Intermedia para la relación Muchos a Muchos (M:N)
class RolPermiso(Base):
    """Tabla intermedia que asigna permisos a roles"""
    __tablename__ = "rol_permisos"
    
    rol_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    permiso_id = Column(Integer, ForeignKey("permisos.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())