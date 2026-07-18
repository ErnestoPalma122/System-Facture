#C:\Users\PC\Desktop\Factu\backend\app\modules\usuarios\routes.py
from typing import Optional
from fastapi import APIRouter, Depends, Request, status, HTTPException
from sqlalchemy.orm import Session
from app.core.rate_limiter import rate_limit
from app.core.config import settings
from app.core.database import get_db
# validan tokens, y inyecta roles.
from app.core.dependencies import get_current_user, require_role
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
# ENDPOINTS DE USUARIOS (PROTEGIDOS CON JWT)
# Rutas descriptivas para mayor control
# ===========================================================


#Este endpoint muestra de modo lista los usuarios guardados en la base de datos
@router.get(
    "/listar",
    #llama una funcion de Schemas haciendo que lo que se responda tenga una forma exacta,
    #funciona para la documentacion de swagger
    response_model=UsuarioListResponse,
    #estatus HTTP de todo bien tendra un codigo de 200
    status_code=status.HTTP_200_OK,
    #Define el limite de consultas para el end point
    dependencies=[Depends(rate_limit(
        limit=settings.RATE_LIMIT_DEFAULT, #---define el limites de intentos
        window=settings.RATE_LIMIT_WINDOW, #---define el tiempo para esos intentos
        key_prefix="usuarios_listar"
    ))],
    #Solo es texto para la documentacion de swagger.
    summary="Listar usuarios",
    description="Obtiene una lista de todos los usuarios del sistema. Requiere autenticación."
)
#funcion que maneja la peticion /listar
def listar_usuarios(
    #Extrae la peticion HTTP y lo inyecta en la funcion
    request: Request,
    #Inyeccion de la conexion de la base de datos, no crea la conexion, si no que lo inyecta
    db: Session = Depends(get_db),
    #Capa de seguridad con JWT y/o Roles.
    current_user: Usuario = Depends(get_current_user),
    #Es un parametro de consulta, que si no se llena automaticamnte envia 0.
    skip: int = 0,
    #Define el limite de consulta, para que el servior no caiga.
    limit: int = 100,
    #Esta variable puede ser String o o None.
    estado: Optional[str] = None  # ← CAMBIADO de 'activo' a 'estado'

#
):
    #Informacion de documentacion interna
    """
    Endpoint para listar usuarios con paginación y filtros.
    
    Ruta: GET /usuarios/listar
    
    Parámetros de filtro:
    - estado: ACTIVO, INACTIVO, BLOQUEADO, PENDIENTE (opcional)
    
    Rate limit: 100 solicitudes por minuto (configuración por defecto).
    Protección: Requiere autenticación JWT.
    """
    
    logger.info("=" * 60)
    logger.info(f"📋 ENDPOINT: GET /usuarios/listar")
    logger.info(f"👤 Usuario autenticado: ID={current_user.id}, Email={current_user.email}")
    logger.info(f"📊 Parámetros: skip={skip}, limit={limit}, estado={estado}")
    logger.info("=" * 60)
    
    #Llama a services(get_usuarios) y inyecta la consulta SQL.
    usuarios = get_usuarios(db, skip=skip, limit=limit, estado=estado)  # ← CAMBIADO
    logger.info(f"✅ Retornando {len(usuarios)} usuarios")

    #Llama a schemas(UsuarioListResponse)
    return UsuarioListResponse(
        #Funcion que cuanta los elementos de una lista y los manda junto con: UsuarioListResponse
        total=len(usuarios),
        #La consulta lo manda junto con: UsuarioListResponse
        usuarios=usuarios
    )

