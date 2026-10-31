from unittest.mock import Mock

import pytest

from application.producto_service import ProductoService
from domain.entities import Producto, ProductoBase
from domain.exceptions import ProductoDuplicado, ProductoNoEncontrado
from domain.ports import ProductoRepositoryPort
from infrastructure.memory_producto_repository import MemoriaProductoRepository

LAPTOP = Producto(id=1, nombre="Laptop", categoria="Tecnología", precio=2500000, stock=10)


def _repo_falso():
    """Repositorio simulado con la misma interfaz que el puerto (equivale a un mock de Mockito)."""
    return Mock(spec=ProductoRepositoryPort)


def test_listar_delega_en_el_repositorio():
    repo = _repo_falso()
    repo.listar.return_value = [LAPTOP]
    assert ProductoService(repo).listar() == [LAPTOP]
    repo.listar.assert_called_once()


def test_obtener_existente():
    repo = _repo_falso()
    repo.obtener.return_value = LAPTOP
    assert ProductoService(repo).obtener(1) == LAPTOP


def test_obtener_inexistente_lanza_no_encontrado():
    repo = _repo_falso()
    repo.obtener.return_value = None
    with pytest.raises(ProductoNoEncontrado):
        ProductoService(repo).obtener(999)


def test_obtener_no_oculta_fallos_de_infraestructura():
    repo = _repo_falso()
    repo.obtener.side_effect = RuntimeError("base de datos caida")
    with pytest.raises(RuntimeError):
        ProductoService(repo).obtener(500)


def test_crear_guarda_y_devuelve_el_producto():
    repo = _repo_falso()
    repo.existe.return_value = False
    assert ProductoService(repo).crear(LAPTOP) == LAPTOP
    repo.guardar.assert_called_once_with(LAPTOP)


def test_crear_duplicado_lanza_error_y_no_guarda():
    repo = _repo_falso()
    repo.existe.return_value = True
    with pytest.raises(ProductoDuplicado):
        ProductoService(repo).crear(LAPTOP)
    repo.guardar.assert_not_called()


def test_actualizar_conserva_el_id_recibido():
    repo = _repo_falso()
    repo.existe.return_value = True
    datos = ProductoBase(nombre="Laptop", categoria="Tecnología", precio=2300000, stock=7)
    resultado = ProductoService(repo).actualizar(1, datos)
    assert resultado.id == 1 and resultado.precio == 2300000
    repo.guardar.assert_called_once_with(resultado)


def test_actualizar_inexistente_lanza_no_encontrado():
    repo = _repo_falso()
    repo.existe.return_value = False
    datos = ProductoBase(nombre="X", categoria="Y", precio=1, stock=0)
    with pytest.raises(ProductoNoEncontrado):
        ProductoService(repo).actualizar(999, datos)
    repo.guardar.assert_not_called()


def test_eliminar_existente():
    repo = _repo_falso()
    repo.existe.return_value = True
    ProductoService(repo).eliminar(1)
    repo.eliminar.assert_called_once_with(1)


def test_eliminar_inexistente_no_borra_nada():
    repo = _repo_falso()
    repo.existe.return_value = False
    with pytest.raises(ProductoNoEncontrado):
        ProductoService(repo).eliminar(999)
    repo.eliminar.assert_not_called()


def test_servicio_con_el_repositorio_real_en_memoria():
    servicio = ProductoService(MemoriaProductoRepository())
    servicio.crear(LAPTOP)
    with pytest.raises(ProductoDuplicado):
        servicio.crear(LAPTOP)
    servicio.eliminar(1)
    assert servicio.listar() == []