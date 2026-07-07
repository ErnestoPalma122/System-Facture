#C:\Users\PC\Desktop\Factu\backend\app\modules\usuarios\services.py
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.modules.usuarios.models import Usuario, EstadoUsuario
from app.modules.usuarios.schemas import UsuarioCreate, UsuarioUpdate
from passlib.context import CryptContext
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

##################################### LOGICA USUARIOS ############################################################


# Funcion para obtener usuario por id OBTENER USUARIO POR ID
def get_usuario_by_id(db: Session, usuario_id: int):
    """Obtener usuario por ID con logging"""
    logger.info(f"🔍 Buscando usuario con ID: {usuario_id}")
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    
    if usuario:
        logger.info(f"✅ Usuario encontrado: ID={usuario.id}, Nombre={usuario.nombre}, Email={usuario.email}, Estado={usuario.estado}")
    else:
        logger.warning(f"❌ Usuario con ID {usuario_id} NO encontrado")
    
    return usuario


# Funcion para obtener usuario por correo OBTENER USUARIO POR CORREO
def get_usuario_by_email(db: Session, email: str):
    """Obtener usuario por email con logging"""
    logger.info(f"🔍 Buscando usuario con email: {email}")
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    
    if usuario:
        logger.info(f"✅ Usuario encontrado: ID={usuario.id}, Email={usuario.email}")
    else:
        logger.info(f"ℹ️ No se encontró usuario con email: {email}")
    
    return usuario


# Funcion para traer todos los usuarios OBTENER TODOS LOS USUARIOS
def get_usuarios(db: Session, skip: int = 0, limit: int = 100, estado: str = None):
    """Obtener lista de usuarios con filtros y logging"""
    logger.info(f"🔍 Obteniendo usuarios (skip={skip}, limit={limit}, estado={estado})")
    
    query = db.query(Usuario)
    
    if estado is not None:
        query = query.filter(Usuario.estado == estado)
        logger.info(f"🔎 Aplicando filtro: estado={estado}")
    
    usuarios = query.offset(skip).limit(limit).all()
    logger.info(f"✅ Se encontraron {len(usuarios)} usuarios")
    
    return usuarios


# Funcion para crear usuarios CREAR USUARIOS
def crear_usuario(db: Session, usuario: UsuarioCreate):
    """Crear nuevo usuario con logging detallado"""
    logger.info("=" * 60)
    logger.info("🆕 INICIANDO CREACIÓN DE USUARIO")
    logger.info(f"📧 Email: {usuario.email}")
    logger.info(f"👤 Nombre: {usuario.nombre}")
    logger.info("=" * 60)
    
    db_usuario = get_usuario_by_email(db, usuario.email)
    if db_usuario:
        logger.error(f"❌ ERROR: El email {usuario.email} ya está registrado")
        raise ValueError(f"El email {usuario.email} ya está registrado")
    
    logger.info("🔐 Hasheando contraseña...")
    hashed_password = pwd_context.hash(usuario.password)
    logger.info(f"✅ Contraseña hasheada: {hashed_password[:20]}...")
    
    logger.info("📝 Creando objeto Usuario...")
    db_usuario = Usuario(
        nombre=usuario.nombre,
        email=usuario.email,
        password_hash=hashed_password,
        telefono=usuario.telefono,
        departamento_id=usuario.departamento_id,
        rol_id=usuario.rol_id,
        estado=EstadoUsuario.ACTIVO  # ← SOLO estado
    )
    
    logger.info(f"📦 Objeto creado: {db_usuario}")
    
    try:
        logger.info("💾 Guardando en base de datos...")
        db.add(db_usuario)
        db.commit()
        db.refresh(db_usuario)
        logger.info(f"✅ USUARIO CREADO EXITOSAMENTE: ID={db_usuario.id}, Estado={db_usuario.estado}")
        return db_usuario
    except IntegrityError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE INTEGRIDAD: {str(e)}")
        raise ValueError(f"Error de integridad: {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE BASE DE DATOS: {str(e)}")
        raise ValueError(f"Error de base de datos: {str(e)}")



