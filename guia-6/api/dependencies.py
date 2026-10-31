from fastapi import Request

from application.producto_service import ProductoService


def get_producto_service(request: Request) -> ProductoService:
    """Entrega el servicio que main.py dejó armado en app.state (la capa api no conoce la infraestructura)."""
    return request.app.state.producto_service

def get_ai_service(request: Request):
    return request.app.state.ai_service