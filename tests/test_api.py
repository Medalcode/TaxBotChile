import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
_test_email = None


def _registro(email_suffix: str = "test"):
    global _test_email
    _test_email = f"{email_suffix}@example.com"
    return client.post("/auth/registro", json={
        "nombre": "Test User",
        "email": _test_email,
        "password": "test123456",
    })


def _login():
    r = client.post("/auth/login", json={
        "email": _test_email,
        "password": "test123456",
    })
    assert r.status_code == 200
    return r.json()["access_token"]


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_registro():
    r = _registro("reg")
    assert r.status_code == 200
    assert r.json()["email"] == _test_email


def test_login():
    _registro("log")
    r = client.post("/auth/login", json={
        "email": _test_email,
        "password": "test123456",
    })
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_calcular_boleta():
    r = client.post("/api/calcular/boleta?monto=500000")
    assert r.status_code == 200
    data = r.json()
    assert data["monto_bruto"] == 500000
    assert data["retencion"] == 68750
    assert data["liquido_a_recibir"] == 431250


def test_ingresos_crud():
    _registro("crud")
    token = _login()
    headers = {"Authorization": f"Bearer {token}"}

    r = client.post("/api/ingresos", json={
        "monto_bruto": 1000000,
        "fecha_emision": "2026-04-15",
        "cliente": "Cliente Test",
        "descripcion": "Servicio de consultoría",
    }, headers=headers)
    assert r.status_code == 200
    ingreso_id = r.json()["id"]

    r = client.get("/api/ingresos", headers=headers)
    assert r.status_code == 200
    assert len(r.json()) > 0

    r = client.delete(f"/api/ingresos/{ingreso_id}", headers=headers)
    assert r.status_code == 200


def test_proyeccion():
    _registro("proy")
    token = _login()
    headers = {"Authorization": f"Bearer {token}"}

    r = client.get("/api/proyeccion", headers=headers)
    assert r.status_code == 404

    client.post("/api/ingresos", json={
        "monto_bruto": 2000000,
        "fecha_emision": "2026-04-15",
    }, headers=headers)

    r = client.get("/api/proyeccion", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert "proyeccion_anual" in data
    assert "global_complementario" in data


def test_recomendaciones():
    _registro("rec")
    token = _login()
    headers = {"Authorization": f"Bearer {token}"}

    r = client.get("/api/recomendaciones", headers=headers)
    assert r.status_code == 404

    client.post("/api/ingresos", json={
        "monto_bruto": 8000000,
        "fecha_emision": "2026-04-15",
    }, headers=headers)

    r = client.get("/api/recomendaciones", headers=headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)
