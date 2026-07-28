# C:\Users\PC\Desktop\Factu\backend\app\modules\usuarios\routes.py
from typing import Optional
from fastapi import APIRouter, Depends, Request, status, HTTPException
from sqlalchemy.orm import Session
from app.core.rate_limiter import rate_limit
from app.core.config import settings
from app.core.database import get_db
# ✅ AGREGADO: require_permission
from app.core.dependencies import get_current_user, require_role, require_permission
from app.modules.usuarios.models import Usuario

from app.modules.usuarios.schemas import (
    DepartamentoCreate,
    DepartamentoListResponse,
    DepartamentoResponse,
    DepartamentoUpdate,
    RolCreate,
    RolListResponse,
    RolResponse,
    RolUpdate,
    UsuarioCreate,
    UsuarioUpdate,
    CambiarContrasenaRequest,
    UsuarioResponse,
    UsuarioListResponse,
    MessageResponse
)

from app.modules.usuarios.services import (
    get_usuarios,
    get_usuario_by_id,
    crear_usuario,
    actualizar_usuario,
    eliminar_usuario,
    cambiar_contrasena
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

# ===========================================================
# ENDPOINTS DE USUARIOS (PROTEGIDOS CON PERMISOS)
# ===========================================================

@router.get(
    "/listar",
    response_model=UsuarioListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(rate_limit(
        limit=settings.RATE_LIMIT_DEFAULT,
        window=settings.RATE_LIMIT_WINDOW,
        key_prefix="usuarios_listar"
    ))],
    summary="Listar usuarios",
    description="Obtiene una lista de usuarios. Requiere permiso 'usuario:leer'."
)
def listar_usuarios(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_permission("usuario:leer")),
    skip: int = 0,
    limit: int = 10, # Por defecto muestra 10
    busqueda: Optional[str] = None, # <-- NUEVO PARÁMETRO
    estado: Optional[str] = None
):
    logger.info("=" * 60)
    logger.info(f"📋 ENDPOINT: GET /usuarios/listar")
    logger.info(f"👤 Usuario autenticado: ID={current_user.id}")
    logger.info(f"📊 Parámetros: skip={skip}, limit={limit}, busqueda={busqueda}, estado={estado}")
    logger.info("=" * 60)
    
    usuarios = get_usuarios(db, skip=skip, limit=limit, busqueda=busqueda, estado=estado)
    logger.info(f"✅ Retornando {len(usuarios)} usuarios")

    return UsuarioListResponse(
        total=len(usuarios),
        usuarios=usuarios
    )


@router.get(
    "/obtener/{usuario_id}",
    response_model=UsuarioResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(rate_limit(
        limit=settings.RATE_LIMIT_DEFAULT,
        window=settings.RATE_LIMIT_WINDOW,
        key_prefix="usuarios_obtener"
    ))],
    summary="Obtener usuario por ID",
    description="Obtiene los detalles completos de un usuario específico por su ID. Requiere permiso 'usuario:leer'."
)
def obtener_usuario(
    request: Request,
    usuario_id: int,
    db: Session = Depends(get_db),
    # ✅ CAMBIO: Ahora usa require_permission
    current_user: Usuario = Depends(require_permission("usuario:leer"))
):
    logger.info("=" * 60)
    logger.info(f"📋 ENDPOINT: GET /usuarios/obtener/{usuario_id}")
    logger.info(f"👤 Usuario autenticado: ID={current_user.id}")
    logger.info("=" * 60)
    
    usuario = get_usuario_by_id(db, usuario_id)
    
    if not usuario:
        logger.error(f"❌ Usuario ID={usuario_id} NO encontrado")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {usuario_id} no encontrado"
        )
    
    logger.info(f"✅ Retornando usuario ID={usuario.id}, Nombre={usuario.nombre}")
    return usuario


