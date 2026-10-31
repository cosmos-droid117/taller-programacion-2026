import pytest
from fastapi.testclient import TestClient

from api.dependencies import get_ai_service
from application.ai_service import AIService
from domain.exceptions import LLMRateLimit, LLMSinClave, LLMTimeout
from main import app

client = TestClient(app)


class LLMFalso:
    def __init__(self):
        self.prompt = None

    def generar(self, prompt):
        self.prompt = prompt
        return {
            "respuesta": "Respuesta de prueba",
            "modelo": "modelo-falso",
            "tokens_entrada": 120,
            "tokens_salida": 15,
            "tokens_razonamiento": 0,
            "latencia_ms": 5.0,
        }


class LLMConError:
    def __init__(self, error):
        self.error = error

    def generar(self, prompt):
        raise self.error


class LogFalso:
    def registrar(self, registro):
        pass


def _usar(llm):
    app.dependency_overrides[get_ai_service] = lambda: AIService(
        llm, app.state.producto_service, LogFalso()
    )


@pytest.fixture(autouse=True)
def aislar():
    yield
    app.dependency_overrides.clear()


def test_endpoint_ai_con_rag():
    falso = LLMFalso()
    _usar(falso)
    r = client.post(
        "/api/v1/ai",
        json={"pregunta": "¿Cuánto cuestan 2 laptops?", "tecnica": "few-shot", "usar_rag": True},
    )
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["respuesta"] == "Respuesta de prueba"
    assert cuerpo["productos_contexto"] == [1]
    assert "Laptop" in falso.prompt
    assert "Monitor" not in falso.prompt


@pytest.mark.parametrize("error, codigo", [(LLMTimeout(), 504), (LLMRateLimit(), 429), (LLMSinClave(), 503)])
def test_endpoint_ai_errores_del_proveedor(error, codigo):
    _usar(LLMConError(error))
    r = client.post("/api/v1/ai", json={"pregunta": "¿Hay laptops?"})
    assert r.status_code == codigo


def test_endpoint_ai_validacion():
    assert client.post("/api/v1/ai", json={"pregunta": "a"}).status_code == 422
    assert client.post("/api/v1/ai", json={"pregunta": "¿Hay laptops?", "tecnica": "otra"}).status_code == 422