from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from domain.exceptions import FuenteDatosNoDisponible
from observability.logging_config import logger


def registrar_manejadores_datos(app: FastAPI) -> None:
    """Traduce el error de dominio 'fuente de datos no disponible' a HTTP 503."""

    @app.exception_handler(FuenteDatosNoDisponible)
    async def manejador_fuente_no_disponible(request: Request, exc: FuenteDatosNoDisponible):
        fuente = getattr(exc, "fuente", "unknown")
        logger.error(f"{request.method} {request.url.path} - Fuente de datos no disponible: {fuente}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": f"Data source '{fuente}' is currently unavailable"},
        )