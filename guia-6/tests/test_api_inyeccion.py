from fastapi.testclient import TestClient

from api.dependencies import get_producto_service
from application.producto_service import ProductoService
from domain.entities import Producto
from infrastructure.memory_producto_repository import MemoriaProductoRepository
from main import app


def _cliente_con_repositorio_propio():
    repo = MemoriaProductoRepository(
        {7: Producto(id=7, nombre="Cable", categoria="Accesorios", precio=5000, stock=3)}
    )
    app.dependency_overrides[get_producto_service] = lambda: ProductoService(repo)
    return TestClient(app)


def test_la_api_usa_el_servicio_que_se_le_inyecta():
    try:
        cliente = _cliente_con_repositorio_propio()
        assert [p["id"] for p in cliente.get("/productos").json()] == [7]
    finally:
        app.dependency_overrides.clear()


def test_las_excepciones_del_dominio_se_traducen_a_http():
    try:
        cliente = _cliente_con_repositorio_propio()
        r = cliente.get("/productos/999")
        assert r.status_code == 404
        assert r.json() == {"detail": "No product with id 999 exists"}
        dup = {"id": 7, "nombre": "X", "categoria": "Y", "precio": 10, "stock": 1}
        r = cliente.post("/productos", json=dup)
        assert r.status_code == 400
        assert r.json() == {"detail": "A product with id 7 already exists"}
    finally:
        app.dependency_overrides.clear()