@router.post(
    "/crear",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit(
        limit=10,
        window=60,
        key_prefix="usuarios_crear",
        error_message="Demasiadas solicitudes de creación de usuarios. Espera 1 minuto."
    ))],
    summary="Crear nuevo usuario",
    description="Crea un nuevo usuario en el sistema. Requiere permiso 'usuario:crear'."
)
def crear_usuario_endpoint(
    request: Request,
    usuario: UsuarioCreate,
    db: Session = Depends(get_db),
    # ✅ CAMBIO: Ahora usa require_permission en lugar de require_role
    current_user: Usuario = Depends(require_permission("usuario:crear"))
):
    logger.info("=" * 60)
    logger.info(f"📋 ENDPOINT: POST /usuarios/crear")
    logger.info(f"👤 Creado por: ID={current_user.id}, Email={current_user.email}")
    logger.info(f"📧 Email del nuevo usuario: {usuario.email}")
    logger.info(f"👤 Nombre del nuevo usuario: {usuario.nombre}")
    logger.info("=" * 60)
    
    try:
        db_usuario = crear_usuario(db, usuario)
        logger.info(f"✅ Usuario creado exitosamente: ID={db_usuario.id}")
        return db_usuario
    except ValueError as e:
        logger.error(f"❌ Error al crear usuario: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put(
    "/actualizar/{usuario_id}",
    response_model=UsuarioResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(rate_limit(
        limit=20,
        window=60,
        key_prefix="usuarios_actualizar",
        error_message="Demasiadas solicitudes de actualización. Espera 1 minuto."
    ))],
    summary="Actualizar usuario completo",
    description="Actualiza todos los datos de un usuario existente. Requiere permiso 'usuario:actualizar'."
)
def actualizar_usuario_endpoint(
    request: Request,
    usuario_id: int,
    usuario: UsuarioUpdate,
    db: Session = Depends(get_db),
    # ✅ CAMBIO: Ahora usa require_permission
    current_user: Usuario = Depends(require_permission("usuario:actualizar"))
):
    logger.info("=" * 60)
    logger.info(f"📋 ENDPOINT: PUT /usuarios/actualizar/{usuario_id}")
    logger.info(f"👤 Actualizado por: ID={current_user.id}, Email={current_user.email}")
    logger.info(f"📝 Datos recibidos: {usuario.model_dump(exclude_unset=True)}") # Actualizado a model_dump para Pydantic V2
    logger.info("=" * 60)
    
    try:
        db_usuario = actualizar_usuario(db, usuario_id, usuario)
        
        if not db_usuario:
            logger.error(f"❌ Usuario ID={usuario_id} NO encontrado")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con ID {usuario_id} no encontrado"
            )
        
        logger.info(f"✅ Usuario ID={usuario_id} actualizado exitosamente")
        return db_usuario
    except ValueError as e:
        logger.error(f"❌ Error al actualizar usuario: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/eliminar/{usuario_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(rate_limit(
        limit=5,
        window=60,
        key_prefix="usuarios_eliminar_permanente",
        error_message="Demasiadas solicitudes de eliminación. Espera 1 minuto."
    ))],
    summary="💀 Eliminar usuario PERMANENTEMENTE",
    description="ELIMINACIÓN PERMANENTE. Solo SUPER_ADMIN (mantenido por rol por ser acción crítica)."
)
def eliminar_usuario_endpoint(
    request: Request,
    usuario_id: int,
    db: Session = Depends(get_db),
    # ⚠️ NOTA: Se mantiene require_role porque "usuario:eliminar" no está en tu lista de permisos seed.
    current_user: Usuario = Depends(require_role(["SUPER_ADMIN"]))
):
    logger.info("=" * 60)
    logger.info(f"📋 ENDPOINT: DELETE /usuarios/eliminar/{usuario_id}")
    logger.info(f"💀 ACCIÓN: ELIMINACIÓN PERMANENTE (HARD DELETE)")
    logger.info(f"👤 Ejecutado por: ID={current_user.id}, Email={current_user.email}")
    logger.info("=" * 60)
    
    try:
        resultado = eliminar_usuario(
            db=db,
            usuario_id=usuario_id,
            super_admin_id=current_user.id
        )
        
        logger.info(f"✅ {resultado['mensaje']}")
        return MessageResponse(message=resultado["mensaje"])
    
    except ValueError as e:
        logger.error(f"❌ ERROR al eliminar usuario: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch(
    "/activar/{usuario_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(rate_limit(
        limit=10,
        window=60,
        key_prefix="usuarios_activar",
        error_message="Demasiadas solicitudes. Espera 1 minuto."
    ))],
    summary="Activar usuario",
    description="Activa un usuario que estaba desactivado. (Mantenido por rol, no hay permiso 'usuario:activar' en seed)."
)
def activar_usuario_endpoint(
    request: Request,
    usuario_id: int,
    db: Session = Depends(get_db),
    # ⚠️ NOTA: Se mantiene require_role porque "usuario:activar" no está en tu lista de permisos seed.
    current_user: Usuario = Depends(require_role(["SUPER_ADMIN", "ADMIN"]))
):
    logger.info("=" * 60)
    logger.info(f"📋 ENDPOINT: PATCH /usuarios/activar/{usuario_id}")
    logger.info(f"👤 Solicitado por: ID={current_user.id}, Email={current_user.email}")
    logger.info("=" * 60)
    
    from app.modules.usuarios.services import activar_usuario
    
    try:
        resultado = activar_usuario(db=db, usuario_id=usuario_id)
        
        if not resultado["cambio_realizado"]:
            logger.warning(f"⚠️ {resultado['mensaje']}")
            return MessageResponse(message=resultado["mensaje"])
        
        logger.info(f"✅ {resultado['mensaje']}")
        return MessageResponse(message=resultado["mensaje"])
    
    except ValueError as e:
        logger.error(f"❌ ERROR al activar usuario: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch(
    "/desactivar/{usuario_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(rate_limit(
        limit=10,
        window=60,
        key_prefix="usuarios_desactivar",
        error_message="Demasiadas solicitudes. Espera 1 minuto."
    ))],
    summary="Desactivar usuario",
    description="Desactiva un usuario sin eliminarlo permanentemente. Requiere permiso 'usuario:desactivar'."
)
def desactivar_usuario_endpoint(
    request: Request,
    usuario_id: int,
    db: Session = Depends(get_db),
    # ✅ CAMBIO: Ahora usa require_permission
    current_user: Usuario = Depends(require_permission("usuario:desactivar"))
):
    logger.info("=" * 60)
    logger.info(f"📋 ENDPOINT: PATCH /usuarios/desactivar/{usuario_id}")
    logger.info(f"👤 Solicitado por: ID={current_user.id}, Email={current_user.email}")
    logger.info("=" * 60)
    
    from app.modules.usuarios.services import desactivar_usuario
    
    try:
        resultado = desactivar_usuario(db=db, usuario_id=usuario_id)
        
        if not resultado["cambio_realizado"]:
            logger.warning(f"⚠️ {resultado['mensaje']}")
            return MessageResponse(message=resultado["mensaje"])
        
        logger.info(f"✅ {resultado['mensaje']}")
        return MessageResponse(message=resultado["mensaje"])
    
    except ValueError as e:
        logger.error(f"❌ ERROR al desactivar usuario: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ===========================================================
# ENDPOINTS DE DEPARTAMENTOS (PROTEGIDOS: SOLO ADMIN Y SUPER_ADMIN)
# ===========================================================

@router.get(
    "/departamentos/listar",
    response_model=DepartamentoListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(rate_limit(
        limit=settings.RATE_LIMIT_DEFAULT,
        window=settings.RATE_LIMIT_WINDOW,
        key_prefix="departamentos_listar"
    ))],
    summary="Listar departamentos",
    description="Obtiene una lista de todos los departamentos. Solo ADMIN o SUPER_ADMIN."
)
def listar_departamentos(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["SUPER_ADMIN", "ADMIN"])), # ✅ PROTEGIDO
    skip: int = 0,
    limit: int = 100,
    activo: Optional[bool] = None
):
    logger.info("=" * 60)
    logger.info(f"📋 ENDPOINT: GET /usuarios/departamentos/listar")
    logger.info(f"👤 Usuario autenticado: ID={current_user.id}, Email={current_user.email}")
    logger.info("=" * 60)
    
    from app.modules.usuarios.services import get_departamentos
    departamentos = get_departamentos(db, skip=skip, limit=limit, activo=activo)
    logger.info(f"✅ Retornando {len(departamentos)} departamentos")
    
    return DepartamentoListResponse(total=len(departamentos), departamentos=departamentos)


