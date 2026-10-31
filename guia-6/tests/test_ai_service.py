from unittest.mock import Mock

import pytest

from application.ai_service import AIService
from application.producto_service import ProductoService
from domain.entities import Producto
from domain.exceptions import LLMTimeout
from domain.ports import LLMPort, LlamadaLogPort


def _servicio(llm, registro):
    productos = Mock(spec=ProductoService)
    productos.listar.return_value = [
        Producto(id=1, nombre="Laptop", categoria="Tecnología", precio=3000000, stock=5),
        Producto(id=2, nombre="Monitor", categoria="Tecnología", precio=900000, stock=3),
    ]
    return AIService(llm, productos, registro)


def test_consultar_registra_y_devuelve_contexto():
    llm = Mock(spec=LLMPort)
    llm.generar.return_value = {"respuesta": "ok", "modelo": "m"}
    registro = Mock(spec=LlamadaLogPort)

    res = _servicio(llm, registro).consultar("¿Cuánto cuesta una laptop?", "zero-shot", True)

    assert res["productos_contexto"] == [1]
    assert res["respuesta"] == "ok"
    registro.registrar.assert_called_once()
    assert "Monitor" not in llm.generar.call_args[0][0]


def test_sin_rag_no_hay_contexto():
    llm = Mock(spec=LLMPort)
    llm.generar.return_value = {"respuesta": "ok"}
    res = _servicio(llm, Mock(spec=LlamadaLogPort)).consultar("hola", "zero-shot", False)
    assert res["productos_contexto"] == []


def test_error_del_llm_se_registra_y_se_propaga():
    llm = Mock(spec=LLMPort)
    llm.generar.side_effect = LLMTimeout()
    registro = Mock(spec=LlamadaLogPort)

    with pytest.raises(LLMTimeout):
        _servicio(llm, registro).consultar("¿Hay laptops?", "cot", True)

    assert registro.registrar.call_args[0][0]["error"] == "LLMTimeout"