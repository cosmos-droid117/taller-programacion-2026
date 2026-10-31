import copy

import pytest
from fastapi.testclient import TestClient

from database import productos_db
from main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def restaurar_db():
    """Deja la 'base de datos' en memoria como estaba antes de cada prueba."""
    copia = copy.deepcopy(productos_db)
    yield
    productos_db.clear()
    productos_db.update(copia)


def test_ciclo_crud_completo():
    nuevo = {"id": 10, "nombre": "Teclado", "categoria": "Tecnología", "precio": 90000, "stock": 15}

    # Create
    r = client.post("/productos", json=nuevo)
    assert r.status_code == 201
    assert r.json()["id"] == 10

    # Read (uno y lista)
    r = client.get("/productos/10")
    assert r.status_code == 200
    assert r.json()["nombre"] == "Teclado"
    ids = [p["id"] for p in client.get("/productos").json()]
    assert 10 in ids

    # Update
    cambios = {"nombre": "Teclado mecánico", "categoria": "Tecnología", "precio": 120000, "stock": 8}
    r = client.put("/productos/10", json=cambios)
    assert r.status_code == 200
    assert r.json()["precio"] == 120000

    # Delete
    assert client.delete("/productos/10").status_code == 204
    assert client.get("/productos/10").status_code == 404


def test_manejo_de_errores_http():
    # 404: producto inexistente
    assert client.get("/productos/999").status_code == 404

    # 422: datos inválidos (precio negativo)
    malo = {"id": 11, "nombre": "X", "categoria": "Y", "precio": -5, "stock": 1}
    assert client.post("/productos", json=malo).status_code == 422

    # 400: id duplicado (el id 1 ya existe en el seed)
    dup = {"id": 1, "nombre": "X", "categoria": "Y", "precio": 10, "stock": 1}
    assert client.post("/productos", json=dup).status_code == 400

    # 500: fallo simulado de base de datos (id 500)
    cliente_500 = TestClient(app, raise_server_exceptions=False)
    assert cliente_500.get("/productos/500").status_code == 500