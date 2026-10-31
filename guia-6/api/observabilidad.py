import time

from fastapi import FastAPI, Request

from observability.logging_config import logger
from observability.metrics import metricas


def registrar_observabilidad(app: FastAPI) -> None:
    @app.middleware("http")
    async def middleware_observabilidad(request: Request, call_next):
        inicio = time.perf_counter()
        endpoint = f"{request.method} {request.url.path}"
        logger.info(f"{endpoint} - Petición recibida")

        try:
            response = await call_next(request)
        except Exception:
            # Cualquier excepción no controlada por los handlers globales
            duracion_ms = (time.perf_counter() - inicio) * 1000
            metricas.registrar(endpoint, exitosa=False, duracion_ms=duracion_ms)
            raise

        duracion_ms = (time.perf_counter() - inicio) * 1000
        exitosa = response.status_code < 400
        metricas.registrar(endpoint, exitosa=exitosa, duracion_ms=duracion_ms)

        nivel = "INFO" if exitosa else "ERROR"
        logger.info(
            f"{endpoint} - Finalizada con status {response.status_code} "
            f"({duracion_ms:.2f} ms) [{nivel}]"
        )
        return response

    @app.get(
        "/metricas",
        tags=["Observability"],
        operation_id="get_metrics",
        summary="Get API metrics",
        description=(
            "Returns the metrics accumulated since the server started: total requests, requests per "
            "endpoint, successful and failed operations, error rate and average response time."
        ),
        responses={
            200: {
                "description": "Accumulated metrics",
                "content": {
                    "application/json": {
                        "example": {
                            "total_peticiones": 12,
                            "peticiones_por_endpoint": {"GET /productos": 5, "POST /productos": 3, "GET /productos/999": 4},
                            "operaciones_exitosas": 8,
                            "operaciones_fallidas": 4,
                            "tasa_error_porcentaje": 33.33,
                            "tiempo_respuesta_promedio_ms": 2.41,
                        }
                    }
                },
            }
        },
    )
    def obtener_metricas():
        return metricas.resumen()