@router.get(
    "/departamentos/obtener/{departamento_id}",
    response_model=DepartamentoResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(rate_limit(
        limit=settings.RATE_LIMIT_DEFAULT,
        window=settings.RATE_LIMIT_WINDOW,
        key_prefix="departamentos_obtener"
    ))],
    summary="Obtener departamento por ID",
    description="Obtiene los detalles de un departamento específico. Solo ADMIN o SUPER_ADMIN."
)
def obtener_departamento(
    request: Request,
    departamento_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["SUPER_ADMIN", "ADMIN"])) # ✅ PROTEGIDO
):
    logger.info("=" * 60)
    logger.info(f"📋 ENDPOINT: GET /usuarios/departamentos/obtener/{departamento_id}")
    logger.info(f"👤 Usuario autenticado: ID={current_user.id}")
    logger.info("=" * 60)
    
    from app.modules.usuarios.services import get_departamento_by_id
    departamento = get_departamento_by_id(db, departamento_id)
    
    if not departamento:
        logger.error(f"❌ Departamento ID={departamento_id} NO encontrado")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Departamento con ID {departamento_id} no encontrado"
        )
    
    logger.info(f"✅ Retornando departamento ID={departamento.id}, Nombre={departamento.nombre}")
    return departamento


@router.post(
    "/departamentos/crear",
    response_model=DepartamentoResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit(
        limit=10,
        window=60,
        key_prefix="departamentos_crear",
        error_message="Demasiadas solicitudes de creación de departamentos. Espera 1 minuto."
    ))],
    summary="Crear nuevo departamento",
    description="Crea un nuevo departamento. Solo ADMIN o SUPER_ADMIN."
)
def crear_departamento_endpoint(
    request: Request,
    departamento: DepartamentoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["SUPER_ADMIN", "ADMIN"])) # ✅ PROTEGIDO
):
    logger.info("=" * 60)
    logger.info(f"📋 ENDPOINT: POST /usuarios/departamentos/crear")
    logger.info(f"👤 Creado por: ID={current_user.id}, Email={current_user.email}")
    logger.info(f"🏢 Nombre del departamento: {departamento.nombre}")
    logger.info("=" * 60)
    
    from app.modules.usuarios.services import crear_departamento
    try:
        db_departamento = crear_departamento(db, departamento)
        logger.info(f"✅ Departamento creado exitosamente: ID={db_departamento.id}")
        return db_departamento
    except ValueError as e:
        logger.error(f"❌ Error al crear departamento: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put(
    "/departamentos/actualizar/{departamento_id}",
    response_model=DepartamentoResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(rate_limit(
        limit=20,
        window=60,
        key_prefix="departamentos_actualizar",
        error_message="Demasiadas solicitudes de actualización. Espera 1 minuto."
    ))],
    summary="Actualizar departamento",
    description="Actualiza los datos de un departamento existente. Solo ADMIN o SUPER_ADMIN."
)
def actualizar_departamento_endpoint(
    request: Request,
    departamento_id: int,
    departamento: DepartamentoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["SUPER_ADMIN", "ADMIN"])) # ✅ PROTEGIDO
):
    logger.info("=" * 60)
    logger.info(f"📋 ENDPOINT: PUT /usuarios/departamentos/actualizar/{departamento_id}")
    logger.info(f"👤 Actualizado por: ID={current_user.id}, Email={current_user.email}")
    logger.info("=" * 60)
    
    from app.modules.usuarios.services import actualizar_departamento
    try:
        db_departamento = actualizar_departamento(db, departamento_id, departamento)
        if not db_departamento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Departamento con ID {departamento_id} no encontrado"
            )
        logger.info(f"✅ Departamento ID={departamento_id} actualizado exitosamente")
        return db_departamento
    except ValueError as e:
        logger.error(f"❌ Error al actualizar departamento: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ===========================================================
# ENDPOINTS DE ROLES (PROTEGIDOS: SOLO ADMIN Y SUPER_ADMIN)
# ===========================================================

@router.get(
    "/roles/listar",
    response_model=RolListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(rate_limit(
        limit=settings.RATE_LIMIT_DEFAULT,
        window=settings.RATE_LIMIT_WINDOW,
        key_prefix="roles_listar"
    ))],
    summary="Listar roles",
    description="Obtiene una lista de todos los roles del sistema. Solo ADMIN o SUPER_ADMIN."
)
def listar_roles(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["SUPER_ADMIN", "ADMIN"])), # ✅ PROTEGIDO
    skip: int = 0,
    limit: int = 100,
    activo: Optional[bool] = None
):
    logger.info("=" * 60)
    logger.info(f"📋 ENDPOINT: GET /usuarios/roles/listar")
    logger.info(f"👤 Usuario autenticado: ID={current_user.id}, Email={current_user.email}")
    logger.info("=" * 60)
    
    from app.modules.usuarios.services import get_roles
    roles = get_roles(db, skip=skip, limit=limit, activo=activo)
    logger.info(f"✅ Retornando {len(roles)} roles")
    
    return RolListResponse(total=len(roles), roles=roles)


