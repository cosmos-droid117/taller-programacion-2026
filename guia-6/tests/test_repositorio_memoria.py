import pytest

from domain.entities import Producto
from domain.ports import ProductoRepositoryPort
from infrastructure.memory_producto_repository import MemoriaProductoRepository


def _laptop():
    return Producto(id=1, nombre="Laptop", categoria="Tecnología", precio=2500000, stock=10)


def test_es_un_adaptador_del_puerto():
    assert isinstance(MemoriaProductoRepository(), ProductoRepositoryPort)


def test_guardar_obtener_y_listar():
    repo = MemoriaProductoRepository()
    repo.guardar(_laptop())
    assert repo.obtener(1) == _laptop()
    assert repo.listar() == [_laptop()]


def test_obtener_inexistente_devuelve_none():
    assert MemoriaProductoRepository().obtener(999) is None


def test_existe_y_eliminar():
    repo = MemoriaProductoRepository({1: _laptop()})
    assert repo.existe(1) is True
    repo.eliminar(1)
    assert repo.existe(1) is False
    repo.eliminar(1)  # eliminar algo que no existe no falla


def test_fallo_simulado_solo_afecta_a_obtener():
    repo = MemoriaProductoRepository()
    with pytest.raises(RuntimeError):
        repo.obtener(500)
    assert repo.existe(500) is False