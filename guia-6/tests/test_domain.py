import pytest
from pydantic import ValidationError

from domain.entities import Producto
from domain.exceptions import ProductoDuplicado, ProductoNoEncontrado
from domain.ports import ProductoRepositoryPort


def test_producto_rechaza_precio_no_positivo():
    with pytest.raises(ValidationError):
        Producto(id=1, nombre="X", categoria="Y", precio=0, stock=1)


def test_producto_rechaza_stock_negativo():
    with pytest.raises(ValidationError):
        Producto(id=1, nombre="X", categoria="Y", precio=10, stock=-1)


def test_excepciones_conservan_el_mensaje_de_la_api():
    assert str(ProductoNoEncontrado(999)) == "No product with id 999 exists"
    assert str(ProductoDuplicado(1)) == "A product with id 1 already exists"


def test_los_puertos_son_abstractos():
    with pytest.raises(TypeError):
        ProductoRepositoryPort()