# Funcion para actualizar usuarios ACTUALIZAR USUARIOS
def actualizar_usuario(db: Session, usuario_id: int, usuario: UsuarioUpdate):
    """Actualizar usuario existente con logging DETALLADO"""
    logger.info("=" * 60)
    logger.info(f"🔄 INICIANDO ACTUALIZACIÓN DE USUARIO ID: {usuario_id}")
    logger.info("=" * 60)
    
    db_usuario = get_usuario_by_id(db, usuario_id)
    if not db_usuario:
        logger.error(f"❌ ERROR: Usuario con ID {usuario_id} NO encontrado")
        return None
    
    logger.info(f"📊 Datos ANTES de actualizar:")
    logger.info(f"   - Nombre: {db_usuario.nombre}")
    logger.info(f"   - Email: {db_usuario.email}")
    logger.info(f"   - Teléfono: {db_usuario.telefono}")
    logger.info(f"   - Estado: {db_usuario.estado}")
    logger.info(f"   - Departamento ID: {db_usuario.departamento_id}")
    logger.info(f"   - Rol ID: {db_usuario.rol_id}")
    
    update_data = usuario.dict(exclude_unset=True)
    logger.info(f"📝 Datos RECIBIDOS para actualizar: {update_data}")
    
    # Campos que NO se pueden actualizar desde este endpoint
    campos_protegidos = ['estado', 'password_hash', 'created_at', 'created_by']
    
    for campo in campos_protegidos:
        if campo in update_data:
            logger.error(f"❌ ERROR: Intento de actualizar campo protegido: {campo}")
            raise ValueError(f"No se puede actualizar el campo '{campo}' desde este endpoint.")
    
    campos_actualizados = []
    for field, value in update_data.items():
        valor_anterior = getattr(db_usuario, field)
        setattr(db_usuario, field, value)
        campos_actualizados.append(f"{field}: {valor_anterior} → {value}")
        logger.info(f"   ✅ {field}: {valor_anterior} → {value}")
    
    if not campos_actualizados:
        logger.warning("⚠️ No se proporcionaron campos para actualizar")
        return db_usuario
    
    logger.info(f"📊 Campos actualizados: {', '.join(campos_actualizados)}")
    
    try:
        logger.info("💾 Guardando cambios en base de datos...")
        db.commit()
        db.refresh(db_usuario)
        
        logger.info(f"📊 Datos DESPUÉS de actualizar:")
        logger.info(f"   - Nombre: {db_usuario.nombre}")
        logger.info(f"   - Email: {db_usuario.email}")
        logger.info(f"   - Estado: {db_usuario.estado}")
        logger.info(f"   - Updated At: {db_usuario.updated_at}")
        
        logger.info(f"✅ USUARIO ACTUALIZADO EXITOSAMENTE: ID={db_usuario.id}")
        return db_usuario
    except IntegrityError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE INTEGRIDAD al actualizar: {str(e)}")
        raise ValueError(f"Error de integridad: {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE BASE DE DATOS al actualizar: {str(e)}")
        raise ValueError(f"Error de base de datos: {str(e)}")



# Funcion para activar usuarios ACTIVAR USUARIOS
def activar_usuario(db: Session, usuario_id: int):
    """Activar usuario con verificación completa"""
    logger.info("=" * 60)
    logger.info(f"🟢 INICIANDO ACTIVACIÓN de usuario ID: {usuario_id}")
    logger.info("=" * 60)
    
    logger.info("🔍 PASO 1: Consultando estado actual del usuario...")
    usuario_antes = get_usuario_by_id(db, usuario_id)
    
    if not usuario_antes:
        logger.error(f"❌ ERROR: Usuario ID={usuario_id} NO encontrado")
        raise ValueError(f"Usuario con ID {usuario_id} no encontrado")
    
    logger.info(f"📊 Estado ANTES del cambio:")
    logger.info(f"   - ID: {usuario_antes.id}")
    logger.info(f"   - Nombre: {usuario_antes.nombre}")
    logger.info(f"   - Estado: {usuario_antes.estado}")
    
    if usuario_antes.estado == EstadoUsuario.ACTIVO:
        logger.warning(f"⚠️ Usuario ID={usuario_id} YA está ACTIVO")
        return {
            "usuario": usuario_antes,
            "cambio_realizado": False,
            "mensaje": "El usuario ya está activo"
        }
    
    logger.info("🔄 PASO 3: Realizando cambio de estado...")
    logger.info(f"   - Cambiando estado: {usuario_antes.estado} → ACTIVO")
    
    try:
        usuario_antes.estado = EstadoUsuario.ACTIVO
        db.commit()
        logger.info("✅ Cambio guardado en base de datos")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"❌ ERROR al guardar cambio: {str(e)}")
        raise ValueError(f"Error al activar usuario: {str(e)}")
    
    logger.info("🔍 PASO 4: Verificando que el cambio se realizó correctamente...")
    usuario_despues = get_usuario_by_id(db, usuario_id)
    
    logger.info(f"📊 Estado DESPUÉS del cambio:")
    logger.info(f"   - ID: {usuario_despues.id}")
    logger.info(f"   - Estado: {usuario_despues.estado}")
    
    if usuario_despues.estado == EstadoUsuario.ACTIVO:
        logger.info("=" * 60)
        logger.info(f"✅ USUARIO ACTIVADO EXITOSAMENTE")
        logger.info(f"   - Verificación: estado=ACTIVO confirmado en BD")
        logger.info("=" * 60)
        
        return {
            "usuario": usuario_despues,
            "cambio_realizado": True,
            "mensaje": "Usuario activado exitosamente"
        }
    else:
        logger.error("=" * 60)
        logger.error(f"❌ ERROR: El cambio NO se realizó correctamente")
        logger.error("=" * 60)
        raise ValueError("No se pudo activar el usuario.")



