import time
from enum import Enum
from typing import Callable, TypeVar

from observability.logging_config import logger

T = TypeVar("T")


class Estado(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitOpenError(Exception):
    """El circuito está abierto: la llamada se rechaza sin tocar la API externa."""


class CircuitBreaker:
    """Circuit breaker de 3 estados: CLOSED -> OPEN -> HALF_OPEN -> CLOSED."""

    def __init__(self, nombre: str = "api", max_fallos: int = 3, enfriamiento: float = 30.0, reloj=time.monotonic):
        self.nombre = nombre
        self.max_fallos = max_fallos
        self.enfriamiento = enfriamiento
        self._reloj = reloj
        self._fallos = 0
        self._abierto_en = None
        self.estado = Estado.CLOSED

    def _cambiar(self, nuevo: Estado) -> None:
        if nuevo is not self.estado:
            logger.info(
                f"[CircuitBreaker:{self.nombre}] {self.estado.value.upper()} -> {nuevo.value.upper()}"
            )
            self.estado = nuevo

    def call(self, fn: Callable[..., T], *args, **kwargs) -> T:
        if self.estado is Estado.OPEN:
            if self._reloj() - self._abierto_en >= self.enfriamiento:
                self._cambiar(Estado.HALF_OPEN)
            else:
                raise CircuitOpenError(f"Circuito abierto para {self.nombre}")
        try:
            resultado = fn(*args, **kwargs)
        except Exception:
            self._fallos += 1
            if self.estado is Estado.HALF_OPEN or self._fallos >= self.max_fallos:
                self._abierto_en = self._reloj()
                self._cambiar(Estado.OPEN)
            raise
        self._fallos = 0
        self._cambiar(Estado.CLOSED)
        return resultado


def con_reintentos(fn: Callable[[], T], intentos: int = 3, base: float = 0.5,
                   dormir=time.sleep, nombre: str = "api") -> T:
    """Reintenta con backoff exponencial: espera base*2^n (0.5 s, 1 s, 2 s...)."""
    for n in range(intentos):
        try:
            return fn()
        except CircuitOpenError:
            raise
        except Exception as exc:
            if n == intentos - 1:
                logger.error(f"[Retry:{nombre}] intento {n + 1}/{intentos} falló ({type(exc).__name__}); sin más reintentos")
                raise
            espera = base * (2 ** n)
            logger.warning(
                f"[Retry:{nombre}] intento {n + 1}/{intentos} falló ({type(exc).__name__}); reintentando en {espera} s"
            )
            dormir(espera)