import time

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from swagger_ui_bundle import swagger_ui_path
from typing import List

from models import Producto, ProductoCrear, ProductoActualizar
from database import productos_db
from logging_config import logger
from metrics import metricas

app = FastAPI(
    title="API de Productos",
    description="API REST para administrar productos de una empresa (CRUD), con observabilidad.",
    version="1.1.0",
    docs_url=None,  # se desactiva el /docs por defecto (que usa CDN) para reemplazarlo por uno local
)
app.openapi_version = "3.0.2"  # swagger-ui-bundle local no soporta 3.1.0

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
        content={"detail": "Datos de entrada inválidos o incompletos", "errores": exc.errors()},
    )


@app.exception_handler(Exception)
async def manejador_generico(request: Request, exc: Exception):
    logger.error(f"{request.method} {request.url.path} - Error interno: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Error interno del servidor"},
    )


# ---------------------------------------------------------------------------
# ENDPOINT DE OBSERVABILIDAD: expone las métricas acumuladas
# ---------------------------------------------------------------------------
@app.get("/metricas", tags=["Observabilidad"])
def obtener_metricas():
    """Métricas de comportamiento de la API (para el paso 4/5 de la guía)."""
    return metricas.resumen()


# ---------------------------------------------------------------------------
# ENDPOINTS DE PRODUCTOS
# ---------------------------------------------------------------------------
@app.get("/productos", response_model=List[Producto], tags=["Productos"])
def obtener_productos():
    """Consultar todos los productos registrados."""
    logger.info("GET /productos - Consulta exitosa")
    return list(productos_db.values())


@app.get("/productos/{id}", response_model=Producto, tags=["Productos"])
def obtener_producto(id: int):
    """Consultar un producto por su id.

    NOTA para la Guía 4 (Paso 3, falla controlada #3): usar id=500 simula
    una caída de la conexión con la base de datos.
    """
    if id == 500:
        logger.error(f"GET /productos/{id} - Fallo simulado de conexión con la base de datos")
        raise RuntimeError("Error simulado: no fue posible conectar con la base de datos")

    producto = productos_db.get(id)
    if producto is None:
        logger.error(f"GET /productos/{id} - Producto no encontrado")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe un producto con id {id}",
        )
    logger.info(f"GET /productos/{id} - Consulta exitosa")
    return producto


@app.post("/productos", response_model=Producto, status_code=status.HTTP_201_CREATED, tags=["Productos"])
def crear_producto(producto: ProductoCrear):
    """Registrar un nuevo producto. El id debe ser único."""
    if producto.id in productos_db:
        logger.error(f"POST /productos - Ya existe un producto con id {producto.id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un producto con id {producto.id}",
        )
    nuevo_producto = Producto(**producto.model_dump())
    productos_db[producto.id] = nuevo_producto
    logger.info(f"POST /productos - Producto {producto.id} registrado")
    return nuevo_producto


@app.put("/productos/{id}", response_model=Producto, tags=["Productos"])
def actualizar_producto(id: int, datos: ProductoActualizar):
    """Actualizar un producto existente."""
    if id not in productos_db:
        logger.error(f"PUT /productos/{id} - Producto no encontrado")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe un producto con id {id}",
        )
    producto_actualizado = Producto(id=id, **datos.model_dump())
    productos_db[id] = producto_actualizado
    logger.info(f"PUT /productos/{id} - Producto actualizado")
    return producto_actualizado


@app.delete("/productos/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Productos"])
def eliminar_producto(id: int):
    """Eliminar un producto existente."""
    if id not in productos_db:
        logger.error(f"DELETE /productos/{id} - Producto no encontrado")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe un producto con id {id}",
        )
    del productos_db[id]
    logger.info(f"DELETE /productos/{id} - Producto eliminado")