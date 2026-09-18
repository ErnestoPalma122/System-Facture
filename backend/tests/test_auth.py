# backend/tests/test_auth.py
#
# Pruebas del modulo de autenticacion (login, logout, refresh token).
# Usa los fixtures definidos en conftest.py: client, db_session, usuario_test.
#
# Ejecutar con:
#   set APP_ENV=test && pytest tests/test_auth.py -v

import pytest
from app.modules.usuarios.models import Usuario, EstadoUsuario, Sesion, EstadoSesion
from app.modules.auth.services import get_password_hash


# ============================================================================
# FIXTURES LOCALES (usuarios con estados especiales, solo para este archivo)
# ============================================================================

@pytest.fixture
def usuario_inactivo(db_session):
    """Crea un usuario en estado INACTIVO para probar el rechazo de login."""
    email_test = "inactivo@example.com"

    existente = db_session.query(Usuario).filter(Usuario.email == email_test).first()
    if existente:
        return existente

    usuario = Usuario(
        nombre="Usuario Inactivo QA",
        email=email_test,
        password_hash=get_password_hash("password123"),
        telefono="2222-3333",
        departamento_id=1,
        rol_id=1,
        estado=EstadoUsuario.INACTIVO
    )
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)
    return usuario


@pytest.fixture
def usuario_bloqueado(db_session):
    """Crea un usuario en estado BLOQUEADO para probar el rechazo de login."""
    email_test = "bloqueado@example.com"

    existente = db_session.query(Usuario).filter(Usuario.email == email_test).first()
    if existente:
        return existente

    usuario = Usuario(
        nombre="Usuario Bloqueado QA",
        email=email_test,
        password_hash=get_password_hash("password123"),
        telefono="2222-4444",
        departamento_id=1,
        rol_id=1,
        estado=EstadoUsuario.BLOQUEADO
    )
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)
    return usuario


# ============================================================================
# TESTS: LOGIN
# ============================================================================

def test_login_exitoso(client, usuario_test):
    """Un usuario activo con credenciales correctas debe recibir tokens y sus datos."""
    response = client.post("/auth/iniciar-sesion", json={
        "email": "test@example.com",
        "password": "password123"
    })

    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["usuario"]["email"] == "test@example.com"
    assert data["usuario"]["id"] == usuario_test.id

    # La cookie HttpOnly tambien debe quedar establecida
    assert "access_token" in response.cookies


def test_login_password_incorrecta(client, usuario_test):
    """Password incorrecta debe rechazarse con 401 y mensaje generico."""
    response = client.post("/auth/iniciar-sesion", json={
        "email": "test@example.com",
        "password": "password_incorrecta"
    })

    assert response.status_code == 401
    assert "Credenciales inv" in response.json()["detail"]


def test_login_email_no_existe(client):
    """Un email que no existe en la base debe dar el mismo mensaje generico
    que una password incorrecta, para no revelar si el correo esta registrado."""
    response = client.post("/auth/iniciar-sesion", json={
        "email": "no_existe@example.com",
        "password": "password123"
    })

    assert response.status_code == 401
    assert "Credenciales inv" in response.json()["detail"]


def test_login_usuario_inactivo(client, usuario_inactivo):
    """Un usuario INACTIVO no debe poder iniciar sesion, aunque la password sea correcta."""
    response = client.post("/auth/iniciar-sesion", json={
        "email": "inactivo@example.com",
        "password": "password123"
    })

    assert response.status_code == 401
    assert "desactivado" in response.json()["detail"].lower()


def test_login_usuario_bloqueado(client, usuario_bloqueado):
    """Un usuario BLOQUEADO no debe poder iniciar sesion."""
    response = client.post("/auth/iniciar-sesion", json={
        "email": "bloqueado@example.com",
        "password": "password123"
    })

    assert response.status_code == 401
    assert "bloqueada" in response.json()["detail"].lower()


# ============================================================================
# TESTS: LOGOUT
# ============================================================================

def test_logout_con_token_valido(client, usuario_test, db_session):
    """Logout con un access_token valido debe cerrar la sesion en la base de datos."""
    login_response = client.post("/auth/iniciar-sesion", json={
        "email": "test@example.com",
        "password": "password123"
    })
    access_token = login_response.json()["access_token"]

    response = client.post(
        "/auth/cerrar-sesion",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200

    # Verificar en la base de datos que la sesion quedo marcada como CERRADA
    sesion = db_session.query(Sesion).filter(Sesion.token == access_token).first()
    assert sesion is not None
    assert sesion.estado == EstadoSesion.CERRADA
    assert sesion.activo is False


def test_logout_sin_authorization_header(client):
    """Logout sin header Authorization debe rechazarse con 401."""
    response = client.post("/auth/cerrar-sesion")

    assert response.status_code == 401


# ============================================================================
# TESTS: REFRESH TOKEN
# ============================================================================

def test_refrescar_token_valido(client, usuario_test):
    """Un refresh_token valido debe generar un nuevo access_token."""
    login_response = client.post("/auth/iniciar-sesion", json={
        "email": "test@example.com",
        "password": "password123"
    })
    refresh_token = login_response.json()["refresh_token"]

    response = client.post(
        "/auth/refrescar-token",
        headers={"Authorization": f"Bearer {refresh_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_refrescar_token_con_access_token(client, usuario_test):
    """Si se envia un access_token (no un refresh_token) al endpoint de refresh,
    debe rechazarse, porque el payload no tiene type='refresh'."""
    login_response = client.post("/auth/iniciar-sesion", json={
        "email": "test@example.com",
        "password": "password123"
    })
    access_token = login_response.json()["access_token"]

    response = client.post(
        "/auth/refrescar-token",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 401
    assert "refresh" in response.json()["detail"].lower()