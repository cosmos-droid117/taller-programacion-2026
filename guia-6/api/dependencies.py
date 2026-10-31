from typing import Dict

from fastapi import Request

from application.analisis_service import AnalisisService
from application.producto_service import ProductoService

def get_producto_service(request: Request) -> ProductoService:
    """Entrega el servicio que main.py dejó armado en app.state (la capa api no conoce la infraestructura)."""
    return request.app.state.producto_service

def get_ai_service(request: Request):
    return request.app.state.ai_service


def get_analisis_services(request: Request) -> Dict[str, AnalisisService]:
    return request.app.state.analisis_services