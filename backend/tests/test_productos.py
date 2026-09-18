# backend/tests/test_productos.py
#
# Pruebas del modulo de productos: categorias y productos (con precio integrado).
# Ejecutar con:
#   set APP_ENV=test && pytest tests/test_productos.py -v

import uuid
import pytest
from app.modules.usuarios.models import Usuario, Rol, TipoRol, EstadoUsuario
from app.modules.auth.services import get_password_hash
from app.modules.productos.modelsproducto import Producto, Categoria


def _sufijo_unico():
    """Genera un sufijo unico para evitar colisiones con datos ya existentes
    en la base de pruebas (restaurada desde produccion)."""
    return uuid.uuid4().hex[:8]


def _producto_payload(vendible_granel=False, qty_contenido=None, categoria_id=None):
    """Genera un payload valido de creacion de producto, con codigo y nombre
    unicos en cada llamada."""
    sufijo = _sufijo_unico()
    payload = {
        "codigo": f"COD-{sufijo}",
        "nombre": f"Producto Test {sufijo}",
        "descripcion": "Producto creado en pruebas automatizadas",
        "marca": "MarcaTest",
        "tipo": "BIEN",
        "vendible_granel": vendible_granel,
        "precio": {
            "precio_base": "10.00",
            "precio_costo": "5.00",
            "precio_publico": "12.00",
            "precio_iva": "13.56"
        }
    }
    if qty_contenido is not None:
        payload["qty_contenido"] = qty_contenido
    if categoria_id is not None:
        payload["categoria_id"] = categoria_id
    return payload


# ============================================================================
# FIXTURES LOCALES: usuarios con roles reales para probar permisos
# ============================================================================

@pytest.fixture
def rol_admin(db_session):
    """Obtiene el rol con tipo ADMIN si ya existe en la base (por el backup
    restaurado), o lo crea si no existe."""
    rol = db_session.query(Rol).filter(Rol.tipo == TipoRol.ADMIN).first()
    if rol:
        return rol

    rol = Rol(nombre="Administrador QA", tipo=TipoRol.ADMIN, activo=True)
    db_session.add(rol)
    db_session.commit()
    db_session.refresh(rol)
    return rol


@pytest.fixture
def rol_vendedor(db_session):
    """Obtiene o crea un rol SIN privilegios de administrador, para probar
    que los endpoints protegidos rechazan correctamente a este tipo de usuario."""
    rol = db_session.query(Rol).filter(Rol.tipo == TipoRol.VENDEDOR).first()
    if rol:
        return rol

    rol = Rol(nombre="Vendedor QA", tipo=TipoRol.VENDEDOR, activo=True)
    db_session.add(rol)
    db_session.commit()
    db_session.refresh(rol)
    return rol


@pytest.fixture
def usuario_admin(db_session, rol_admin):
    """Usuario de prueba con rol ADMIN, para probar endpoints protegidos."""
    email_test = "admin_qa@example.com"

    existente = db_session.query(Usuario).filter(Usuario.email == email_test).first()
    if existente:
        return existente

    usuario = Usuario(
        nombre="Admin QA",
        email=email_test,
        password_hash=get_password_hash("password123"),
        telefono="2222-5555",
        departamento_id=1,
        rol_id=rol_admin.id,
        estado=EstadoUsuario.ACTIVO
    )
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)
    return usuario


@pytest.fixture
def usuario_vendedor(db_session, rol_vendedor):
    """Usuario de prueba SIN rol de administrador, para probar rechazo de permisos."""
    email_test = "vendedor_qa@example.com"

    existente = db_session.query(Usuario).filter(Usuario.email == email_test).first()
    if existente:
        return existente

    usuario = Usuario(
        nombre="Vendedor QA",
        email=email_test,
        password_hash=get_password_hash("password123"),
        telefono="2222-6666",
        departamento_id=1,
        rol_id=rol_vendedor.id,
        estado=EstadoUsuario.ACTIVO
    )
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)
    return usuario


