# app/modules/usuarios/models.py
"""
Módulo consolidado de modelos de usuarios.
Contiene: Usuario, Rol, Departamento, Sesion
"""


# Prueba de colaboración - Luis - 07/07/
# Prueba de Git - Luis - 07/07/2026

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
# Permite usar funciones nativas de la base de datos (como NOW()) en lugar de depender solo de la hora de Python.
from sqlalchemy.sql import func
#Es la base declarativa que representa una tabla de la base de datos.
from app.core.database import Base
import enum
import logging
from datetime import datetime

#quien se encarga de imprimir en la consola.
logger = logging.getLogger(__name__)


# ===========================================================
# ENUMS
# ===========================================================

#Este enum representa los posibles estados de un usuario en el sistema permitiendo solo lo definido.
class EstadoUsuario(enum.Enum):
    """Estados posibles de un usuario"""
    ACTIVO = "ACTIVO"
    INACTIVO = "INACTIVO"
    BLOQUEADO = "BLOQUEADO"
    PENDIENTE = "PENDIENTE"

#
class TipoRol(enum.Enum):
    """Tipos de roles en el sistema"""
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    GERENTE = "GERENTE"
    SUPERVISOR = "SUPERVISOR"
    VENDEDOR = "VENDEDOR"
    CONTADOR = "CONTADOR"
    USUARIO = "USUARIO"


class EstadoSesion(enum.Enum):
    """Estados de una sesión (ciclo de vida)"""
    ACTIVA = "ACTIVA"
    CERRADA = "CERRADA"
    EXPIRADA = "EXPIRADA"


# ===========================================================
# MODELOS
# ===========================================================

#SON MODELOS O TABLAS DE REFERENCIA QUE REPRESENTAN ENTIDADES DEN LA BASE DE DATOS.

#En este caso departamentos en un a empresa.
class Departamento(Base):
    """Modelo para departamentos/áreas de la empresa"""
    __tablename__ = "departamentos"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False, unique=True, index=True)
    descripcion = Column(Text, nullable=True)
    activo = Column(Boolean, default=True, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    usuarios = relationship("Usuario", back_populates="departamento")
    
    def __repr__(self):
        return f"<Departamento(id={self.id}, nombre={self.nombre}, activo={self.activo})>"

#El rol que tiene un usuario, que define sus permisos y nivel de acceso al sistema.
class Rol(Base):
    """Modelo para roles de usuario"""
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(50), nullable=False, unique=True, index=True)
    descripcion = Column(Text, nullable=True)
    tipo = Column(Enum(TipoRol), nullable=False, index=True)
    activo = Column(Boolean, default=True, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    usuarios = relationship("Usuario", back_populates="rol")
    
    def __repr__(self):
        return f"<Rol(id={self.id}, nombre={self.nombre}, tipo={self.tipo}, activo={self.activo})>"

#Los usuarios que pueden acceder al sistema, con sus credenciales y estado.
class Usuario(Base):
    """Modelo principal de usuarios del sistema"""
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False, index=True)
    email = Column(String(150), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    telefono = Column(String(20), nullable=True)
    
    estado = Column(
        Enum(
            EstadoUsuario,
            name="estadousuario",
            create_constraint=True,
            values_callable=lambda x: [e.value for e in x]
        ),
        default=EstadoUsuario.ACTIVO,
        nullable=False,
        index=True
    )
    
    departamento_id = Column(Integer, ForeignKey("departamentos.id"), nullable=True, index=True)
    rol_id = Column(Integer, ForeignKey("roles.id"), nullable=True, index=True)
    
    created_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=True
    )
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    created_by = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    
    departamento = relationship("Departamento", back_populates="usuarios")
    rol = relationship("Rol", back_populates="usuarios")
    sesiones = relationship("Sesion", back_populates="usuario", cascade="all, delete-orphan")
    
    def puede_acceder(self) -> bool:
        """Verifica si el usuario puede acceder al sistema"""
        return self.estado == EstadoUsuario.ACTIVO
    
    def __repr__(self):
        return f"<Usuario(id={self.id}, email={self.email}, nombre={self.nombre}, estado={self.estado})>"


#Este modelo registra las sesiones de casa usuario cada vez que inicia sesión en el sistema, permitiendo controlar su estado y duración.
class Sesion(Base):
    """Modelo para registrar sesiones de usuarios"""
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
    
    def __repr__(self):
        return f"<Sesion(id={self.id}, usuario_id={self.usuario_id}, estado={self.estado}, activo={self.activo})>"