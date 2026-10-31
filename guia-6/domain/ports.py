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


class DatosAbiertosPort(ABC):
    """Contrato para obtener registros de una fuente externa de datos abiertos."""

    @abstractmethod
    def obtener_registros(self, limite: Optional[int] = None) -> List[Dict[str, Any]]: ...

class AnaliticaPort(ABC):
    """Contrato para calcular estadísticas descriptivas sobre registros de una fuente."""

    @abstractmethod
    def estadisticas(self, registros: List[Dict[str, Any]], columna: str) -> Dict[str, Any]: ...

    @abstractmethod
    def por_grupo(self, registros: List[Dict[str, Any]], columna_grupo: str,
                  columna_numerica: Optional[str] = None) -> List[Dict[str, Any]]: ...