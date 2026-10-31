from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from observability.logging_config import logger


def registrar_manejadores_globales(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def manejador_validacion(request: Request, exc: RequestValidationError):
        logger.error(
            f"{request.method} {request.url.path} - Error de validación: {exc.errors()}"
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": "Invalid or incomplete input data", "errors": exc.errors()},
        )

    @app.exception_handler(Exception)
    async def manejador_generico(request: Request, exc: Exception):
        logger.error(f"{request.method} {request.url.path} - Error interno: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )