from typing import Dict, List, Optional

from domain.entities import Producto
from domain.ports import ProductoRepositoryPort

ID_FALLO_SIMULADO = 500


class MemoriaProductoRepository(ProductoRepositoryPort):
    """Adaptador del puerto ProductoRepositoryPort que guarda los productos en un diccionario."""

    def __init__(self, productos: Optional[Dict[int, Producto]] = None):
        self._productos: Dict[int, Producto] = productos if productos is not None else {}

    def listar(self) -> List[Producto]:
        return list(self._productos.values())

    def obtener(self, id: int) -> Optional[Producto]:
        if id == ID_FALLO_SIMULADO:
            raise RuntimeError("Error simulado: no fue posible conectar con la base de datos")
        return self._productos.get(id)

    def existe(self, id: int) -> bool:
        return id in self._productos

    def guardar(self, producto: Producto) -> None:
        self._productos[producto.id] = producto

    def eliminar(self, id: int) -> None:
        self._productos.pop(id, None)