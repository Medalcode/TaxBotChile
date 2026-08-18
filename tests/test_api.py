import os
import sys
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import pytest
from app.main import app
from app.models import Base, engine
from app.services.auth import create_access_token
from fastapi.testclient import TestClient


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def random_email():
    return f"test_{uuid.uuid4().hex[:8]}@example.com"


@pytest.fixture
def registered_user(client, random_email):
    client.post(
        "/auth/registro",
        json={
            "nombre": "Test User",
            "email": random_email,
            "password": "test123456",
        },
    )
    return {"email": random_email, "password": "test123456"}


@pytest.fixture
def auth_token(client, registered_user):
    r = client.post("/auth/login", json=registered_user)
    return r.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_registro(client, random_email):
    r = client.post(
        "/auth/registro",
        json={
            "nombre": "Test User",
            "email": random_email,
            "password": "test123456",
        },
    )
    assert r.status_code == 200
    assert r.json()["email"] == random_email


def test_registro_duplicado(client, registered_user):
    r = client.post(
        "/auth/registro",
        json={
            "nombre": "Test User 2",
            "email": registered_user["email"],
            "password": "anotherpassword",
        },
    )
    assert r.status_code == 400
    assert r.json()["detail"] == "Email ya registrado"


def test_login(client, registered_user):
    r = client.post(
        "/auth/login",
        json={
            "email": registered_user["email"],
            "password": registered_user["password"],
        },
    )
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_login_credenciales_invalidas(client, registered_user):
    r = client.post(
        "/auth/login",
        json={
            "email": registered_user["email"],
            "password": "wrongpassword",
        },
    )
    assert r.status_code == 401
    assert r.json()["detail"] == "Credenciales inválidas"


def test_calcular_boleta(client):
    r = client.post("/api/calcular/boleta?monto=500000")
    assert r.status_code == 200
    data = r.json()
    assert data["monto_bruto"] == 500000
    assert data["retencion"] == 68750
    assert data["liquido_a_recibir"] == 431250


def test_ingresos_crud(client, auth_headers):
    r = client.post(
        "/api/ingresos",
        json={
            "monto_bruto": 1000000,
            "fecha_emision": "2026-04-15",
            "cliente": "Cliente Test",
            "descripcion": "Servicio de consultoría",
        },
        headers=auth_headers,
    )
    assert r.status_code == 200
    ingreso_id = r.json()["id"]

    r = client.get("/api/ingresos", headers=auth_headers)
    assert r.status_code == 200
    assert len(r.json()) > 0

    r = client.delete(f"/api/ingresos/{ingreso_id}", headers=auth_headers)
    assert r.status_code == 200


def test_ingreso_fecha_invalida(client, auth_headers):
    r = client.post(
        "/api/ingresos",
        json={
            "monto_bruto": 500000,
            "fecha_emision": "15/04/2026",
        },
        headers=auth_headers,
    )
    assert r.status_code == 400
    assert "Formato de fecha inválido" in r.json()["detail"]


def test_eliminar_ingreso_inexistente(client, auth_headers):
    r = client.delete("/api/ingresos/999999", headers=auth_headers)
    assert r.status_code == 404
    assert r.json()["detail"] == "Ingreso no encontrado"


def test_proyeccion(client, auth_headers):
    r = client.get("/api/proyeccion", headers=auth_headers)
    assert r.status_code == 404

    client.post(
        "/api/ingresos",
        json={
            "monto_bruto": 2000000,
            "fecha_emision": "2026-04-15",
        },
        headers=auth_headers,
    )

    r = client.get("/api/proyeccion", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert "proyeccion_anual" in data
    assert "global_complementario" in data


def test_recomendaciones(client, auth_headers):
    r = client.get("/api/recomendaciones", headers=auth_headers)
    assert r.status_code == 404

    client.post(
        "/api/ingresos",
        json={
            "monto_bruto": 8000000,
            "fecha_emision": "2026-04-15",
        },
        headers=auth_headers,
    )

    r = client.get("/api/recomendaciones", headers=auth_headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_auth_token_invalido(client):
    r = client.get(
        "/api/ingresos",
        headers={"Authorization": "Bearer token_totalmente_invalido"},
    )
    assert r.status_code == 401
    assert r.json()["detail"] == "Token inválido"


def test_usuario_no_encontrado_token(client):
    token_fantasma = create_access_token({"sub": "999999", "email": "fantasma@example.com"})
    r = client.get(
        "/api/ingresos",
        headers={"Authorization": f"Bearer {token_fantasma}"},
    )
    assert r.status_code == 401
    assert r.json()["detail"] == "Usuario no encontrado"


def test_aislamiento_multiusuario(client):
    # Crear Usuario A
    email_a = f"usua_{uuid.uuid4().hex[:6]}@example.com"
    client.post(
        "/auth/registro",
        json={"nombre": "User A", "email": email_a, "password": "pass123456"},
    )
    res_a = client.post(
        "/auth/login",
        json={"email": email_a, "password": "pass123456"},
    )
    token_a = res_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Crear Usuario B
    email_b = f"usub_{uuid.uuid4().hex[:6]}@example.com"
    client.post(
        "/auth/registro",
        json={"nombre": "User B", "email": email_b, "password": "pass123456"},
    )
    res_b = client.post(
        "/auth/login",
        json={"email": email_b, "password": "pass123456"},
    )
    token_b = res_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}


    # Usuario A registra un ingreso
    r_ing = client.post(
        "/api/ingresos",
        json={"monto_bruto": 1500000, "fecha_emision": "2026-05-10"},
        headers=headers_a,
    )
    ing_id_a = r_ing.json()["id"]

    # Usuario B intenta ver los ingresos (no debe ver el de A)
    ingresos_b = client.get("/api/ingresos", headers=headers_b).json()
    assert not any(i["id"] == ing_id_a for i in ingresos_b)

    # Usuario B intenta eliminar el ingreso de A (debe recibir 404 Not Found)
    del_res = client.delete(f"/api/ingresos/{ing_id_a}", headers=headers_b)
    assert del_res.status_code == 404
