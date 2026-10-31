from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from domain.exceptions import ProductoDuplicado, ProductoNoEncontrado
from logging_config import logger


def registrar_manejadores_dominio(app: FastAPI) -> None:
    """Traduce las excepciones del dominio a respuestas HTTP (el dominio no conoce HTTP)."""

    @app.exception_handler(ProductoNoEncontrado)
    async def manejador_no_encontrado(request: Request, exc: ProductoNoEncontrado):
        logger.error(f"{request.method} {request.url.path} - Producto no encontrado")
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)})

    @app.exception_handler(ProductoDuplicado)
    async def manejador_duplicado(request: Request, exc: ProductoDuplicado):
        logger.error(f"{request.method} {request.url.path} - Ya existe un producto con id {exc.id}")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)})