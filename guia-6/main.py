from fastapi import FastAPI

from api.ai_routes import router as ai_router
from api.docs import registrar_docs
from api.error_handlers import registrar_manejadores_dominio
from api.global_handlers import registrar_manejadores_globales
from api.llm_error_handlers import registrar_manejadores_llm
from api.observabilidad import registrar_observabilidad
from api.productos_routes import router as productos_router
from application.ai_service import AIService
from application.producto_service import ProductoService
from domain.entities import Producto
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
    docs_url=None,  # se reemplaza por un /docs local (api/docs.py)
    openapi_tags=[
        {"name": "Products", "description": "Create, read, update and delete products."},
        {"name": "Observability", "description": "Runtime metrics of the API."},
        {"name": "AI", "description": "Questions about the catalog answered by an LLM."},
    ],
)

# "Base de datos" en memoria (semilla): se reinicia cada vez que se reinicia el servidor.
productos_db = {
    1: Producto(id=1, nombre="Laptop", categoria="Tecnología", precio=2500000, stock=10),
    2: Producto(id=2, nombre="Mouse inalámbrico", categoria="Tecnología", precio=45000, stock=50),
    3: Producto(id=3, nombre="Teclado", categoria="Tecnología", precio=90000, stock=30),
    4: Producto(id=4, nombre="Monitor", categoria="Tecnología", precio=780000, stock=12),
    5: Producto(id=5, nombre="Audífonos", categoria="Audio", precio=120000, stock=25),
}

# Composición: aquí (y solo aquí) se eligen las implementaciones concretas
producto_service = ProductoService(MemoriaProductoRepository(productos_db))
app.state.producto_service = producto_service
app.state.ai_service = AIService(GeminiClient(), producto_service, JsonlLlamadaLog())

registrar_docs(app)
registrar_observabilidad(app)
registrar_manejadores_globales(app)
registrar_manejadores_dominio(app)
registrar_manejadores_llm(app)
app.include_router(productos_router)
app.include_router(ai_router)