## Funcion para desactivar usuarios DESACTIVAR USUARIO
def desactivar_usuario(db: Session, usuario_id: int):
    """Desactivar usuario con verificación completa"""
    logger.info("=" * 60)
    logger.info(f"🔴 INICIANDO DESACTIVACIÓN de usuario ID: {usuario_id}")
    logger.info("=" * 60)
    
    logger.info("🔍 PASO 1: Consultando estado actual del usuario...")
    usuario_antes = get_usuario_by_id(db, usuario_id)
    
    if not usuario_antes:
        logger.error(f"❌ ERROR: Usuario ID={usuario_id} NO encontrado")
        raise ValueError(f"Usuario con ID {usuario_id} no encontrado")
    
    logger.info(f"📊 Estado ANTES del cambio:")
    logger.info(f"   - ID: {usuario_antes.id}")
    logger.info(f"   - Nombre: {usuario_antes.nombre}")
    logger.info(f"   - Estado: {usuario_antes.estado}")
    
    if usuario_antes.estado == EstadoUsuario.INACTIVO:
        logger.warning(f"⚠️ Usuario ID={usuario_id} YA está INACTIVO")
        return {
            "usuario": usuario_antes,
            "cambio_realizado": False,
            "mensaje": "El usuario ya está desactivado"
        }
    
    logger.info("🔄 PASO 3: Realizando cambio de estado...")
    logger.info(f"   - Cambiando estado: {usuario_antes.estado} → INACTIVO")
    
    try:
        usuario_antes.estado = EstadoUsuario.INACTIVO
        db.commit()
        logger.info("✅ Cambio guardado en base de datos")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"❌ ERROR al guardar cambio: {str(e)}")
        raise ValueError(f"Error al desactivar usuario: {str(e)}")
    
    logger.info("🔍 PASO 4: Verificando que el cambio se realizó correctamente...")
    usuario_despues = get_usuario_by_id(db, usuario_id)
    
    logger.info(f"📊 Estado DESPUÉS del cambio:")
    logger.info(f"   - ID: {usuario_despues.id}")
    logger.info(f"   - Estado: {usuario_despues.estado}")
    
    if usuario_despues.estado == EstadoUsuario.INACTIVO:
        logger.info("=" * 60)
        logger.info(f"✅ USUARIO DESACTIVADO EXITOSAMENTE")
        logger.info(f"   - Verificación: estado=INACTIVO confirmado en BD")
        logger.info("=" * 60)
        
        return {
            "usuario": usuario_despues,
            "cambio_realizado": True,
            "mensaje": "Usuario desactivado exitosamente"
        }
    else:
        logger.error("=" * 60)
        logger.error(f"❌ ERROR: El cambio NO se realizó correctamente")
        logger.error("=" * 60)
        raise ValueError("No se pudo desactivar el usuario.")



