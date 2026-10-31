import pytest

from infrastructure.resilience import CircuitBreaker, CircuitOpenError, Estado, con_reintentos


class Reloj:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


def _falla():
    raise ValueError("fallo")


def _breaker(reloj=None):
    return CircuitBreaker("test", max_fallos=3, enfriamiento=30.0, reloj=reloj or Reloj())


def _abrir(b):
    for _ in range(3):
        with pytest.raises(ValueError):
            b.call(_falla)


def test_abre_tras_max_fallos():
    b = _breaker()
    assert b.estado is Estado.CLOSED
    _abrir(b)
    assert b.estado is Estado.OPEN


def test_abierto_rechaza_sin_llamar():
    b = _breaker()
    _abrir(b)
    llamadas = []
    with pytest.raises(CircuitOpenError):
        b.call(lambda: llamadas.append(1))
    assert llamadas == []


def test_half_open_y_cierra_si_tiene_exito():
    reloj = Reloj()
    b = _breaker(reloj)
    _abrir(b)
    reloj.t = 31
    assert b.call(lambda: "ok") == "ok"
    assert b.estado is Estado.CLOSED


def test_half_open_reabre_si_falla():
    reloj = Reloj()
    b = _breaker(reloj)
    _abrir(b)
    reloj.t = 31
    with pytest.raises(ValueError):
        b.call(_falla)
    assert b.estado is Estado.OPEN
    with pytest.raises(CircuitOpenError):
        b.call(lambda: "ok")


def test_exito_reinicia_contador_de_fallos():
    b = _breaker()
    for _ in range(2):
        with pytest.raises(ValueError):
            b.call(_falla)
    b.call(lambda: "ok")
    for _ in range(2):
        with pytest.raises(ValueError):
            b.call(_falla)
    assert b.estado is Estado.CLOSED


def test_backoff_exponencial_y_exito_al_tercer_intento():
    esperas, intentos = [], []

    def fn():
        intentos.append(1)
        if len(intentos) < 3:
            raise ValueError("fallo")
        return "ok"

    assert con_reintentos(fn, intentos=3, base=0.5, dormir=esperas.append) == "ok"
    assert esperas == [0.5, 1.0]


def test_agota_reintentos_y_relanza():
    esperas = []
    with pytest.raises(ValueError):
        con_reintentos(_falla, intentos=3, base=0.5, dormir=esperas.append)
    assert esperas == [0.5, 1.0]


def test_no_reintenta_si_el_circuito_esta_abierto():
    esperas = []

    def abierto():
        raise CircuitOpenError("abierto")

    with pytest.raises(CircuitOpenError):
        con_reintentos(abierto, dormir=esperas.append)
    assert esperas == []