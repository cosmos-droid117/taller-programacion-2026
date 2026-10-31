from typing import List

from domain.entities import Producto, ProductoBase
from domain.exceptions import ProductoDuplicado, ProductoNoEncontrado
from domain.ports import ProductoRepositoryPort


class ProductoService:
    """Casos de uso del catálogo. Recibe el repositorio por constructor (inyección de dependencias)."""

    def __init__(self, repositorio: ProductoRepositoryPort):
        self._repositorio = repositorio

    def listar(self) -> List[Producto]:
        return self._repositorio.listar()

    def obtener(self, id: int) -> Producto:
        producto = self._repositorio.obtener(id)
        if producto is None:
            raise ProductoNoEncontrado(id)
        return producto

    def crear(self, producto: Producto) -> Producto:
        if self._repositorio.existe(producto.id):
            raise ProductoDuplicado(producto.id)
        self._repositorio.guardar(producto)
        return producto

    def actualizar(self, id: int, datos: ProductoBase) -> Producto:
        if not self._repositorio.existe(id):
            raise ProductoNoEncontrado(id)
        actualizado = Producto(id=id, **datos.model_dump())
        self._repositorio.guardar(actualizado)
        return actualizado

    def eliminar(self, id: int) -> None:
        if not self._repositorio.existe(id):
            raise ProductoNoEncontrado(id)
        self._repositorio.eliminar(id)