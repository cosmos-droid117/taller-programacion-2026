from observability.logging_config import logger
class DominioError(Exception):
    """Base de los errores de negocio. No conoce HTTP: la capa api los traduce."""


class ProductoNoEncontrado(DominioError):
    def __init__(self, id: int):
        self.id = id
        super().__init__(f"No product with id {id} exists")


class ProductoDuplicado(DominioError):
    def __init__(self, id: int):
        self.id = id
        super().__init__(f"A product with id {id} already exists")

class LLMError(DominioError):
    """Fallo genérico del proveedor LLM (sin códigos HTTP)."""


class LLMTimeout(LLMError):
    """El proveedor no respondió a tiempo."""


class LLMRateLimit(LLMError):
    """Se alcanzó el límite de peticiones del proveedor."""


class LLMSinClave(LLMError):
    """No hay API key configurada."""