# Funcion para cambio de contraseña CAMBIAR CONTRASEÑA
def cambiar_contrasena(db: Session, usuario_id: int, contrasena_actual: str, contrasena_nueva: str):
    """Cambiar contraseña de usuario con logging DETALLADO"""
    logger.info("=" * 60)
    logger.info(f"🔐 INICIANDO CAMBIO DE CONTRASEÑA para usuario ID: {usuario_id}")
    logger.info("=" * 60)
    
    db_usuario = get_usuario_by_id(db, usuario_id)
    if not db_usuario:
        logger.error(f"❌ ERROR: Usuario con ID {usuario_id} NO encontrado")
        raise ValueError(f"Usuario con ID {usuario_id} no encontrado")
    
    # Verificar si puede acceder (estado ACTIVO)
    if not db_usuario.puede_acceder():
        logger.error(f"❌ ERROR: Usuario ID={usuario_id} tiene estado {db_usuario.estado}")
        raise ValueError("El usuario no puede cambiar su contraseña porque no está activo")
    
    logger.info(f"📊 Usuario encontrado:")
    logger.info(f"   - ID: {db_usuario.id}")
    logger.info(f"   - Nombre: {db_usuario.nombre}")
    logger.info(f"   - Estado: {db_usuario.estado}")
    
    logger.info("🔍 Verificando contraseña actual...")
    if not pwd_context.verify(contrasena_actual, db_usuario.password_hash):
        logger.error("❌ ERROR: La contraseña actual es INCORRECTA")
        raise ValueError("La contraseña actual es incorrecta")
    
    logger.info("✅ Contraseña actual verificada correctamente")
    
    if contrasena_actual == contrasena_nueva:
        logger.warning("⚠️ La nueva contraseña es igual a la actual")
        raise ValueError("La nueva contraseña debe ser diferente a la actual")
    
    logger.info("🔐 Hasheando nueva contraseña...")
    hashed_nueva = pwd_context.hash(contrasena_nueva)
    logger.info(f"✅ Nueva contraseña hasheada: {hashed_nueva[:20]}...")
    
    logger.info("💾 Actualizando contraseña en base de datos...")
    db_usuario.password_hash = hashed_nueva
    
    try:
        db.commit()
        db.refresh(db_usuario)
        
        logger.info("=" * 60)
        logger.info(f"✅ CONTRASEÑA CAMBIADA EXITOSAMENTE")
        logger.info(f"   - Usuario ID: {db_usuario.id}")
        logger.info(f"   - Timestamp: {datetime.utcnow()}")
        logger.info("=" * 60)
        
        return db_usuario
    
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE BASE DE DATOS al cambiar contraseña: {str(e)}")
        raise ValueError(f"Error al cambiar contraseña: {str(e)}")


