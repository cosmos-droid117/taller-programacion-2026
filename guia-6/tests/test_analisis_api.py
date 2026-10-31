import pytest
from fastapi.testclient import TestClient

from api.dependencies import get_analisis_services
from domain.exceptions import FuenteDatosNoDisponible
from main import app

client = TestClient(app)

RESULTADO_SECOP = {
    "fuente": "SECOP II",
    "total_registros": 3,
    "metrica": "precio_base",
    "estadisticas": {"n": 3, "promedio": 20.0, "mediana": 20.0, "desviacion": 10.0, "minimo": 10, "maximo": 30},
    "grupos": [
        {"grupo": "Antioquia", "n": 2, "promedio": 15.0},
        {"grupo": "Bogotá <b>x</b>", "n": 1, "promedio": 30.0},
    ],
}
RESULTADO_DANE = {
    "fuente": "DIVIPOLA (DANE)",
    "total_registros": 4,
    "metrica": "registros por dpto",
    "estadisticas": {"n": 2, "promedio": 2.0, "mediana": 2.0, "desviacion": 0.0, "minimo": 2, "maximo": 2},
    "grupos": [{"grupo": "ANTIOQUIA", "n": 2}, {"grupo": "BOYACÁ", "n": 2}],
}


class ServicioFalso:
    def __init__(self, resultado=None, error=None):
        self._resultado, self._error = resultado, error

    def analizar(self, limite=None):
        if self._error:
            raise self._error
        return self._resultado


@pytest.fixture(autouse=True)
def limpiar():
    yield
    app.dependency_overrides.clear()


def _inyectar(secop, dane):
    app.dependency_overrides[get_analisis_services] = lambda: {"secop": secop, "dane": dane}


def test_analisis_devuelve_el_resultado_del_servicio():
    _inyectar(ServicioFalso(RESULTADO_SECOP), ServicioFalso(RESULTADO_DANE))
    r = client.get("/analisis/secop")
    assert r.status_code == 200
    assert r.json() == RESULTADO_SECOP
    assert client.get("/analisis/dane").json()["fuente"] == "DIVIPOLA (DANE)"


def test_fuente_desconocida_da_422():
    _inyectar(ServicioFalso(RESULTADO_SECOP), ServicioFalso(RESULTADO_DANE))
    assert client.get("/analisis/otra").status_code == 422


def test_fuente_caida_da_503():
    _inyectar(ServicioFalso(error=FuenteDatosNoDisponible("SECOP II")), ServicioFalso(RESULTADO_DANE))
    r = client.get("/analisis/secop")
    assert r.status_code == 503
    assert r.json() == {"detail": "Data source 'SECOP II' is currently unavailable"}


def test_dashboard_muestra_los_datos_y_escapa_el_html():
    _inyectar(ServicioFalso(RESULTADO_SECOP), ServicioFalso(RESULTADO_DANE))
    r = client.get("/dashboard")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/html")
    assert "SECOP II" in r.text and "DIVIPOLA (DANE)" in r.text and "Antioquia" in r.text
    assert "<svg" in r.text
    assert "Bogotá &lt;b&gt;x&lt;/b&gt;" in r.text
    assert "<b>x</b>" not in r.text


def test_dashboard_sigue_vivo_si_una_fuente_falla():
    _inyectar(ServicioFalso(error=FuenteDatosNoDisponible("SECOP II")), ServicioFalso(RESULTADO_DANE))
    r = client.get("/dashboard")
    assert r.status_code == 200
    assert "currently unavailable" in r.text
    assert "ANTIOQUIA" in r.text


def test_openapi_documenta_analisis_y_oculta_el_dashboard():
    rutas = app.openapi()["paths"]
    assert "/analisis/{fuente}" in rutas
    assert "/dashboard" not in rutas