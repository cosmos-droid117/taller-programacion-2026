import time

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from swagger_ui_bundle import swagger_ui_path

from database import productos_db
from logging_config import logger
from metrics import metricas
from api.ai_routes import router as ai_router
from api.error_handlers import registrar_manejadores_dominio
from api.llm_error_handlers import registrar_manejadores_llm
from api.productos_routes import router as productos_router
from application.ai_service import AIService
from application.producto_service import ProductoService
from infrastructure.gemini_client import GeminiClient
from infrastructure.jsonl_llamada_log import JsonlLlamadaLog
from infrastructure.memory_producto_repository import MemoriaProductoRepository

DESCRIPTION = """
REST API to manage a product catalog (CRUD) with observability (logs and metrics)
and an AI endpoint that answers questions about the catalog using an LLM.

**Features**

* Product CRUD with consistent HTTP error handling (400, 404, 422, 500).
* `/metricas`: request counts, error rate and average response time.
* `/api/v1/ai`: LLM queries with three prompting techniques (zero-shot, few-shot,
  chain-of-thought) and optional RAG (matching products are added to the prompt).
"""

app = FastAPI(
    title="Products API",
    description=DESCRIPTION,
    version="1.2.0",
    docs_url=None,  # se desactiva el /docs por defecto (que usa CDN) para reemplazarlo por uno local
    openapi_tags=[
        {"name": "Products", "description": "Create, read, update and delete products."},
        {"name": "Observability", "description": "Runtime metrics of the API."},
        {"name": "AI", "description": "Questions about the catalog answered by an LLM."},
    ],
)


def _a_openapi_30(nodo):
    """Pydantic v2 emits JSON Schema 2020-12 keywords. OpenAPI 3.0 needs the boolean form
    of exclusiveMinimum/exclusiveMaximum, so convert them in place."""
    if isinstance(nodo, dict):
        for clave, limite in (("exclusiveMinimum", "minimum"), ("exclusiveMaximum", "maximum")):
            valor = nodo.get(clave)
            if isinstance(valor, (int, float)) and not isinstance(valor, bool):
                nodo[limite] = valor
                nodo[clave] = True
        for valor in nodo.values():
            _a_openapi_30(valor)
    elif isinstance(nodo, list):
        for valor in nodo:
            _a_openapi_30(valor)


def openapi_personalizado():
    # El swagger-ui-bundle local no soporta OpenAPI 3.1, por eso se fija 3.0.2
    if app.openapi_schema:
        return app.openapi_schema
    esquema = get_openapi(
        title=app.title,
        version=app.version,
        openapi_version="3.0.2",
        description=app.description,
        routes=app.routes,
        tags=app.openapi_tags,
    )
    _a_openapi_30(esquema)
    app.openapi_schema = esquema
    return esquema


app.openapi = openapi_personalizado

# Composición: aquí (y solo aquí) se eligen las implementaciones concretas
producto_service = ProductoService(MemoriaProductoRepository(productos_db))
app.state.producto_service = producto_service
app.state.ai_service = AIService(GeminiClient(), producto_service, JsonlLlamadaLog())
registrar_manejadores_dominio(app)
registrar_manejadores_llm(app)
app.include_router(productos_router)
app.include_router(ai_router)


@app.get("/docs", include_in_schema=False)
def docs_local():
    """Documentación interactiva Swagger UI, cargada con archivos locales."""
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Docs",
        swagger_js_url="/swagger-static/swagger-ui-bundle.js",
        swagger_css_url="/swagger-static/swagger-ui.css",
    )


# ---------------------------------------------------------------------------
# OBSERVABILIDAD: middleware que mide tiempo de respuesta y alimenta métricas
# ---------------------------------------------------------------------------
@app.middleware("http")
async def middleware_observabilidad(request: Request, call_next):
    inicio = time.perf_counter()
    endpoint = f"{request.method} {request.url.path}"
    logger.info(f"{endpoint} - Petición recibida")

    try:
        response = await call_next(request)
    except Exception:
        # Cualquier excepción no controlada por los handlers de abajo
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


# ---------------------------------------------------------------------------
# MANEJO DE ERRORES: handlers globales para respuestas y logs consistentes
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# ENDPOINT DE OBSERVABILIDAD: expone las métricas acumuladas
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# ENDPOINTS DE PRODUCTOS
# ---------------------------------------------------------------------------

app.state.producto_service = ProductoService(MemoriaProductoRepository(productos_db))
app.mount("/swagger-static", StaticFiles(directory=swagger_ui_path), name="swagger-static")     