# Este endponit busca a un usuario espesifico por el ID en la base de datos
@router.get(
    "/obtener/{usuario_id}",
    #llama una funcion de Schemas haciendo que lo que se responda tenga una forma exacta,
    #funciona para la documentacion de swagger
    response_model=UsuarioResponse,
    #estatus HTTP de todo bien tendra un codigo de 200
    status_code=status.HTTP_200_OK,
    #Define el limite de consultas
    dependencies=[Depends(rate_limit(
        limit=settings.RATE_LIMIT_DEFAULT, #---define el limites de intentos
        window=settings.RATE_LIMIT_WINDOW, #---define el tiempo para esos intentos
        key_prefix="usuarios_obtener"
    ))],
    summary="Obtener usuario por ID",
    description="Obtiene los detalles completos de un usuario específico por su ID. Requiere autenticación."
)
def obtener_usuario(
    #Extrae la peticion HTTP y lo inyecta en la funcion
    request: Request,
    #Es un parametro que se convierte a entero, para que la URL lo pueda leer y hacer la consulta.
    usuario_id: int,
    #Inyeccion de la conexion de la base de datos, no crea la conexion, si no que lo inyecta
    db: Session = Depends(get_db),
    #Capa de seguridad con JWT y/o Roles.
    current_user: Usuario = Depends(get_current_user)
):
    #Informacion de documentacion interna
    """
    Endpoint para obtener un usuario específico por ID.
    
    Ruta: GET /usuarios/obtener/{usuario_id}
    
    Rate limit: 100 solicitudes por minuto.
    Protección: Requiere autenticación JWT.
    """
    logger.info("=" * 60)
    logger.info(f"📋 ENDPOINT: GET /usuarios/obtener/{usuario_id}")
    logger.info(f"👤 Usuario autenticado: ID={current_user.id}")
    logger.info("=" * 60)
    
    #Llama a get_usuario_by_id de services, e inyecta informacion de la base de datos
    usuario = get_usuario_by_id(db, usuario_id)
    
    #Hace una validacion de si encuentra el usuario o no 
    if not usuario:
        logger.error(f"❌ Usuario ID={usuario_id} NO encontrado")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {usuario_id} no encontrado"
        )
    
    logger.info(f"✅ Retornando usuario ID={usuario.id}, Nombre={usuario.nombre}")
    return usuario
#---------------------------------------------------------------------------------------
#este endpoint Crea usuarios 
@router.post(
    "/crear",
    #llama una funcion de Schemas haciendo que lo que se responda tenga una forma exacta,
    #funciona para la documentacion de swagger    
    response_model = UsuarioResponse,
    #estatus HTTP de cracion exitosa con un codigo de 201
    status_code=status.HTTP_201_CREATED,
    #Define el limite de consultas
    dependencies=[Depends(rate_limit(
        limit=10,
        window=60,
        key_prefix="usuarios_crear",
        error_message="Demasiadas solicitudes de creación de usuarios. Espera 1 minuto."
    ))],
    summary="Crear nuevo usuario",
    description="Crea un nuevo usuario en el sistema. Solo administradores pueden crear usuarios."
)
def crear_usuario_endpoint(
    #Extrae la peticion HTTP y lo inyecta en la funcion
    request: Request,
    #Toma el body de UsuarioCreate de Schemas
    usuario: UsuarioCreate,
    #Inyeccion de la conexion de la base de datos, no crea la conexion, si no que lo inyecta
    db: Session = Depends(get_db),
    #Capa de seguridad con JWT y/o Roles.
    current_user: Usuario = Depends(require_role(["SUPER_ADMIN", "ADMIN"]))
):
    """
    Endpoint para crear un nuevo usuario.
    
    Ruta: POST /usuarios/crear
    
    Rate limit: 10 creaciones por minuto.
    Protección: Solo SUPER_ADMIN o ADMIN.
    """
    logger.info("=" * 60)
    logger.info(f"📋 ENDPOINT: POST /usuarios/crear")
    logger.info(f"👤 Creado por: ID={current_user.id}, Email={current_user.email}")
    logger.info(f"📧 Email del nuevo usuario: {usuario.email}")
    logger.info(f"👤 Nombre del nuevo usuario: {usuario.nombre}")
    logger.info("=" * 60)
    
    #Es un bloque de intento...
    try:
        #Llama a la funcion crear_usuario de services
        db_usuario = crear_usuario(db, usuario)
        logger.info(f"✅ Usuario creado exitosamente: ID={db_usuario.id}")
        return db_usuario
    except ValueError as e:
        logger.error(f"❌ Error al crear usuario: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# Actualizar campos en los usaurios
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
    description="Actualiza todos los datos de un usuario existente. Solo administradores."
)
def actualizar_usuario_endpoint(
    request: Request,
    usuario_id: int,
    usuario: UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["SUPER_ADMIN", "ADMIN"]))
):
    """
    Endpoint para actualizar un usuario existente.
    
    Ruta: PUT /usuarios/actualizar/{usuario_id}
    
    Rate limit: 20 actualizaciones por minuto.
    Protección: Solo SUPER_ADMIN o ADMIN.
    """
    logger.info("=" * 60)
    logger.info(f"📋 ENDPOINT: PUT /usuarios/actualizar/{usuario_id}")
    logger.info(f"👤 Actualizado por: ID={current_user.id}, Email={current_user.email}")
    logger.info(f"📝 Datos recibidos: {usuario.dict(exclude_unset=True)}")
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