# Funcion para eliminar usuatrios ELIMINAR USAURIOS
def eliminar_usuario(db: Session, usuario_id: int, super_admin_id: int):
    """
    Eliminar usuario PERMANENTEMENTE de la base de datos (HARD DELETE).
    
    SEGURIDAD:
    - Solo SUPER_ADMIN puede ejecutar esta acción
    - No puede eliminarse a sí mismo
    - No puede eliminar al último SUPER_ADMIN del sistema
    - Elimina también todas las sesiones asociadas (cascade)
    """
    logger.info("=" * 60)
    logger.info(f"💀 INICIANDO ELIMINACIÓN PERMANENTE de usuario ID: {usuario_id}")
    logger.info(f"👤 Ejecutado por SUPER_ADMIN ID: {super_admin_id}")
    logger.info("=" * 60)
    
    # VALIDACIÓN 1: No puede eliminarse a sí mismo
    if usuario_id == super_admin_id:
        logger.error(f"❌ ERROR: SUPER_ADMIN ID={super_admin_id} intentó eliminarse a sí mismo")
        raise ValueError("No puedes eliminar tu propia cuenta. Pide a otro SUPER_ADMIN que lo haga.")
    
    # PASO 1: Consultar usuario a eliminar
    logger.info("🔍 PASO 1: Consultando usuario a eliminar...")
    usuario_a_eliminar = get_usuario_by_id(db, usuario_id)
    
    if not usuario_a_eliminar:
        logger.error(f"❌ ERROR: Usuario ID={usuario_id} NO encontrado")
        raise ValueError(f"Usuario con ID {usuario_id} no encontrado")
    
    logger.info(f"📊 Usuario a eliminar:")
    logger.info(f"   - ID: {usuario_a_eliminar.id}")
    logger.info(f"   - Nombre: {usuario_a_eliminar.nombre}")
    logger.info(f"   - Email: {usuario_a_eliminar.email}")
    logger.info(f"   - Estado: {usuario_a_eliminar.estado}")
    logger.info(f"   - Rol: {usuario_a_eliminar.rol.tipo.value if usuario_a_eliminar.rol else 'Sin rol'}")
    
    # VALIDACIÓN 2: Si es SUPER_ADMIN, verificar que no sea el último
    if usuario_a_eliminar.rol and usuario_a_eliminar.rol.tipo.value.upper() == "SUPER_ADMIN":
        logger.warning("⚠️ El usuario a eliminar es SUPER_ADMIN. Verificando que no sea el último...")
        
        from app.modules.usuarios.models import Rol, TipoRol
        rol_super_admin = db.query(Rol).filter(Rol.tipo == TipoRol.SUPER_ADMIN).first()
        
        if rol_super_admin:
            total_super_admins = db.query(Usuario).filter(
                Usuario.rol_id == rol_super_admin.id,
                Usuario.estado == EstadoUsuario.ACTIVO
            ).count()
            
            logger.info(f"🔢 Total de SUPER_ADMIN activos en el sistema: {total_super_admins}")
            
            if total_super_admins <= 1:
                logger.error("❌ ERROR: No se puede eliminar al último SUPER_ADMIN del sistema")
                raise ValueError(
                    "No se puede eliminar al último SUPER_ADMIN del sistema. "
                    "Debe existir al menos un SUPER_ADMIN activo para administrar el sistema."
                )
    
    # PASO 2: Contar sesiones asociadas
    logger.info("🔍 PASO 2: Verificando sesiones asociadas...")
    from app.modules.usuarios.models import Sesion
    sesiones_asociadas = db.query(Sesion).filter(Sesion.usuario_id == usuario_id).count()
    logger.info(f"📊 Sesiones asociadas que serán eliminadas: {sesiones_asociadas}")
    
    # PASO 3: Eliminar PERMANENTEMENTE
    logger.info("💀 PASO 3: Eliminando usuario PERMANENTEMENTE de la base de datos...")
    
    try:
        usuario_id_eliminado = usuario_a_eliminar.id
        usuario_email_eliminado = usuario_a_eliminar.email
        usuario_nombre_eliminado = usuario_a_eliminar.nombre
        
        db.delete(usuario_a_eliminar)
        db.commit()
        
        logger.info("✅ Usuario eliminado de la base de datos")
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"❌ ERROR al eliminar usuario: {str(e)}")
        raise ValueError(f"Error al eliminar usuario: {str(e)}")
    
    # PASO 4: Verificar que YA NO existe
    logger.info("🔍 PASO 4: Verificando que el usuario fue eliminado correctamente...")
    usuario_verificacion = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    
    if usuario_verificacion is None:
        logger.info("=" * 60)
        logger.info(f"💀 USUARIO ELIMINADO PERMANENTEMENTE")
        logger.info(f"   - ID eliminado: {usuario_id_eliminado}")
        logger.info(f"   - Nombre: {usuario_nombre_eliminado}")
        logger.info(f"   - Email: {usuario_email_eliminado}")
        logger.info(f"   - Sesiones eliminadas: {sesiones_asociadas}")
        logger.info(f"   - Ejecutado por: SUPER_ADMIN ID={super_admin_id}")
        logger.info(f"   - Verificación: Usuario NO existe en BD ✅")
        logger.info("=" * 60)
        
        return {
            "usuario_id": usuario_id_eliminado,
            "usuario_nombre": usuario_nombre_eliminado,
            "usuario_email": usuario_email_eliminado,
            "sesiones_eliminadas": sesiones_asociadas,
            "mensaje": f"Usuario '{usuario_nombre_eliminado}' (ID: {usuario_id_eliminado}) eliminado permanentemente"
        }
    else:
        logger.error("=" * 60)
        logger.error(f"❌ ERROR CRÍTICO: El usuario SIGUE en la base de datos después del DELETE")
        logger.error("=" * 60)
        raise ValueError("Error crítico: No se pudo eliminar el usuario de la base de datos")
    
##################################### LOGICA DEPARTAMENTOS ############################################################

from app.modules.usuarios.models import Departamento
from app.modules.usuarios.schemas import DepartamentoCreate, DepartamentoUpdate


# Funcion para obtener departamento por id OBTENER DEPARTAMENTO POR ID
def get_departamento_by_id(db: Session, departamento_id: int):
    """Obtener departamento por ID con logging"""
    logger.info(f"🔍 Buscando departamento con ID: {departamento_id}")
    departamento = db.query(Departamento).filter(Departamento.id == departamento_id).first()
    
    if departamento:
        logger.info(f"✅ Departamento encontrado: ID={departamento.id}, Nombre={departamento.nombre}")
    else:
        logger.warning(f"❌ Departamento con ID {departamento_id} NO encontrado")
    
    return departamento


# Funcion para obtener departamento por nombre OBTENER DEPARTAMENTO POR NOMBRE
def get_departamento_by_nombre(db: Session, nombre: str):
    """Obtener departamento por nombre con logging"""
    logger.info(f"🔍 Buscando departamento con nombre: {nombre}")
    departamento = db.query(Departamento).filter(Departamento.nombre == nombre).first()
    
    if departamento:
        logger.info(f"✅ Departamento encontrado: ID={departamento.id}, Nombre={departamento.nombre}")
    else:
        logger.info(f"ℹ️ No se encontró departamento con nombre: {nombre}")
    
    return departamento


