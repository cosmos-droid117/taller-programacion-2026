from typing import List

from fastapi import APIRouter, Body, Depends, status

from api.dependencies import get_producto_service
from api.responses import RESPUESTA_404, RESPUESTA_422, RESPUESTA_500, error
from application.producto_service import ProductoService
from observability.logging_config import logger
from api.schemas import ProductoActualizar, ProductoCrear
from domain.entities import Producto

router = APIRouter()


@router.get(
    "/productos",
    response_model=List[Producto],
    tags=["Products"],
    operation_id="list_products",
    summary="List all products",
    description="Returns every product currently stored in the catalog.",
)
def obtener_productos(servicio: ProductoService = Depends(get_producto_service)):
    productos = servicio.listar()
    logger.info("GET /productos - Consulta exitosa")
    return productos


@router.get(
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
def obtener_producto(id: int, servicio: ProductoService = Depends(get_producto_service)):
    producto = servicio.obtener(id)
    logger.info(f"GET /productos/{id} - Consulta exitosa")
    return producto


@router.post(
    "/productos",
    response_model=Producto,
    status_code=status.HTTP_201_CREATED,
    tags=["Products"],
    operation_id="create_product",
    summary="Create a product",
    description="Registers a new product. The client chooses the `id`, which must not exist yet.",
    responses={
        400: error("A product with that id already exists", "A product with id 1 already exists"),
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
    servicio: ProductoService = Depends(get_producto_service),
):
    nuevo_producto = servicio.crear(Producto(**producto.model_dump()))
    logger.info(f"POST /productos - Producto {producto.id} registrado")
    return nuevo_producto


@router.put(
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
    servicio: ProductoService = Depends(get_producto_service),
):
    producto_actualizado = servicio.actualizar(id, datos)
    logger.info(f"PUT /productos/{id} - Producto actualizado")
    return producto_actualizado


@router.delete(
    "/productos/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Products"],
    operation_id="delete_product",
    summary="Delete a product",
    description="Permanently removes a product. Returns no content when it succeeds.",
    responses=RESPUESTA_404,
)
def eliminar_producto(id: int, servicio: ProductoService = Depends(get_producto_service)):
    servicio.eliminar(id)
    logger.info(f"DELETE /productos/{id} - Producto eliminado")