#este endpoint borra permanentemente usuarios dentro de la base de datos
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
    description=(
        "⚠️ ELIMINACIÓN PERMANENTE: Borra el usuario de la base de datos de forma irreversible. "
        "Solo SUPER_ADMIN puede ejecutar esta acción. "
        "Para desactivar un usuario sin eliminarlo, usa PATCH /usuarios/desactivar/{usuario_id}."
    )
)
def eliminar_usuario_endpoint(
    request: Request,
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["SUPER_ADMIN"]))  # ← SOLO SUPER_ADMIN
):
    """
    Endpoint para eliminar PERMANENTEMENTE un usuario de la base de datos.
    
    Ruta: DELETE /usuarios/eliminar/{usuario_id}
    
    SEGURIDAD:
    - Solo SUPER_ADMIN puede ejecutar esta acción
    - No puede eliminarse a sí mismo
    - No puede eliminar al último SUPER_ADMIN del sistema
    - Elimina también todas las sesiones asociadas
    
    Rate limit: 5 eliminaciones por minuto (muy restrictivo).
    Protección: SOLO SUPER_ADMIN.
    """
    logger.info("=" * 60)
    logger.info(f"📋 ENDPOINT: DELETE /usuarios/eliminar/{usuario_id}")
    logger.info(f"💀 ACCIÓN: ELIMINACIÓN PERMANENTE (HARD DELETE)")
    logger.info(f"👤 Ejecutado por: ID={current_user.id}, Email={current_user.email}")
    logger.info(f"🎭 Rol del ejecutor: {current_user.rol.tipo.value if current_user.rol else 'Sin rol'}")
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
#Este endpoint activa usuarios desactivados mediante su id
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
    description="Activa un usuario que estaba desactivado. Solo administradores."
)
def activar_usuario_endpoint(
    request: Request,
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["SUPER_ADMIN", "ADMIN"]))
):
    """
    Endpoint para activar un usuario desactivado.
    
    Ruta: PATCH /usuarios/activar/{usuario_id}
    
    Rate limit: 10 solicitudes por minuto.
    Protección: Solo SUPER_ADMIN o ADMIN.
    """
    logger.info("=" * 60)
    logger.info(f"📋 ENDPOINT: PATCH /usuarios/activar/{usuario_id}")
    logger.info(f"👤 Solicitado por: ID={current_user.id}, Email={current_user.email}")
    logger.info("=" * 60)
    
    # Importar la función desde services
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

