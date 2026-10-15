from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_listar_productos():
    r = client.get("/productos")
    assert r.status_code == 200