# Funcion para traer todos los departamentos OBTENER TODOS LOS DEPARTAMENTOS
def get_departamentos(db: Session, skip: int = 0, limit: int = 100, activo: bool = None):
    """Obtener lista de departamentos con filtros y logging"""
    logger.info(f"🔍 Obteniendo departamentos (skip={skip}, limit={limit}, activo={activo})")
    
    query = db.query(Departamento)
    
    if activo is not None:
        query = query.filter(Departamento.activo == activo)
        logger.info(f"🔎 Aplicando filtro: activo={activo}")
    
    departamentos = query.offset(skip).limit(limit).all()
    logger.info(f"✅ Se encontraron {len(departamentos)} departamentos")
    
    return departamentos


# Funcion para crear departamentos CREAR DEPARTAMENTO
def crear_departamento(db: Session, departamento: DepartamentoCreate):
    """Crear nuevo departamento con logging detallado"""
    logger.info("=" * 60)
    logger.info("🆕 INICIANDO CREACIÓN DE DEPARTAMENTO")
    logger.info(f"🏢 Nombre: {departamento.nombre}")
    logger.info(f"📝 Descripción: {departamento.descripcion}")
    logger.info("=" * 60)
    
    # Verificar si el nombre ya existe
    db_departamento = get_departamento_by_nombre(db, departamento.nombre)
    if db_departamento:
        logger.error(f"❌ ERROR: El departamento '{departamento.nombre}' ya existe")
        raise ValueError(f"El departamento '{departamento.nombre}' ya existe")
    
    logger.info("📝 Creando objeto Departamento...")
    db_departamento = Departamento(
        nombre=departamento.nombre,
        descripcion=departamento.descripcion,
        activo=True
    )
    
    logger.info(f"📦 Objeto creado: {db_departamento}")
    
    try:
        logger.info("💾 Guardando en base de datos...")
        db.add(db_departamento)
        db.commit()
        db.refresh(db_departamento)
        logger.info(f"✅ DEPARTAMENTO CREADO EXITOSAMENTE: ID={db_departamento.id}")
        return db_departamento
    except IntegrityError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE INTEGRIDAD: {str(e)}")
        raise ValueError(f"Error de integridad: {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE BASE DE DATOS: {str(e)}")
        raise ValueError(f"Error de base de datos: {str(e)}")


# Funcion para actualizar departamentos ACTUALIZAR DEPARTAMENTO
def actualizar_departamento(db: Session, departamento_id: int, departamento: DepartamentoUpdate):
    """Actualizar departamento existente con logging DETALLADO"""
    logger.info("=" * 60)
    logger.info(f"🔄 INICIANDO ACTUALIZACIÓN DE DEPARTAMENTO ID: {departamento_id}")
    logger.info("=" * 60)
    
    db_departamento = get_departamento_by_id(db, departamento_id)
    if not db_departamento:
        logger.error(f"❌ ERROR: Departamento con ID {departamento_id} NO encontrado")
        return None
    
    logger.info(f"📊 Datos ANTES de actualizar:")
    logger.info(f"   - Nombre: {db_departamento.nombre}")
    logger.info(f"   - Descripción: {db_departamento.descripcion}")
    logger.info(f"   - Activo: {db_departamento.activo}")
    
    update_data = departamento.dict(exclude_unset=True)
    logger.info(f"📝 Datos RECIBIDOS para actualizar: {update_data}")
    
    # Si se cambia el nombre, verificar que no exista otro con ese nombre
    if 'nombre' in update_data:
        nombre_nuevo = update_data['nombre']
        departamento_existente = get_departamento_by_nombre(db, nombre_nuevo)
        if departamento_existente and departamento_existente.id != departamento_id:
            logger.error(f"❌ ERROR: Ya existe otro departamento con el nombre '{nombre_nuevo}'")
            raise ValueError(f"Ya existe otro departamento con el nombre '{nombre_nuevo}'")
    
    campos_actualizados = []
    for field, value in update_data.items():
        valor_anterior = getattr(db_departamento, field)
        setattr(db_departamento, field, value)
        campos_actualizados.append(f"{field}: {valor_anterior} → {value}")
        logger.info(f"   ✅ {field}: {valor_anterior} → {value}")
    
    if not campos_actualizados:
        logger.warning("⚠️ No se proporcionaron campos para actualizar")
        return db_departamento
    
    logger.info(f"📊 Campos actualizados: {', '.join(campos_actualizados)}")
    
    try:
        logger.info("💾 Guardando cambios en base de datos...")
        db.commit()
        db.refresh(db_departamento)
        
        logger.info(f"📊 Datos DESPUÉS de actualizar:")
        logger.info(f"   - Nombre: {db_departamento.nombre}")
        logger.info(f"   - Descripción: {db_departamento.descripcion}")
        logger.info(f"   - Activo: {db_departamento.activo}")
        logger.info(f"   - Updated At: {db_departamento.updated_at}")
        
        logger.info(f"✅ DEPARTAMENTO ACTUALIZADO EXITOSAMENTE: ID={db_departamento.id}")
        return db_departamento
    except IntegrityError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE INTEGRIDAD al actualizar: {str(e)}")
        raise ValueError(f"Error de integridad: {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE BASE DE DATOS al actualizar: {str(e)}")
        raise ValueError(f"Error de base de datos: {str(e)}")


