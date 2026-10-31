import logging
import sys


def configurar_logging() -> logging.Logger:
    """Configura un logger que escribe tanto en consola como en un archivo app.log.

    Formato de salida (igual al pedido por la guía):
    2026-09-11 10:15:32 INFO GET /productos - Consulta exitosa
    """
    logger = logging.getLogger("api_productos")
    logger.setLevel(logging.INFO)

    formato = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Evita duplicar handlers si uvicorn recarga el módulo (--reload)
    if not logger.handlers:
        handler_consola = logging.StreamHandler(sys.stdout)
        handler_consola.setFormatter(formato)

        handler_archivo = logging.FileHandler("app.log", encoding="utf-8")
        handler_archivo.setFormatter(formato)

        logger.addHandler(handler_consola)
        logger.addHandler(handler_archivo)

    return logger


logger = configurar_logging()