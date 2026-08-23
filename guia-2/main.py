from fastapi import FastAPI, HTTPException, status
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
from swagger_ui_bundle import swagger_ui_path
from typing import List

from models import Producto, ProductoCrear, ProductoActualizar
from database import productos_db

app = FastAPI(
    title="API de Productos",
    description="API REST para administrar productos de una empresa (CRUD).",
    version="1.0.0",
    docs_url=None,  # se desactiva el /docs por defecto (que usa CDN) para reemplazarlo por uno local
)
app.openapi_version = "3.0.2"  # swagger-ui-bundle local no soporta 3.1.0, que es lo que genera FastAPI por defecto

# Sirve los archivos de Swagger UI (css/js) de forma local, sin depender de internet ni de un CDN.
app.mount("/swagger-static", StaticFiles(directory=swagger_ui_path), name="swagger-static")


@app.get("/docs", include_in_schema=False)
def docs_local():
    """Documentación interactiva Swagger UI, cargada con archivos locales (funciona sin internet)."""
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Docs",
        swagger_js_url="/swagger-static/swagger-ui-bundle.js",
        swagger_css_url="/swagger-static/swagger-ui.css",
    )


@app.get("/productos", response_model=List[Producto], tags=["Productos"])
def obtener_productos():
    """Consultar todos los productos registrados."""
    return list(productos_db.values())


@app.get("/productos/{id}", response_model=Producto, tags=["Productos"])
def obtener_producto(id: int):
    """Consultar un producto por su id."""
    producto = productos_db.get(id)
    if producto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe un producto con id {id}",
        )
    return producto


@app.post("/productos", response_model=Producto, status_code=status.HTTP_201_CREATED, tags=["Productos"])
def crear_producto(producto: ProductoCrear):
    """Registrar un nuevo producto. El id debe ser único."""
    if producto.id in productos_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un producto con id {producto.id}",
        )
    nuevo_producto = Producto(**producto.model_dump())
    productos_db[producto.id] = nuevo_producto
    return nuevo_producto


@app.put("/productos/{id}", response_model=Producto, tags=["Productos"])
def actualizar_producto(id: int, datos: ProductoActualizar):
    """Actualizar un producto existente."""
    if id not in productos_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe un producto con id {id}",
        )
    producto_actualizado = Producto(id=id, **datos.model_dump())
    productos_db[id] = producto_actualizado
    return producto_actualizado


@app.delete("/productos/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Productos"])
def eliminar_producto(id: int):
    """Eliminar un producto existente."""
    if id not in productos_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe un producto con id {id}",
        )
    del productos_db[id]
    return None