#Este endpoint desactiva usuarios activos dentro de la base de datos
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
    description="Desactiva un usuario sin eliminarlo permanentemente. Solo administradores."
)
def desactivar_usuario_endpoint(
    request: Request,
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["SUPER_ADMIN", "ADMIN"]))
):
    """
    Endpoint para desactivar un usuario.
    
    Ruta: PATCH /usuarios/desactivar/{usuario_id}
    
    Rate limit: 10 solicitudes por minuto.
    Protección: Solo SUPER_ADMIN o ADMIN.
    """
    logger.info("=" * 60)
    logger.info(f"📋 ENDPOINT: PATCH /usuarios/desactivar/{usuario_id}")
    logger.info(f"👤 Solicitado por: ID={current_user.id}, Email={current_user.email}")
    logger.info("=" * 60)
    
    # Importar la función desde services
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
# ENDPOINTS DE DEPARTAMENTOS (PROTEGIDOS CON JWT)
# ===========================================================

# Este endpoint muestra de modo lista los departamentos guardados en la base de datos
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
    description="Obtiene una lista de todos los departamentos del sistema. Requiere autenticación."
)
def listar_departamentos(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    activo: Optional[bool] = None
):
    """
    Endpoint para listar departamentos con paginación y filtros.
    
    Ruta: GET /usuarios/departamentos/listar
    
    Parámetros de filtro:
    - activo: true/false (opcional)
    
    Rate limit: 100 solicitudes por minuto (configuración por defecto).
    Protección: Requiere autenticación JWT.
    """
    logger.info("=" * 60)
    logger.info(f"📋 ENDPOINT: GET /usuarios/departamentos/listar")
    logger.info(f"👤 Usuario autenticado: ID={current_user.id}, Email={current_user.email}")
    logger.info(f"📊 Parámetros: skip={skip}, limit={limit}, activo={activo}")
    logger.info("=" * 60)
    
    from app.modules.usuarios.services import get_departamentos
    departamentos = get_departamentos(db, skip=skip, limit=limit, activo=activo)
    logger.info(f"✅ Retornando {len(departamentos)} departamentos")
    
    return DepartamentoListResponse(
        total=len(departamentos),
        departamentos=departamentos
    )