@router.get(
    "/roles/obtener/{rol_id}",
    response_model=RolResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(rate_limit(
        limit=settings.RATE_LIMIT_DEFAULT,
        window=settings.RATE_LIMIT_WINDOW,
        key_prefix="roles_obtener"
    ))],
    summary="Obtener rol por ID",
    description="Obtiene los detalles completos de un rol específico. Solo ADMIN o SUPER_ADMIN."
)
def obtener_rol(
    request: Request,
    rol_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["SUPER_ADMIN", "ADMIN"])) # ✅ PROTEGIDO
):
    logger.info("=" * 60)
    logger.info(f"📋 ENDPOINT: GET /usuarios/roles/obtener/{rol_id}")
    logger.info(f"👤 Usuario autenticado: ID={current_user.id}")
    logger.info("=" * 60)
    
    from app.modules.usuarios.services import get_rol_by_id
    rol = get_rol_by_id(db, rol_id)
    
    if not rol:
        logger.error(f"❌ Rol ID={rol_id} NO encontrado")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rol con ID {rol_id} no encontrado"
        )
    
    logger.info(f"✅ Retornando rol ID={rol.id}, Nombre={rol.nombre}")
    return rol


@router.post(
    "/roles/crear",
    response_model=RolResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit(
        limit=10,
        window=60,
        key_prefix="roles_crear",
        error_message="Demasiadas solicitudes de creación de roles. Espera 1 minuto."
    ))],
    summary="Crear nuevo rol",
    description="Crea un nuevo rol en el sistema. Solo ADMIN o SUPER_ADMIN."
)
def crear_rol_endpoint(
    request: Request,
    rol: RolCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["SUPER_ADMIN", "ADMIN"])) # ✅ PROTEGIDO
):
    logger.info("=" * 60)
    logger.info(f"📋 ENDPOINT: POST /usuarios/roles/crear")
    logger.info(f"👤 Creado por: ID={current_user.id}, Email={current_user.email}")
    logger.info(f"🎭 Nombre del rol: {rol.nombre}")
    logger.info(f"🏷️ Tipo del rol: {rol.tipo}")
    logger.info("=" * 60)
    
    from app.modules.usuarios.services import crear_rol
    try:
        db_rol = crear_rol(db, rol)
        logger.info(f"✅ Rol creado exitosamente: ID={db_rol.id}")
        return db_rol
    except ValueError as e:
        logger.error(f"❌ Error al crear rol: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put(
    "/roles/actualizar/{rol_id}",
    response_model=RolResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(rate_limit(
        limit=20,
        window=60,
        key_prefix="roles_actualizar",
        error_message="Demasiadas solicitudes de actualización. Espera 1 minuto."
    ))],
    summary="Actualizar rol",
    description="Actualiza los datos de un rol existente. Solo ADMIN o SUPER_ADMIN."
)
def actualizar_rol_endpoint(
    request: Request,
    rol_id: int,
    rol: RolUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["SUPER_ADMIN", "ADMIN"])) # ✅ PROTEGIDO
):
    logger.info("=" * 60)
    logger.info(f"📋 ENDPOINT: PUT /usuarios/roles/actualizar/{rol_id}")
    logger.info(f"👤 Actualizado por: ID={current_user.id}, Email={current_user.email}")
    logger.info("=" * 60)
    
    from app.modules.usuarios.services import actualizar_rol
    try:
        db_rol = actualizar_rol(db, rol_id, rol)
        if not db_rol:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rol con ID {rol_id} no encontrado"
            )
        logger.info(f"✅ Rol ID={rol_id} actualizado exitosamente")
        return db_rol
    except ValueError as e:
        logger.error(f"❌ Error al actualizar rol: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))