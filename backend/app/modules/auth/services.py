#C:\Users\PC\Desktop\Factu\backend\app\modules\auth\services.py
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.modules.usuarios.models import Usuario, EstadoUsuario, Sesion, EstadoSesion
from app.modules.auth.schemas import LoginRequest, RegisterRequest
from app.core.jwt import create_access_token, create_refresh_token, verify_token
from passlib.context import CryptContext
from datetime import datetime, timedelta
import logging
import secrets

# Esta configuaración hace que se imprima en la consola, todo aquello que se encuantra en Logger.
logger = logging.getLogger(__name__)

# Contexto para hashear contraseñas usando bcrypt.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#Compara una contraseña en texto plano, con el hash de la contraseña almacenada en la base de datos, y devuelve True si coinciden, o False si no.
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña en texto plano coincide con el hash.
     
    Args:
        plain_password: Contraseña en texto plano
        hashed_password: Hash de la contraseña almacenada
    
    Returns:
        True si coinciden, False si no
    """
    #esto se muestra en consola para depuracion, no se muestra en las contraseñas en texto plano, solo se muestra que se esta verificando la contraseña y si es valida o no.
    logger.info("🔐 Verificando contraseña...")
    result = pwd_context.verify(plain_password, hashed_password)
    logger.info(f"✅ Contraseña {'válida' if result else 'inválida'}")
    return result

#Toma una contraseña en texto plano y devuelve su hash, que es lo que se almacena en la base de datos. Esto es para que las contraseñas no se almacenen en texto plano, sino de forma segura.
def get_password_hash(password: str) -> str:
    """
    Hashea una contraseña.
    
    Args:
        password: Contraseña en texto plano
    
    Returns:
        Hash de la contraseña
    """
    #esto se muestra en consola para depuracion, no se muestra en las contraseñas en texto plano, solo se muestra que se esta hasheando la contraseña y el hash resultante.
    logger.info("🔐 Hasheando contraseña...")
    hashed = pwd_context.hash(password)
    logger.info(f"✅ Contraseña hasheada: {hashed[:20]}...")
    return hashed

#Consulta un usuario por su email en la base de datos y devuelve el objeto Usuario si lo encuentra, o None si no lo encuentra. Esto es para poder autenticar al usuario en el login.
def get_usuario_by_email(db: Session, email: str) -> Optional[Usuario]:
    """
    Busca un usuario por email.
    
    Args:
        db: Sesión de base de datos
        email: Email del usuario
    
    Returns:
        Usuario encontrado o None
    """
    
    logger.info(f"🔍 Buscando usuario con email: {email}")
    #hace la consulta a la base de datos para buscar el usuario por su email, y devuelve el objeto Usuario si lo encuentra, o None si no lo encuentra.
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    
    if usuario:
        logger.info(f"✅ Usuario encontrado: ID={usuario.id}, Nombre={usuario.nombre}")
    else:
        logger.warning(f"❌ Usuario con email {email} NO encontrado")
    
    return usuario

#Es el proceso de autenticación del usuario, que verifica que el usuario este activo y que el email y la contraseña sean correctos.
def authenticate_user(db: Session, email: str, password: str) -> Optional[Usuario]:
    """
    Autentica un usuario verificando email y contraseña.
    
    Raises:
        ValueError: Con mensajes específicos según el tipo de error
    """

    logger.info("=" * 60)
    logger.info(f"🔐 INICIANDO AUTENTICACIÓN para email: {email}")
    logger.info("=" * 60)
    
    # PASO 1: Buscar usuario en la base de datos, por email.
    usuario = get_usuario_by_email(db, email)
    #Evalua si existe el emal, si no existe, manda un menssaje de error, y termina la ejecucion de la funcion, si existe, continua con el siguiente paso.
    if not usuario:
        logger.error(f"❌ ERROR: Usuario con email {email} NO existe")
        raise ValueError("Credenciales inválidas. Verifica tu correo y contraseña.")
    
    logger.info(f"✅ Usuario encontrado: ID={usuario.id}, Nombre={usuario.nombre}, Estado={usuario.estado.value}")
    
    # PASO 2: Verificar estado del usuario
    if not usuario.puede_acceder():
        logger.error(f"❌ ERROR: Usuario {email} tiene estado {usuario.estado.value}")
        
        # Mensajes específicos según el estado
        if usuario.estado == EstadoUsuario.INACTIVO:
            raise ValueError(
                "❌ Usuario desactivado. Tu cuenta ha sido desactivada. "
                "Por favor, contacta al administrador o al equipo de soporte para reactivar tu cuenta."
            )
        elif usuario.estado == EstadoUsuario.BLOQUEADO:
            raise ValueError(
                "❌ Usuario bloqueado. Tu cuenta ha sido bloqueada por seguridad. "
                "Por favor, contacta al administrador o al equipo de soporte."
            )
        elif usuario.estado == EstadoUsuario.PENDIENTE:
            raise ValueError(
                "❌ Usuario pendiente de activación. Tu cuenta aún no ha sido activada. "
                "Por favor, verifica tu correo electrónico o contacta al administrador."
            )
        else:
            raise ValueError(
                f"❌ Usuario con estado {usuario.estado.value}. No puede acceder al sistema. "
                "Por favor, contacta al administrador."
            )
    
    # PASO 3: Verificar contraseña
    if not verify_password(password, usuario.password_hash):
        logger.error(f"❌ ERROR: Contraseña incorrecta para {email}")
        raise ValueError("Credenciales inválidas. Verifica tu correo y contraseña.")
    
    logger.info(f"✅ USUARIO AUTENTICADO EXITOSAMENTE: ID={usuario.id}, Email={email}, Estado={usuario.estado.value}")
    
    # PASO 4: Actualizar último login
    usuario.last_login = datetime.utcnow()
    db.commit()
    
    return usuario

#Registra una nueva sesión para el usuario autenticado, generando un access token y un refresh token, y guardando la sesión en la base de datos.
def create_user_session(
    db: Session,
    usuario_id: int,
    ip_address: str = None,
    user_agent: str = None
) -> tuple[str, str, int]:
    """
    Crea una nueva sesión para el usuario autenticado.
    
    Args:
        db: Sesión de base de datos
        usuario_id: ID del usuario
        ip_address: IP del cliente
        user_agent: User-Agent del cliente
    
    Returns:
        Tupla (access_token, refresh_token, session_id)
    """

    logger.info("=" * 60)
    logger.info(f"🎫 CREANDO SESIÓN para usuario ID: {usuario_id}")
    logger.info("=" * 60)
    
    # Crear tokens y refresca el token de acceso.
    access_token = create_access_token(data={"sub": str(usuario_id)})
    refresh_token = create_refresh_token(data={"sub": str(usuario_id), "type": "refresh"})
    
    logger.info(f"🔑 Access Token: {access_token[:30]}...")
    logger.info(f"🔄 Refresh Token: {refresh_token[:30]}...")
    
    # Crear registro de sesión
    session = Sesion(
        usuario_id=usuario_id,
        token=access_token,
        ip_address=ip_address,
        user_agent=user_agent,
        estado=EstadoSesion.ACTIVA,
        activo=True,
        expires_at=datetime.utcnow() + timedelta(minutes=30)
    )
    
    try:
        db.add(session)
        db.commit()
        db.refresh(session)
        
        logger.info(f"✅ SESIÓN CREADA EXITOSAMENTE: ID={session.id}")
        logger.info(f"📊 Detalles de sesión:")
        logger.info(f"   - Usuario ID: {session.usuario_id}")
        logger.info(f"   - IP: {session.ip_address}")
        logger.info(f"   - User Agent: {session.user_agent}")
        logger.info(f"   - Expira: {session.expires_at}")
        
        return access_token, refresh_token, session.id
    
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"❌ ERROR al crear sesión: {str(e)}")
        raise ValueError(f"Error al crear sesión: {str(e)}")

#Orquesta todo el proceso de login.
def login(db: Session, credentials: LoginRequest, ip_address: str = None, user_agent: str = None):
    """
    Proceso completo de login.
    
    Raises:
        ValueError: Con mensajes específicos según el tipo de error
    """
    logger.info("=" * 60)
    logger.info("🚀 INICIANDO PROCESO DE LOGIN")
    logger.info("=" * 60)
    
    # Autenticar usuario (puede lanzar ValueError con mensajes específicos)
    usuario = authenticate_user(db, credentials.email, credentials.password)
    
    # Crear sesión y llama la generacion de tokens, y devuelve el access token.
    access_token, refresh_token, session_id = create_user_session(
        db, usuario.id, ip_address, user_agent
    )
    
    logger.info("=" * 60)
    logger.info("✅ LOGIN EXITOSO")
    logger.info("=" * 60)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_id": usuario.id,
        "user_name": usuario.nombre,
        "user_email": usuario.email,
        "session_id": session_id
    }

#Regsitra nuevos usuarios en el sistema.
def register_user(db: Session, user_data: RegisterRequest):
    """
    Registra un nuevo usuario en el sistema.
    
    Args:
        db: Sesión de base de datos
        user_data: Datos del usuario a registrar
    
    Returns:
        Usuario creado
    """
    logger.info("=" * 60)
    logger.info("🆕 INICIANDO REGISTRO DE USUARIO")
    logger.info(f"📧 Email: {user_data.email}")
    logger.info(f"👤 Nombre: {user_data.nombre}")
    logger.info(f"🎭 Rol ID: {user_data.rol_id}")
    logger.info(f"🏢 Departamento ID: {user_data.departamento_id}")
    logger.info("=" * 60)
    
    # Verificar si el email ya existe
    existing_user = get_usuario_by_email(db, user_data.email)
    if existing_user:
        logger.error(f"❌ ERROR: El email {user_data.email} ya está registrado")
        raise ValueError(f"El email {user_data.email} ya está registrado")
    
    # Hashear contraseña
    hashed_password = get_password_hash(user_data.password)
    
    # Crear usuario con fecha de creación explícita
    ahora = datetime.utcnow()
    
    nuevo_usuario = Usuario(
        nombre=user_data.nombre,
        email=user_data.email,
        password_hash=hashed_password,
        telefono=user_data.telefono,
        departamento_id=user_data.departamento_id,
        rol_id=user_data.rol_id,
        estado=EstadoUsuario.ACTIVO,
        created_at=ahora
    )
    
    try:
        logger.info(f"💾 Guardando nuevo usuario en base de datos...")
        logger.info(f"📅 Fecha de creación asignada: {ahora}")
        
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)
        
        logger.info("=" * 60)
        logger.info(f"✅ USUARIO REGISTRADO EXITOSAMENTE")
        logger.info(f"   - ID: {nuevo_usuario.id}")
        logger.info(f"   - Nombre: {nuevo_usuario.nombre}")
        logger.info(f"   - Email: {nuevo_usuario.email}")
        logger.info(f"   - Departamento ID: {nuevo_usuario.departamento_id}")
        logger.info(f"   - Rol ID: {nuevo_usuario.rol_id}")
        logger.info(f"   - Estado: {nuevo_usuario.estado}")
        logger.info(f"   - Created At: {nuevo_usuario.created_at}")
        logger.info("=" * 60)
        
        return nuevo_usuario
    
    except IntegrityError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE INTEGRIDAD: {str(e)}")
        raise ValueError(f"Error de integridad: {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"❌ ERROR DE BASE DE DATOS: {str(e)}")
        raise ValueError(f"Error de base de datos: {str(e)}")

#Invalida el token de sesión marcandolo com cerrado en la base de datos, y actualiza el estado de la sesión a cerrada.
#Esto es para que el usuario no pueda seguir usando el token después de cerrar sesión.
def logout(db: Session, token: str):
    """
    Cierra la sesión del usuario invalidando el token.
    
    Args:
        db: Sesión de base de datos
        token: Token de la sesión a cerrar
    
    Returns:
        True si se cerró correctamente
    """
    logger.info("=" * 60)
    logger.info("🚪 INICIANDO LOGOUT")
    logger.info(f"🔑 Token: {token[:30]}...")
    logger.info("=" * 60)
    
    # Buscar sesión por token, en la tabla de sesiones.
    session = db.query(Sesion).filter(Sesion.token == token).first()
    #Si no encuantra la sesión, debuelve un False dando a entender que no hay secion activa con ese token.
    if not session:
        logger.warning(f"⚠️ No se encontró sesión con el token proporcionado")
        return False
    
    # Marcar sesión como cerrada
    session.estado = EstadoSesion.CERRADA
    session.activo = False
    session.logout_at = datetime.utcnow()
    
    try:
        db.commit()
        logger.info(f"✅ SESIÓN CERRADA EXITOSAMENTE: ID={session.id}")
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"❌ ERROR al cerrar sesión: {str(e)}")
        raise ValueError(f"Error al cerrar sesión: {str(e)}")

#valida el refresh tken, y genera un nuevo access token, sin pedir credenciales al usuario,
#esto es para que el usuario no tenga que volver a loguearse cada vez que el access token expira.
def refresh_access_token(db: Session, refresh_token: str):
    """
    Refresca el access token usando un refresh token válido.
    
    Raises:
        ValueError: Con mensajes específicos según el tipo de error
    """
    logger.info("=" * 60)
    logger.info("🔄 INICIANDO REFRESH DE TOKEN")
    logger.info(f"🔑 Refresh Token: {refresh_token[:30]}...")
    logger.info("=" * 60)
    
    # Verificar refresh token.
    payload = verify_token(refresh_token)
    
    if not payload:
        logger.error("❌ ERROR: Refresh token inválido o expirado")
        raise ValueError("Refresh token inválido o expirado")
    
    # Verificar que sea un refresh token
    if payload.get("type") != "refresh":
        logger.error("❌ ERROR: Token no es un refresh token")
        raise ValueError("Token no es un refresh token")
    
    # Obtener usuario extrayendo el id del campo "sub" del token.
    usuario_id = payload.get("sub")
    if not usuario_id:
        logger.error("❌ ERROR: Token no contiene ID de usuario")
        raise ValueError("Token inválido")
    
    logger.info(f"👤 Usuario ID del token: {usuario_id}")
    
    # Verificar que el usuario existe con el id extraido del token.
    usuario = db.query(Usuario).filter(Usuario.id == int(usuario_id)).first()
    
    if not usuario:
        logger.error(f"❌ ERROR: Usuario {usuario_id} no existe")
        raise ValueError("Usuario no encontrado")
    
    # Verificar estado del usuario usando puede_acceder()(activo, o desactivado, o bloqueado, o pendiente)
    if not usuario.puede_acceder():
        logger.error(f"❌ ERROR: Usuario {usuario_id} tiene estado {usuario.estado.value}")
        
        if usuario.estado == EstadoUsuario.INACTIVO:
            raise ValueError(
                "Usuario desactivado. Tu cuenta ha sido desactivada. "
                "Por favor, contacta al administrador."
            )
        elif usuario.estado == EstadoUsuario.BLOQUEADO:
            raise ValueError(
                "Usuario bloqueado. Tu cuenta ha sido bloqueada. "
                "Por favor, contacta al administrador."
            )
        else:
            raise ValueError(
                f"Usuario con estado {usuario.estado.value}. No puede acceder al sistema."
            )
    
    # Crear nuevo access token
    new_access_token = create_access_token(data={"sub": usuario_id})
    
    logger.info(f"✅ NUEVO ACCESS TOKEN CREADO: {new_access_token[:30]}...")
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }