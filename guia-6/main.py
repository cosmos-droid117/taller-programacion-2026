import time

from fastapi import Body, Depends, FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from swagger_ui_bundle import swagger_ui_path
from typing import List

from models import (
    AIConsulta,
    AIRespuesta,
    ErrorResponse,
    Producto,
    ProductoActualizar,
    ProductoCrear,
    ValidationErrorResponse,
)
from database import productos_db
from logging_config import logger
from metrics import metricas
from llm_client import GeminiClient, LLMError, registrar_llamada
from rag import construir_prompt, recuperar_productos

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

app.mount("/swagger-static", StaticFiles(directory=swagger_ui_path), name="swagger-static")


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
# DOCUMENTACIÓN OPENAPI: respuestas de error reutilizables
# ---------------------------------------------------------------------------
def _error(descripcion: str, ejemplo: str) -> dict:
    return {
        "model": ErrorResponse,
        "description": descripcion,
        "content": {"application/json": {"example": {"detail": ejemplo}}},
    }


RESPUESTA_404 = {404: _error("Product not found", "No product with id 999 exists")}
RESPUESTA_422 = {
    422: {
        "model": ValidationErrorResponse,
        "description": "Invalid or incomplete input data",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Invalid or incomplete input data",
                    "errors": [
                        {
                            "type": "greater_than",
                            "loc": ["body", "precio"],
                            "msg": "Input should be greater than 0",
                            "input": -5,
                            "ctx": {"gt": 0.0},
                        }
                    ],
                }
            }
        },
    }
}
RESPUESTA_500 = {500: _error("Unexpected server error", "Internal server error")}


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
@app.get(
    "/productos",
    response_model=List[Producto],
    tags=["Products"],
    operation_id="list_products",
    summary="List all products",
    description="Returns every product currently stored in the catalog.",
)
def obtener_productos():
    logger.info("GET /productos - Consulta exitosa")
    return list(productos_db.values())


@app.get(
    "/productos/{id}",
    response_model=Producto,
    tags=["Products"],
    operation_id="get_product",
    summary="Get a product by id",
    description=(
        "Returns a single product. Product id `500` is reserved: it simulates a database "
        "connection failure and always answers with HTTP 500 (used for the controlled-failure tests)."
    ),
    responses={**RESPUESTA_404, **RESPUESTA_500},
)
def obtener_producto(id: int):
    if id == 500:
        logger.error(f"GET /productos/{id} - Fallo simulado de conexión con la base de datos")
        raise RuntimeError("Error simulado: no fue posible conectar con la base de datos")

    producto = productos_db.get(id)
    if producto is None:
        logger.error(f"GET /productos/{id} - Producto no encontrado")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No product with id {id} exists",
        )
    logger.info(f"GET /productos/{id} - Consulta exitosa")
    return producto


@app.post(
    "/productos",
    response_model=Producto,
    status_code=status.HTTP_201_CREATED,
    tags=["Products"],
    operation_id="create_product",
    summary="Create a product",
    description="Registers a new product. The client chooses the `id`, which must not exist yet.",
    responses={
        400: _error("A product with that id already exists", "A product with id 1 already exists"),
        **RESPUESTA_422,
    },
)
def crear_producto(
    producto: ProductoCrear = Body(
        ...,
        openapi_examples={
            "valid": {
                "summary": "Valid product",
                "description": "Creates a new product (returns 201).",
                "value": {"id": 10, "nombre": "Teclado mecánico", "categoria": "Tecnología", "precio": 120000, "stock": 8},
            },
            "duplicate_id": {
                "summary": "Duplicate id",
                "description": "The id 1 already exists in the seed data (returns 400).",
                "value": {"id": 1, "nombre": "Otro producto", "categoria": "Tecnología", "precio": 1000, "stock": 1},
            },
            "invalid_price": {
                "summary": "Invalid price",
                "description": "The price must be greater than 0 (returns 422).",
                "value": {"id": 11, "nombre": "Cable", "categoria": "Accesorios", "precio": -5, "stock": 3},
            },
        },
    ),
):
    if producto.id in productos_db:
        logger.error(f"POST /productos - Ya existe un producto con id {producto.id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A product with id {producto.id} already exists",
        )
    nuevo_producto = Producto(**producto.model_dump())
    productos_db[producto.id] = nuevo_producto
    logger.info(f"POST /productos - Producto {producto.id} registrado")
    return nuevo_producto


@app.put(
    "/productos/{id}",
    response_model=Producto,
    tags=["Products"],
    operation_id="update_product",
    summary="Update a product",
    description="Replaces all the fields of an existing product. The `id` is taken from the URL and cannot be changed.",
    responses={**RESPUESTA_404, **RESPUESTA_422},
)
def actualizar_producto(
    id: int,
    datos: ProductoActualizar = Body(
        ...,
        openapi_examples={
            "price_change": {
                "summary": "Change price and stock",
                "value": {"nombre": "Laptop", "categoria": "Tecnología", "precio": 2300000, "stock": 7},
            }
        },
    ),
):
    if id not in productos_db:
        logger.error(f"PUT /productos/{id} - Producto no encontrado")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No product with id {id} exists",
        )
    producto_actualizado = Producto(id=id, **datos.model_dump())
    productos_db[id] = producto_actualizado
    logger.info(f"PUT /productos/{id} - Producto actualizado")
    return producto_actualizado


@app.delete(
    "/productos/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Products"],
    operation_id="delete_product",
    summary="Delete a product",
    description="Permanently removes a product. Returns no content when it succeeds.",
    responses=RESPUESTA_404,
)
def eliminar_producto(id: int):
    if id not in productos_db:
        logger.error(f"DELETE /productos/{id} - Producto no encontrado")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No product with id {id} exists",
        )
    del productos_db[id]
    logger.info(f"DELETE /productos/{id} - Producto eliminado")


# ---------------------------------------------------------------------------
# ENDPOINT DE IA: consulta un LLM con contexto recuperado (RAG)
# ---------------------------------------------------------------------------
def get_llm_client() -> GeminiClient:
    return GeminiClient()


@app.post(
    "/api/v1/ai",
    response_model=AIRespuesta,
    tags=["AI"],
    operation_id="ask_ai",
    summary="Ask the LLM about the product catalog",
    description=(
        "Builds a prompt with the chosen technique (`zero-shot`, `few-shot` or `cot`), optionally adds the "
        "catalog products that match the question as context (RAG) and queries the LLM. If no product "
        "matches, the whole catalog is sent. Every call is logged to `llamadas_llm.jsonl`."
    ),
    responses={
        429: _error("LLM rate limit reached", "LLM rate limit reached, try again later"),
        502: _error("The LLM provider returned an error", "The LLM provider returned an error"),
        503: _error("The LLM API key is not configured", "LLM API key is not configured"),
        504: _error("The LLM provider did not respond in time", "The LLM provider did not respond in time"),
        **RESPUESTA_422,
    },
)
def consultar_ai(
    consulta: AIConsulta = Body(
        ...,
        openapi_examples={
            "cot_with_rag": {
                "summary": "Chain-of-thought with RAG",
                "value": {"pregunta": "¿Cuánto cuestan en total 2 laptops y 3 mouse?", "tecnica": "cot", "usar_rag": True},
            },
            "few_shot": {
                "summary": "Few-shot with RAG",
                "value": {"pregunta": "¿Venden tablets?", "tecnica": "few-shot", "usar_rag": True},
            },
            "zero_shot_no_rag": {
                "summary": "Zero-shot without RAG (baseline)",
                "value": {"pregunta": "¿Cuál es el producto más barato?", "tecnica": "zero-shot", "usar_rag": False},
            },
        },
    ),
    llm: GeminiClient = Depends(get_llm_client),
):
    contexto = recuperar_productos(consulta.pregunta, list(productos_db.values())) if consulta.usar_rag else []
    prompt = construir_prompt(consulta.tecnica, consulta.pregunta, contexto)
    base = {"pregunta": consulta.pregunta, "tecnica": consulta.tecnica, "usar_rag": consulta.usar_rag, "prompt": prompt}
    try:
        resultado = llm.generar(prompt)
    except LLMError as exc:
        registrar_llamada({**base, "error": type(exc).__name__})
        logger.error(f"POST /api/v1/ai - {type(exc).__name__}")
        raise HTTPException(status_code=exc.status_code, detail=exc.detalle)
    registrar_llamada({**base, **resultado})
    logger.info(f"POST /api/v1/ai - OK ({consulta.tecnica}, rag={consulta.usar_rag})")
    return AIRespuesta(
        tecnica=consulta.tecnica,
        usar_rag=consulta.usar_rag,
        productos_contexto=[p.id for p in contexto],
        **resultado,
    )