##################################### LOGICA ROLES ############################################################

from app.modules.usuarios.models import Rol, TipoRol
from app.modules.usuarios.schemas import RolCreate, RolUpdate


# Funcion para obtener rol por id OBTENER ROL POR ID
def get_rol_by_id(db: Session, rol_id: int):
    """Obtener rol por ID con logging"""
    logger.info(f"🔍 Buscando rol con ID: {rol_id}")
    rol = db.query(Rol).filter(Rol.id == rol_id).first()
    
    if rol:
        logger.info(f"✅ Rol encontrado: ID={rol.id}, Nombre={rol.nombre}, Tipo={rol.tipo}")
    else:
        logger.warning(f"❌ Rol con ID {rol_id} NO encontrado")
    
    return rol


# Funcion para obtener rol por nombre OBTENER ROL POR NOMBRE
def get_rol_by_nombre(db: Session, nombre: str):
    """Obtener rol por nombre con logging"""
    logger.info(f"🔍 Buscando rol con nombre: {nombre}")
    rol = db.query(Rol).filter(Rol.nombre == nombre).first()
    
    if rol:
        logger.info(f"✅ Rol encontrado: ID={rol.id}, Nombre={rol.nombre}")
    else:
        logger.info(f"ℹ️ No se encontró rol con nombre: {nombre}")
    
    return rol


# Funcion para obtener rol por tipo OBTENER ROL POR TIPO
def get_rol_by_tipo(db: Session, tipo: str):
    """Obtener rol por tipo con logging"""
    logger.info(f"🔍 Buscando rol con tipo: {tipo}")
    rol = db.query(Rol).filter(Rol.tipo == tipo).first()
    
    if rol:
        logger.info(f"✅ Rol encontrado: ID={rol.id}, Tipo={rol.tipo}")
    else:
        logger.info(f"ℹ️ No se encontró rol con tipo: {tipo}")
    
    return rol


# Funcion para traer todos los roles OBTENER TODOS LOS ROLES
def get_roles(db: Session, skip: int = 0, limit: int = 100, activo: bool = None):
    """Obtener lista de roles con filtros y logging"""
    logger.info(f"🔍 Obteniendo roles (skip={skip}, limit={limit}, activo={activo})")
    
    query = db.query(Rol)
    
    if activo is not None:
        query = query.filter(Rol.activo == activo)
        logger.info(f"🔎 Aplicando filtro: activo={activo}")
    
    roles = query.offset(skip).limit(limit).all()
    logger.info(f"✅ Se encontraron {len(roles)} roles")
    
    return roles


# Funcion para crear roles CREAR ROL
def crear_rol(db: Session, rol: RolCreate):
    """Crear nuevo rol con logging detallado"""
    logger.info("=" * 60)
    logger.info("🆕 INICIANDO CREACIÓN DE ROL")
    logger.info(f"🎭 Nombre: {rol.nombre}")
    logger.info(f"🏷️ Tipo: {rol.tipo}")
    logger.info(f"📝 Descripción: {rol.descripcion}")
    logger.info("=" * 60)
    
    # Verificar si el nombre ya existe
    db_rol = get_rol_by_nombre(db, rol.nombre)
    if db_rol:
        logger.error(f"❌ ERROR: El rol '{rol.nombre}' ya existe")
        raise ValueError(f"El rol '{rol.nombre}' ya existe")
    
    # Verificar si el tipo ya existe
    db_rol_tipo = get_rol_by_tipo(db, rol.tipo.value)
    if db_rol_tipo:
        logger.error(f"❌ ERROR: Ya existe un rol con el tipo '{rol.tipo.value}'")
        raise ValueError(f"Ya existe un rol con el tipo '{rol.tipo.value}'")
    
    logger.info("📝 Creando objeto Rol...")
    db_rol = Rol(
        nombre=rol.nombre,
        descripcion=rol.descripcion,
        tipo=rol.tipo,
        activo=True
    )
    
    logger.info(f"📦 Objeto creado: {db_rol}")
    
    try:
        logger.info("💾 Guardando en base de datos...")
        db.add(db_rol)
        db.commit()
        db.refresh(db_rol)
        logger.info(f"✅ ROL CREADO EXITOSAMENTE: ID={db_rol.id}")
        return db_rol
    except IntegrityError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE INTEGRIDAD: {str(e)}")
        raise ValueError(f"Error de integridad: {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE BASE DE DATOS: {str(e)}")
        raise ValueError(f"Error de base de datos: {str(e)}")


# Funcion para actualizar roles ACTUALIZAR ROL
def actualizar_rol(db: Session, rol_id: int, rol: RolUpdate):
    """Actualizar rol existente con logging DETALLADO"""
    logger.info("=" * 60)
    logger.info(f"🔄 INICIANDO ACTUALIZACIÓN DE ROL ID: {rol_id}")
    logger.info("=" * 60)
    
    db_rol = get_rol_by_id(db, rol_id)
    if not db_rol:
        logger.error(f"❌ ERROR: Rol con ID {rol_id} NO encontrado")
        return None
    
    logger.info(f"📊 Datos ANTES de actualizar:")
    logger.info(f"   - Nombre: {db_rol.nombre}")
    logger.info(f"   - Tipo: {db_rol.tipo}")
    logger.info(f"   - Descripción: {db_rol.descripcion}")
    logger.info(f"   - Activo: {db_rol.activo}")
    
    update_data = rol.dict(exclude_unset=True)
    logger.info(f"📝 Datos RECIBIDOS para actualizar: {update_data}")
    
    # Si se cambia el nombre, verificar que no exista otro con ese nombre
    if 'nombre' in update_data:
        nombre_nuevo = update_data['nombre']
        rol_existente = get_rol_by_nombre(db, nombre_nuevo)
        if rol_existente and rol_existente.id != rol_id:
            logger.error(f"❌ ERROR: Ya existe otro rol con el nombre '{nombre_nuevo}'")
            raise ValueError(f"Ya existe otro rol con el nombre '{nombre_nuevo}'")
    
    # Si se cambia el tipo, verificar que no exista otro con ese tipo
    if 'tipo' in update_data:
        tipo_nuevo = update_data['tipo']
        if hasattr(tipo_nuevo, 'value'):
            tipo_nuevo = tipo_nuevo.value
        rol_existente = get_rol_by_tipo(db, tipo_nuevo)
        if rol_existente and rol_existente.id != rol_id:
            logger.error(f"❌ ERROR: Ya existe otro rol con el tipo '{tipo_nuevo}'")
            raise ValueError(f"Ya existe otro rol con el tipo '{tipo_nuevo}'")
    
    campos_actualizados = []
    for field, value in update_data.items():
        valor_anterior = getattr(db_rol, field)
        setattr(db_rol, field, value)
        campos_actualizados.append(f"{field}: {valor_anterior} → {value}")
        logger.info(f"   ✅ {field}: {valor_anterior} → {value}")
    
    if not campos_actualizados:
        logger.warning("⚠️ No se proporcionaron campos para actualizar")
        return db_rol
    
    logger.info(f"📊 Campos actualizados: {', '.join(campos_actualizados)}")
    
    try:
        logger.info("💾 Guardando cambios en base de datos...")
        db.commit()
        db.refresh(db_rol)
        
        logger.info(f"📊 Datos DESPUÉS de actualizar:")
        logger.info(f"   - Nombre: {db_rol.nombre}")
        logger.info(f"   - Tipo: {db_rol.tipo}")
        logger.info(f"   - Descripción: {db_rol.descripcion}")
        logger.info(f"   - Activo: {db_rol.activo}")
        logger.info(f"   - Updated At: {db_rol.updated_at}")
        
        logger.info(f"✅ ROL ACTUALIZADO EXITOSAMENTE: ID={db_rol.id}")
        return db_rol
    except IntegrityError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE INTEGRIDAD al actualizar: {str(e)}")
        raise ValueError(f"Error de integridad: {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE BASE DE DATOS al actualizar: {str(e)}")
        raise ValueError(f"Error de base de datos: {str(e)}")