# Este endpoint busca un departamento específico por el ID en la base de datos
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
    description="Obtiene los detalles completos de un departamento específico por su ID. Requiere autenticación."
)
def obtener_departamento(
    request: Request,
    departamento_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Endpoint para obtener un departamento específico por ID.
    
    Ruta: GET /usuarios/departamentos/obtener/{departamento_id}
    
    Rate limit: 100 solicitudes por minuto.
    Protección: Requiere autenticación JWT.
    """
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


# Este endpoint crea departamentos
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
    description="Crea un nuevo departamento en el sistema. Solo administradores pueden crear departamentos."
)
def crear_departamento_endpoint(
    request: Request,
    departamento: DepartamentoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["SUPER_ADMIN", "ADMIN"]))
):
    """
    Endpoint para crear un nuevo departamento.
    
    Ruta: POST /usuarios/departamentos/crear
    
    Rate limit: 10 creaciones por minuto.
    Protección: Solo SUPER_ADMIN o ADMIN.
    """
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Actualizar campos en los departamentos
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
    description="Actualiza los datos de un departamento existente. Solo administradores."
)
def actualizar_departamento_endpoint(
    request: Request,
    departamento_id: int,
    departamento: DepartamentoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["SUPER_ADMIN", "ADMIN"]))
):
    """
    Endpoint para actualizar un departamento existente.
    
    Ruta: PUT /usuarios/departamentos/actualizar/{departamento_id}
    
    Rate limit: 20 actualizaciones por minuto.
    Protección: Solo SUPER_ADMIN o ADMIN.
    """
    logger.info("=" * 60)
    logger.info(f"📋 ENDPOINT: PUT /usuarios/departamentos/actualizar/{departamento_id}")
    logger.info(f"👤 Actualizado por: ID={current_user.id}, Email={current_user.email}")
    logger.info(f"📝 Datos recibidos: {departamento.dict(exclude_unset=True)}")
    logger.info("=" * 60)
    
    from app.modules.usuarios.services import actualizar_departamento
    try:
        db_departamento = actualizar_departamento(db, departamento_id, departamento)
        
        if not db_departamento:
            logger.error(f"❌ Departamento ID={departamento_id} NO encontrado")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Departamento con ID {departamento_id} no encontrado"
            )
        
        logger.info(f"✅ Departamento ID={departamento_id} actualizado exitosamente")
        return db_departamento
    except ValueError as e:
        logger.error(f"❌ Error al actualizar departamento: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ===========================================================
# ENDPOINTS DE ROLES (PROTEGIDOS CON JWT)
# ===========================================================

# Este endpoint muestra de modo lista los roles guardados en la base de datos
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
    description="Obtiene una lista de todos los roles del sistema. Requiere autenticación."
)
def listar_roles(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    activo: Optional[bool] = None
):
    """
    Endpoint para listar roles con paginación y filtros.
    
    Ruta: GET /usuarios/roles/listar
    
    Parámetros de filtro:
    - activo: true/false (opcional)
    
    Rate limit: 100 solicitudes por minuto (configuración por defecto).
    Protección: Requiere autenticación JWT.
    """
    logger.info("=" * 60)
    logger.info(f"📋 ENDPOINT: GET /usuarios/roles/listar")
    logger.info(f"👤 Usuario autenticado: ID={current_user.id}, Email={current_user.email}")
    logger.info(f"📊 Parámetros: skip={skip}, limit={limit}, activo={activo}")
    logger.info("=" * 60)
    
    from app.modules.usuarios.services import get_roles
    roles = get_roles(db, skip=skip, limit=limit, activo=activo)
    logger.info(f"✅ Retornando {len(roles)} roles")
    
    return RolListResponse(
        total=len(roles),
        roles=roles
    )


# Este endpoint busca un rol específico por el ID en la base de datos
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
    description="Obtiene los detalles completos de un rol específico por su ID. Requiere autenticación."
)
def obtener_rol(
    request: Request,
    rol_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Endpoint para obtener un rol específico por ID.
    
    Ruta: GET /usuarios/roles/obtener/{rol_id}
    
    Rate limit: 100 solicitudes por minuto.
    Protección: Requiere autenticación JWT.
    """
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


# Este endpoint crea roles
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
    description="Crea un nuevo rol en el sistema. Solo SUPER_ADMIN puede crear roles."
)
def crear_rol_endpoint(
    request: Request,
    rol: RolCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["SUPER_ADMIN"]))
):
    """
    Endpoint para crear un nuevo rol.
    
    Ruta: POST /usuarios/roles/crear
    
    Rate limit: 10 creaciones por minuto.
    Protección: Solo SUPER_ADMIN.
    """
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Actualizar campos en los roles
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
    description="Actualiza los datos de un rol existente. Solo SUPER_ADMIN."
)
def actualizar_rol_endpoint(
    request: Request,
    rol_id: int,
    rol: RolUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["SUPER_ADMIN"]))
):
    """
    Endpoint para actualizar un rol existente.
    
    Ruta: PUT /usuarios/roles/actualizar/{rol_id}
    
    Rate limit: 20 actualizaciones por minuto.
    Protección: Solo SUPER_ADMIN.
    """
    logger.info("=" * 60)
    logger.info(f"📋 ENDPOINT: PUT /usuarios/roles/actualizar/{rol_id}")
    logger.info(f"👤 Actualizado por: ID={current_user.id}, Email={current_user.email}")
    logger.info(f"📝 Datos recibidos: {rol.dict(exclude_unset=True)}")
    logger.info("=" * 60)
    
    from app.modules.usuarios.services import actualizar_rol
    try:
        db_rol = actualizar_rol(db, rol_id, rol)
        
        if not db_rol:
            logger.error(f"❌ Rol ID={rol_id} NO encontrado")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rol con ID {rol_id} no encontrado"
            )
        
        logger.info(f"✅ Rol ID={rol_id} actualizado exitosamente")
        return db_rol
    except ValueError as e:
        logger.error(f"❌ Error al actualizar rol: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )