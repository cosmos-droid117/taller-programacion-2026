from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from domain.entities import Producto


class ProductoRepositoryPort(ABC):
    """Contrato que la aplicación necesita para guardar y leer productos."""

    @abstractmethod
    def listar(self) -> List[Producto]: ...

    @abstractmethod
    def obtener(self, id: int) -> Optional[Producto]: ...

    @abstractmethod
    def existe(self, id: int) -> bool: ...

    @abstractmethod
    def guardar(self, producto: Producto) -> None: ...

    @abstractmethod
    def eliminar(self, id: int) -> None: ...


class LLMPort(ABC):
    """Contrato para consultar un modelo de lenguaje."""

    @abstractmethod
    def generar(self, prompt: str) -> Dict[str, Any]: ...


class LlamadaLogPort(ABC):
    """Contrato para dejar registro de cada llamada al LLM."""

    @abstractmethod
    def registrar(self, registro: Dict[str, Any]) -> None: ...