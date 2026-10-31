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