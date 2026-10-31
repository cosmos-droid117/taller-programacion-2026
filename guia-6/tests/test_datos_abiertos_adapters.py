import pytest
import requests

from domain.exceptions import FuenteDatosNoDisponible
from infrastructure.datos_abiertos_adapters import DaneAdapter, DatosGovCoAdapter
from infrastructure.resilience import CircuitBreaker, Estado


class Resp:
    def __init__(self, datos=None, error=None):
        self._datos, self._error = datos, error

    def raise_for_status(self):
        if self._error:
            raise self._error

    def json(self):
        return self._datos


class HttpFalso:
    """Devuelve las respuestas en orden; si una es excepción, la lanza."""

    def __init__(self, *respuestas):
        self.respuestas = list(respuestas)
        self.llamadas = []

    def __call__(self, url, params=None, timeout=None):
        self.llamadas.append((url, params, timeout))
        r = self.respuestas.pop(0)
        if isinstance(r, Exception):
            raise r
        return r


def _adaptador(http, esperas=None):
    breaker = CircuitBreaker("t", max_fallos=3, enfriamiento=30.0)
    dormir = esperas.append if esperas is not None else (lambda s: None)
    return DatosGovCoAdapter(breaker, http_get=http, dormir=dormir), breaker


def test_devuelve_registros_y_arma_la_peticion():
    http = HttpFalso(Resp([{"precio_base": "10"}]))
    adaptador, _ = _adaptador(http)
    assert adaptador.obtener_registros(5) == [{"precio_base": "10"}]
    url, params, _ = http.llamadas[0]
    assert url == "https://www.datos.gov.co/resource/p6dx-8zbt.json"
    assert params == {"$limit": 5, "$order": "fecha_de_publicacion_del DESC"}


def test_dane_usa_su_dataset_sin_orden():
    http = HttpFalso(Resp([]))
    DaneAdapter(CircuitBreaker("d"), http_get=http).obtener_registros()
    url, params, _ = http.llamadas[0]
    assert url.endswith("/gdxc-w37w.json")
    assert params == {"$limit": 2000}


def test_se_recupera_con_reintentos_y_backoff():
    esperas = []
    http = HttpFalso(requests.ConnectionError(), requests.Timeout(), Resp([{"a": 1}]))
    adaptador, breaker = _adaptador(http, esperas)
    assert adaptador.obtener_registros() == [{"a": 1}]
    assert esperas == [0.5, 1.0]
    assert breaker.estado is Estado.CLOSED


def test_error_http_agota_reintentos_y_abre_el_circuito():
    err = requests.HTTPError("500")
    http = HttpFalso(Resp(error=err), Resp(error=err), Resp(error=err))
    adaptador, breaker = _adaptador(http)
    with pytest.raises(FuenteDatosNoDisponible):
        adaptador.obtener_registros()
    assert breaker.estado is Estado.OPEN
    # con el circuito abierto ya no se llama a la API
    with pytest.raises(FuenteDatosNoDisponible):
        adaptador.obtener_registros()
    assert len(http.llamadas) == 3


def test_respuesta_que_no_es_lista_cuenta_como_fallo():
    http = HttpFalso(*[Resp({"error": True})] * 3)
    adaptador, _ = _adaptador(http)
    with pytest.raises(FuenteDatosNoDisponible):
        adaptador.obtener_registros()


def test_cada_api_tiene_su_propio_circuito():
    err = requests.ConnectionError()
    secop, b_secop = _adaptador(HttpFalso(err, err, err))
    with pytest.raises(FuenteDatosNoDisponible):
        secop.obtener_registros()
    b_dane = CircuitBreaker("dane")
    dane = DaneAdapter(b_dane, http_get=HttpFalso(Resp([{"dpto": "X"}])))
    assert dane.obtener_registros() == [{"dpto": "X"}]
    assert b_secop.estado is Estado.OPEN
    assert b_dane.estado is Estado.CLOSED