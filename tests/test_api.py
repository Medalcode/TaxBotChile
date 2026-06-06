import sys
import os
import uuid
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import Base, engine

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
    client.post("/auth/registro", json={
        "nombre": "Test User",
        "email": random_email,
        "password": "test123456",
    })
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
    r = client.post("/auth/registro", json={
        "nombre": "Test User",
        "email": random_email,
        "password": "test123456",
    })
    assert r.status_code == 200
    assert r.json()["email"] == random_email

def test_login(client, registered_user):
    r = client.post("/auth/login", json={
        "email": registered_user["email"],
        "password": registered_user["password"],
    })
    assert r.status_code == 200
    assert "access_token" in r.json()

def test_calcular_boleta(client):
    r = client.post("/api/calcular/boleta?monto=500000")
    assert r.status_code == 200
    data = r.json()
    assert data["monto_bruto"] == 500000
    assert data["retencion"] == 68750
    assert data["liquido_a_recibir"] == 431250

def test_ingresos_crud(client, auth_headers):
    r = client.post("/api/ingresos", json={
        "monto_bruto": 1000000,
        "fecha_emision": "2026-04-15",
        "cliente": "Cliente Test",
        "descripcion": "Servicio de consultoría",
    }, headers=auth_headers)
    assert r.status_code == 200
    ingreso_id = r.json()["id"]

    r = client.get("/api/ingresos", headers=auth_headers)
    assert r.status_code == 200
    assert len(r.json()) > 0

    r = client.delete(f"/api/ingresos/{ingreso_id}", headers=auth_headers)
    assert r.status_code == 200

def test_proyeccion(client, auth_headers):
    r = client.get("/api/proyeccion", headers=auth_headers)
    assert r.status_code == 404

    client.post("/api/ingresos", json={
        "monto_bruto": 2000000,
        "fecha_emision": "2026-04-15",
    }, headers=auth_headers)

    r = client.get("/api/proyeccion", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert "proyeccion_anual" in data
    assert "global_complementario" in data

def test_recomendaciones(client, auth_headers):
    r = client.get("/api/recomendaciones", headers=auth_headers)
    assert r.status_code == 404

    client.post("/api/ingresos", json={
        "monto_bruto": 8000000,
        "fecha_emision": "2026-04-15",
    }, headers=auth_headers)

    r = client.get("/api/recomendaciones", headers=auth_headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)
