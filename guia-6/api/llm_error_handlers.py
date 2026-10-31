from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from domain.exceptions import LLMError, LLMRateLimit, LLMSinClave, LLMTimeout
from logging_config import logger

_MAPA = (
    (LLMTimeout, 504, "The LLM provider did not respond in time"),
    (LLMRateLimit, 429, "LLM rate limit reached, try again later"),
    (LLMSinClave, 503, "LLM API key is not configured"),
)


def registrar_manejadores_llm(app: FastAPI) -> None:
    @app.exception_handler(LLMError)
    async def manejador_llm(request: Request, exc: LLMError):
        codigo, detalle = 502, "The LLM provider returned an error"
        for tipo, c, d in _MAPA:
            if isinstance(exc, tipo):
                codigo, detalle = c, d
                break
        logger.error(f"{request.method} {request.url.path} - {type(exc).__name__}")
        return JSONResponse(status_code=codigo, content={"detail": detalle})