@pytest.fixture
def headers_admin(client, usuario_admin):
    """Header Authorization listo para usar, autenticado como ADMIN."""
    response = client.post("/auth/iniciar-sesion", json={
        "email": "admin_qa@example.com",
        "password": "password123"
    })
    assert response.status_code == 200, f"Login admin fallo: {response.json()}"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def headers_vendedor(client, usuario_vendedor):
    """Header Authorization listo para usar, autenticado como VENDEDOR (sin permisos de admin)."""
    response = client.post("/auth/iniciar-sesion", json={
        "email": "vendedor_qa@example.com",
        "password": "password123"
    })
    assert response.status_code == 200, f"Login vendedor fallo: {response.json()}"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ============================================================================
# TESTS: CATEGORIAS
# ============================================================================

def test_crear_categoria_como_admin(client, headers_admin):
    """Un ADMIN debe poder crear una categoria nueva."""
    nombre_unico = f"Categoria Test {_sufijo_unico()}"
    response = client.post(
        "/productos/categorias/crear",
        json={"nombre": nombre_unico},
        headers=headers_admin
    )

    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == nombre_unico


def test_crear_categoria_duplicada(client, headers_admin):
    """No debe permitirse crear dos categorias con el mismo nombre."""
    nombre_unico = f"Categoria Duplicada {_sufijo_unico()}"

    primera = client.post(
        "/productos/categorias/crear",
        json={"nombre": nombre_unico},
        headers=headers_admin
    )
    assert primera.status_code == 201

    segunda = client.post(
        "/productos/categorias/crear",
        json={"nombre": nombre_unico},
        headers=headers_admin
    )
    assert segunda.status_code == 400
    assert "ya existe" in segunda.json()["detail"].lower()


def test_crear_categoria_sin_permiso(client, headers_vendedor):
    """Un usuario sin rol de administrador no debe poder crear categorias."""
    response = client.post(
        "/productos/categorias/crear",
        json={"nombre": f"Categoria Rechazada {_sufijo_unico()}"},
        headers=headers_vendedor
    )

    assert response.status_code == 403


def test_listar_categorias_usuario_normal(client, headers_vendedor):
    """Cualquier usuario autenticado (sin importar su rol) debe poder listar categorias."""
    response = client.get("/productos/categorias/listar", headers=headers_vendedor)

    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "categorias" in data


# ============================================================================
# TESTS: PRODUCTOS - CREACION
# ============================================================================

def test_crear_producto_exitoso(client, headers_admin):
    """Un ADMIN debe poder crear un producto junto con su precio."""
    payload = _producto_payload()

    response = client.post("/productos/crear", json=payload, headers=headers_admin)

    assert response.status_code == 201
    data = response.json()
    assert data["codigo"] == payload["codigo"]
    assert data["nombre"] == payload["nombre"]
    assert data["activo"] is True
    assert data["precio"] is not None
    assert float(data["precio"]["precio_publico"]) == 12.00


def test_crear_producto_codigo_duplicado(client, headers_admin):
    """No debe permitirse crear dos productos con el mismo codigo."""
    payload = _producto_payload()

    primero = client.post("/productos/crear", json=payload, headers=headers_admin)
    assert primero.status_code == 201

    # Mismo codigo, nombre distinto
    payload_duplicado = _producto_payload()
    payload_duplicado["codigo"] = payload["codigo"]

    segundo = client.post("/productos/crear", json=payload_duplicado, headers=headers_admin)
    assert segundo.status_code == 400
    assert "código" in segundo.json()["detail"].lower() or "codigo" in segundo.json()["detail"].lower()


def test_crear_producto_nombre_duplicado(client, headers_admin):
    """No debe permitirse crear dos productos con el mismo nombre."""
    payload = _producto_payload()

    primero = client.post("/productos/crear", json=payload, headers=headers_admin)
    assert primero.status_code == 201

    # Nombre igual, codigo distinto
    payload_duplicado = _producto_payload()
    payload_duplicado["nombre"] = payload["nombre"]

    segundo = client.post("/productos/crear", json=payload_duplicado, headers=headers_admin)
    assert segundo.status_code == 400
    assert "nombre" in segundo.json()["detail"].lower()


def test_crear_producto_granel_sin_qty_contenido_falla(client, headers_admin):
    """Si vendible_granel=True pero no se envia qty_contenido (o es 0),
    debe rechazarse por la regla de negocio del servicio."""
    payload = _producto_payload(vendible_granel=True, qty_contenido=None)

    response = client.post("/productos/crear", json=payload, headers=headers_admin)

    assert response.status_code == 400
    assert "qty_contenido" in response.json()["detail"]


def test_crear_producto_granel_con_qty_contenido_exitoso(client, headers_admin):
    """Si vendible_granel=True y qty_contenido > 0, el producto debe crearse sin problema."""
    payload = _producto_payload(vendible_granel=True, qty_contenido=100)

    response = client.post("/productos/crear", json=payload, headers=headers_admin)

    assert response.status_code == 201
    data = response.json()
    assert data["vendible_granel"] is True
    assert data["qty_contenido"] == 100


def test_crear_producto_sin_permiso(client, headers_vendedor):
    """Un usuario sin rol de administrador no debe poder crear productos."""
    payload = _producto_payload()

    response = client.post("/productos/crear", json=payload, headers=headers_vendedor)

    assert response.status_code == 403


# ============================================================================
# TESTS: PRODUCTOS - LECTURA, ACTUALIZACION Y ELIMINACION
# ============================================================================

def test_obtener_producto_por_id(client, headers_admin):
    """Debe poder consultarse un producto recien creado por su ID, con su precio."""
    payload = _producto_payload()
    creado = client.post("/productos/crear", json=payload, headers=headers_admin)
    producto_id = creado.json()["id"]

    response = client.get(f"/productos/obtener/{producto_id}", headers=headers_admin)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == producto_id
    assert data["codigo"] == payload["codigo"]


def test_actualizar_producto_actualiza_precio(client, headers_admin):
    """Actualizar un producto enviando un nuevo precio_publico debe reflejarse
    tanto en la cabecera del producto como en su precio asociado."""
    payload = _producto_payload()
    creado = client.post("/productos/crear", json=payload, headers=headers_admin)
    producto_id = creado.json()["id"]

    response = client.put(
        f"/productos/actualizar/{producto_id}",
        json={
            "nombre": f"{payload['nombre']} (editado)",
            "precio": {"precio_publico": "20.00"}
        },
        headers=headers_admin
    )

    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == f"{payload['nombre']} (editado)"
    assert float(data["precio"]["precio_publico"]) == 20.00


def test_eliminar_producto_soft_delete(client, headers_admin, db_session):
    """Eliminar un producto debe marcarlo como activo=False (soft delete),
    no borrarlo fisicamente de la base de datos."""
    payload = _producto_payload()
    creado = client.post("/productos/crear", json=payload, headers=headers_admin)
    producto_id = creado.json()["id"]

    response = client.delete(f"/productos/eliminar/{producto_id}", headers=headers_admin)

    assert response.status_code == 200

    # Verificar directamente en la base de datos
    producto_db = db_session.query(Producto).filter(Producto.id == producto_id).first()
    assert producto_db is not None
    assert producto_db.activo is False

    # Verificar que el producto sigue siendo consultable (no fue borrado fisicamente)
    consulta = client.get(f"/productos/obtener/{producto_id}", headers=headers_admin)
    assert consulta.status_code == 200
    assert consulta.json()["activo"] is False


def test_eliminar_producto_ya_desactivado(client, headers_admin):
    """Eliminar un producto que ya esta desactivado no debe fallar, solo
    informar que ya estaba desactivado."""
    payload = _producto_payload()
    creado = client.post("/productos/crear", json=payload, headers=headers_admin)
    producto_id = creado.json()["id"]

    primera = client.delete(f"/productos/eliminar/{producto_id}", headers=headers_admin)
    assert primera.status_code == 200

    segunda = client.delete(f"/productos/eliminar/{producto_id}", headers=headers_admin)
    assert segunda.status_code == 200
    assert "ya está desactivado" in segunda.json()["message"].lower() or "ya esta desactivado" in segunda.json()["message"].lower()


def test_obtener_producto_inexistente(client, headers_admin):
    """Consultar un producto con un ID que no existe debe retornar 404."""
    response = client.get("/productos/obtener/999999999", headers=headers_admin)

    assert response.status_code == 404